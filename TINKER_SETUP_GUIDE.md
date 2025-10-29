# EpiBrief-MMWR-LM: Tinker API Setup & Training Guide

## Step-by-Step Instructions for Fine-Tuning with Tinker

---

## PHASE 1: SETUP & AUTHENTICATION

### Step 1: Access Your API Key
Since you already received access from Thinking Machines:

1. **Go to Tinker Console:** https://tinker-console.thinkingmachines.ai
2. **Log in** with your credentials (from the email)
3. **Generate API Key:**
   - Look for "API Keys" section in the console
   - Click "Generate New Key"
   - **COPY THE KEY** - you'll only see it once!
   - Save it somewhere secure

### Step 2: Set Up API Key on Your Machine

**Option A: Environment Variable (Recommended)**
```bash
# Windows PowerShell
$env:TINKER_API_KEY = "your-api-key-here"

# Or add permanently:
[System.Environment]::SetEnvironmentVariable('TINKER_API_KEY', 'your-api-key-here', 'User')
```

**Option B: In Code (Less Secure)**
```python
import os
os.environ['TINKER_API_KEY'] = 'your-api-key-here'
```

### Step 3: Install Tinker SDK

```bash
# Install the main Tinker package
pip install tinker

# Optional: Clone the cookbook for examples
git clone https://github.com/thinking-machines-lab/tinker-cookbook.git
cd tinker-cookbook
pip install -e .
```

---

## PHASE 2: PREPARE YOUR TRAINING DATA

### Step 4: Verify Your Training Pairs
Your data is already ready at:
```
training_data/training_pairs.jsonl
```

**Current Stats:**
- ✅ 11,632 training pairs
- ✅ JSONL format (perfect for Tinker)
- ✅ 6 pair types (executive_summary, data_interpretation, etc.)

### Step 5: Create Train/Validation Split

```python
# Create this script: scripts/4_split_dataset.py

import json
import random
from pathlib import Path

# Load training pairs
pairs = []
with open('../training_data/training_pairs.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        pairs.append(json.loads(line))

print(f"Total pairs: {len(pairs)}")

# Shuffle
random.seed(42)
random.shuffle(pairs)

# 90% train, 10% validation
split_idx = int(0.9 * len(pairs))
train_pairs = pairs[:split_idx]
val_pairs = pairs[split_idx:]

print(f"Train: {len(train_pairs)}")
print(f"Val: {len(val_pairs)}")

# Save splits
with open('../training_data/train.jsonl', 'w', encoding='utf-8') as f:
    for pair in train_pairs:
        f.write(json.dumps(pair) + '\n')

with open('../training_data/val.jsonl', 'w', encoding='utf-8') as f:
    for pair in val_pairs:
        f.write(json.dumps(pair) + '\n')

print("✓ Dataset split complete!")
```

**Run it:**
```bash
cd scripts
python 4_split_dataset.py
```

---

## PHASE 3: CREATE TRAINING SCRIPT

### Step 6: Create Your Tinker Training Script

```python
# Create this file: scripts/5_train_with_tinker.py

"""
EpiBrief-MMWR-LM Training Script using Tinker API
Fine-tune Llama 3.1 8B on MMWR epidemiological reasoning
"""

import json
import os
from pathlib import Path
from typing import List, Dict
import tinker
from tinker import Tinker

# Configuration
MODEL = "Llama-3.1-8B"  # Or "Qwen3-8B" for comparison
TRAIN_DATA = Path("../training_data/train.jsonl")
VAL_DATA = Path("../training_data/val.jsonl")
BATCH_SIZE = 4
LEARNING_RATE = 2e-5
NUM_EPOCHS = 3
SAVE_DIR = Path("../models/epibrief-mmwr-lm-v1")

# Ensure API key is set
if 'TINKER_API_KEY' not in os.environ:
    raise ValueError("TINKER_API_KEY environment variable not set!")

print("="*70)
print("   EpiBrief-MMWR-LM Training with Tinker API")
print("   Model: " + MODEL)
print("="*70 + "\n")


class EpiBriefDataLoader:
    """Load and batch training pairs for supervised fine-tuning."""

    def __init__(self, data_path: Path, batch_size: int = 4):
        self.data_path = data_path
        self.batch_size = batch_size
        self.data = self._load_data()

    def _load_data(self) -> List[Dict]:
        """Load JSONL training pairs."""
        data = []
        with open(self.data_path, 'r', encoding='utf-8') as f:
            for line in f:
                pair = json.loads(line)
                data.append(pair)
        return data

    def __len__(self):
        return len(self.data)

    def get_batches(self):
        """Yield batches of training pairs."""
        for i in range(0, len(self.data), self.batch_size):
            batch = self.data[i:i + self.batch_size]
            yield batch


def format_training_example(pair: Dict) -> Dict[str, str]:
    """
    Format training pair into instruction-response format.

    This is critical - we're teaching the model to:
    1. Follow CDC-style instructions
    2. Generate epidemiologically-sound responses
    3. Interpret quantitative data
    """
    instruction = pair['instruction']
    response = pair['response']

    # Format as conversation (Llama 3.1 chat format)
    prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{instruction}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    completion = f"{response}<|eot_id|>"

    return {
        "prompt": prompt,
        "completion": completion,
        "full_text": prompt + completion
    }


def main():
    print("Loading training data...")
    train_loader = EpiBriefDataLoader(TRAIN_DATA, BATCH_SIZE)
    val_loader = EpiBriefDataLoader(VAL_DATA, BATCH_SIZE)

    print(f"Train batches: {len(train_loader) // BATCH_SIZE}")
    print(f"Val batches: {len(val_loader) // BATCH_SIZE}\n")

    print("Initializing Tinker API...")
    # Initialize Tinker with your model choice
    session = Tinker(
        model=MODEL,
        learning_rate=LEARNING_RATE,
        # LoRA parameters (Tinker handles this)
        # They use sensible defaults for LoRA
    )

    print(f"✓ Connected to Tinker")
    print(f"✓ Model: {MODEL}")
    print(f"✓ Starting training...\n")

    # Training loop
    for epoch in range(NUM_EPOCHS):
        print(f"\n{'='*70}")
        print(f"EPOCH {epoch + 1}/{NUM_EPOCHS}")
        print('='*70)

        total_loss = 0
        num_batches = 0

        for batch_idx, batch in enumerate(train_loader.get_batches()):
            # Format batch
            formatted_examples = [format_training_example(pair) for pair in batch]

            # Prepare inputs for Tinker
            texts = [ex['full_text'] for ex in formatted_examples]

            # Tinker's forward_backward computes gradients
            # You provide the texts and it handles tokenization and loss computation
            loss = session.forward_backward(
                texts=texts,
                # Tinker handles supervised learning loss internally
            )

            total_loss += loss
            num_batches += 1

            # Progress update
            if batch_idx % 10 == 0:
                avg_loss = total_loss / num_batches
                print(f"Batch {batch_idx}: loss={loss:.4f}, avg_loss={avg_loss:.4f}")

            # Optimizer step (update weights)
            if (batch_idx + 1) % 1 == 0:  # Gradient accumulation steps
                session.optim_step()

        # Epoch summary
        avg_epoch_loss = total_loss / num_batches
        print(f"\nEpoch {epoch + 1} complete: avg_loss={avg_epoch_loss:.4f}")

        # Validation (optional - sample some outputs)
        print("\nValidation sampling...")
        val_batch = next(val_loader.get_batches())
        sample_pair = val_batch[0]

        # Generate sample output
        sample_prompt = format_training_example(sample_pair)['prompt']
        generated = session.sample(
            prompt=sample_prompt,
            max_tokens=256,
            temperature=0.7
        )

        print("\nSample Generation:")
        print(f"Instruction: {sample_pair['instruction'][:100]}...")
        print(f"Generated: {generated[:200]}...")
        print(f"Expected: {sample_pair['response'][:200]}...")

    # Save trained model
    print(f"\n{'='*70}")
    print("Training complete! Saving model...")

    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    session.save_state(str(SAVE_DIR / "checkpoint"))

    print(f"✓ Model saved to: {SAVE_DIR}")
    print(f"✓ You can now download weights from Tinker console")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
```

---

## PHASE 4: TRAIN YOUR MODEL

### Step 7: Run Training

```bash
cd scripts
python 5_train_with_tinker.py
```

**Expected Output:**
```
======================================================================
   EpiBrief-MMWR-LM Training with Tinker API
   Model: Llama-3.1-8B
======================================================================

Loading training data...
Train batches: 2615
Val batches: 291

Initializing Tinker API...
✓ Connected to Tinker
✓ Model: Llama-3.1-8B
✓ Starting training...

======================================================================
EPOCH 1/3
======================================================================
Batch 0: loss=2.4531, avg_loss=2.4531
Batch 10: loss=1.9234, avg_loss=2.1245
...
```

### Step 8: Monitor Training

**Tinker Console:**
- Go to https://tinker-console.thinkingmachines.ai
- View real-time training metrics
- Monitor GPU usage
- Check for any errors

**What to Watch:**
- Loss should decrease over epochs
- Validation samples should improve
- Training should complete in hours (not days)

---

## PHASE 5: DOWNLOAD & USE YOUR MODEL

### Step 9: Download Trained Weights

**Option A: From Console**
1. Go to Tinker Console
2. Find your training run
3. Click "Download Weights"
4. Save to `models/epibrief-mmwr-lm-v1/`

**Option B: Via API**
```python
# In your training script, after training:
session.download_weights("./models/epibrief-mmwr-lm-v1/model.safetensors")
```

### Step 10: Test Your Fine-Tuned Model

```python
# Create: scripts/6_test_model.py

from tinker import Tinker

# Load your trained model
session = Tinker.load_state("../models/epibrief-mmwr-lm-v1/checkpoint")

# Test prompt
test_instruction = """
Based on this MMWR article, generate an executive summary following CDC format.
Article: Measles Outbreak in Urban Community — United States, 2024
"""

prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{test_instruction}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"

# Generate
output = session.sample(
    prompt=prompt,
    max_tokens=512,
    temperature=0.7
)

print("Generated EpiBrief:")
print(output)
```

---

## PHASE 6: EVALUATION

### Step 11: Evaluate Model Quality

**Test on Real MMWR Articles:**
1. Pick 5-10 recent MMWR articles (not in training set)
2. Generate executive summaries
3. Compare to actual CDC summaries
4. Score on:
   - Factual accuracy
   - CDC-style language
   - Quantitative interpretation
   - Public health framing

**Evaluation Metrics:**
- ROUGE score vs. gold CDC summaries
- Human evaluation (you or domain expert)
- Quantitative reasoning accuracy

---

## MODEL RECOMMENDATIONS

Based on Tinker's available models:

### For Your Use Case:

**Best Choice: Llama-3.1-8B**
- ✅ Good balance of size and quality
- ✅ Well-documented, widely used
- ✅ 8B parameters = efficient training
- ✅ Strong instruction-following

**Alternative: Qwen3-8B**
- ✅ Similar size to Llama 3.1 8B
- ✅ May be faster/cheaper
- ✅ Good for comparison

**If You Want More Power: Llama-3.1-70B**
- Higher quality potential
- More expensive to train
- Try 8B first, upgrade if needed

**Cost-Efficient Option: Qwen3-30B-A3B (MoE)**
- Only 3B active parameters
- Cheaper than dense 30B
- Worth testing!

---

## COST ESTIMATION

**Training Time:**
- ~11K training pairs × 3 epochs = ~33K forward passes
- Batch size 4 = ~8,250 batches
- Estimate: 2-4 hours on Tinker's infrastructure

**Tinker Pricing:**
- Check console for current rates
- Likely charged by GPU-hour
- LoRA is more efficient than full fine-tuning

---

## TROUBLESHOOTING

### API Key Issues
```python
# Verify API key is set
import os
print(os.environ.get('TINKER_API_KEY', 'NOT SET'))
```

### Data Format Issues
- Ensure JSONL has one JSON object per line
- Check for encoding issues (use UTF-8)
- Validate each pair has 'instruction' and 'response'

### Training Issues
- Start with small batch (2-4)
- Monitor loss - should decrease
- Check Tinker console for errors
- Try different learning rate if loss explodes

### Model Selection Issues
- Check exact model names in Tinker docs
- Case-sensitive: "Llama-3.1-8B" not "llama-3.1-8b"

---

## NEXT STEPS AFTER TRAINING

1. **Evaluate** thoroughly on test set
2. **Compare** 8B vs larger models
3. **Iterate** on hyperparameters if needed
4. **Deploy** for actual EpiBrief generation
5. **Share results** with domain experts

---

## SUMMARY CHECKLIST

- [ ] Step 1: Get API key from Tinker Console
- [ ] Step 2: Set TINKER_API_KEY environment variable
- [ ] Step 3: Install tinker package (`pip install tinker`)
- [ ] Step 4: Verify training_pairs.jsonl exists (11,632 pairs)
- [ ] Step 5: Create train/val split (run 4_split_dataset.py)
- [ ] Step 6: Review training script (5_train_with_tinker.py)
- [ ] Step 7: Run training (`python 5_train_with_tinker.py`)
- [ ] Step 8: Monitor in Tinker Console
- [ ] Step 9: Download trained weights
- [ ] Step 10: Test model (6_test_model.py)
- [ ] Step 11: Evaluate quality on test articles

---

## RESOURCES

- **Tinker Docs:** https://tinker-docs.thinkingmachines.ai/
- **Tinker Console:** https://tinker-console.thinkingmachines.ai
- **Tinker Cookbook:** https://github.com/thinking-machines-lab/tinker-cookbook
- **Your Training Data:** `training_data/training_pairs.jsonl`
- **Your Scripts:** `scripts/` directory

---

**Ready to fine-tune? Start with Step 1!**
