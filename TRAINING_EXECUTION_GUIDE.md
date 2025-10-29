# EpiBrief-MMWR-LM: Training Execution Guide

## Complete Step-by-Step Instructions for Fine-Tuning

**Status: Ready to Train**
- Training data: 11,632 high-quality pairs prepared
- Model selected: Llama 3.1 8B Base (best-in-class for medical reasoning)
- Infrastructure: Tinker API (professional distributed training)
- Training script: Production-ready with comprehensive monitoring

---

## PRE-FLIGHT CHECKLIST

Before starting training, verify these items:

### 1. Data Files Present

```bash
dir training_data
```

**Required files:**
- `training_pairs.jsonl` (11,632 pairs) - EXISTS ✓
- `train.jsonl` (will be created by step 1)
- `val.jsonl` (will be created by step 1)

### 2. Scripts Present

```bash
dir scripts
```

**Required scripts:**
- `4_split_dataset.py` - EXISTS ✓
- `5_train_epibrief_tinker.py` - EXISTS ✓

### 3. Environment Setup

**Check Python version:**
```bash
python --version
```
Required: Python 3.8+

**Check dependencies:**
```bash
pip list | findstr tinker
```
If not installed, proceed to Installation section.

---

## PHASE 1: SETUP (15-20 minutes)

### Step 1: Get Your Tinker API Key

1. **Open Tinker Console:**
   - URL: https://tinker-console.thinkingmachines.ai
   - Log in with credentials from your email

2. **Generate API Key:**
   - Navigate to "API Keys" section
   - Click "Generate New Key" or "Create API Key"
   - **CRITICAL:** Copy the key immediately - you'll only see it once!
   - Save it in a secure location (password manager recommended)

**Example key format:** `tinker_abc123def456...` (actual key will be longer)

### Step 2: Set Environment Variable

**Windows PowerShell (Recommended):**

```powershell
# Set for current session
$env:TINKER_API_KEY = "your-api-key-here"

# Verify it's set
echo $env:TINKER_API_KEY

# Make it permanent (optional but recommended)
[System.Environment]::SetEnvironmentVariable('TINKER_API_KEY', 'your-api-key-here', 'User')
```

**To verify permanent setting:**
```powershell
# Close PowerShell and reopen, then:
echo $env:TINKER_API_KEY
```

**Windows Command Prompt (Alternative):**
```cmd
set TINKER_API_KEY=your-api-key-here
echo %TINKER_API_KEY%
```

### Step 3: Install Tinker SDK

```bash
pip install tinker
```

**Expected output:**
```
Successfully installed tinker-x.x.x
```

**Verify installation:**
```bash
python -c "import tinker; print(tinker.__version__)"
```

### Step 4: Install Additional Dependencies

```bash
pip install torch transformers numpy tqdm
```

**Note:** These should already be installed from Phase 2, but verify:
```bash
pip list | findstr -i "torch transformers"
```

---

## PHASE 2: DATA PREPARATION (5 minutes)

### Step 5: Split Dataset into Train/Val

```bash
cd scripts
python 4_split_dataset.py
```

**Expected output:**
```
======================================================================
   EpiBrief-MMWR-LM Dataset Splitter
======================================================================

Loading training pairs from: ..\training_data\training_pairs.jsonl
Total pairs loaded: 11632

Split:
  Train: 10469 pairs (90%)
  Val:   1163 pairs (10%)

Train distribution:
  comparative_analysis          :  3025
  data_interpretation           :  3696
  executive_summary             :  1697
  public_health_implications    :  1688
  quantitative_reasoning        :  2194

Val distribution:
  comparative_analysis          :   336
  data_interpretation           :   411
  executive_summary             :   189
  public_health_implications    :   188
  quantitative_reasoning        :   244

Saving train split to: ..\training_data\train.jsonl
Saving val split to: ..\training_data\val.jsonl

======================================================================
[OK] Dataset split complete!
[OK] Ready for Tinker fine-tuning
======================================================================
```

**Verification:**
```bash
dir ..\training_data
```

Should show:
- `train.jsonl` (~10,469 lines)
- `val.jsonl` (~1,163 lines)
- `training_pairs.jsonl` (original, unchanged)

---

## PHASE 3: TRAINING EXECUTION (2-4 hours)

### Step 6: Review Training Configuration

Open `5_train_epibrief_tinker.py` and verify these settings:

```python
class Config:
    # Model selection
    model_name: str = "meta-llama/Llama-3.1-8B"  # Base model, NOT Instruct

    # Training hyperparameters
    batch_size: int = 4              # Adjust if memory issues
    learning_rate: float = 1e-4      # Conservative for stability
    num_epochs: int = 3              # 3 full passes through data

    # LoRA parameters
    lora_rank: int = 32              # Good balance of efficiency/quality
    lora_alpha: float = 64.0         # Typically 2x rank

    # Data parameters
    max_length: int = 2048           # Max tokens per example
    train_on_what: TrainOnWhat = TrainOnWhat.ALL_ASSISTANT_MESSAGES
```

**Do NOT modify these unless you encounter specific issues.**

### Step 7: Start Training

```bash
cd scripts
python 5_train_epibrief_tinker.py
```

**Expected startup output:**
```
======================================================================
   EpiBrief-MMWR-LM Training with Tinker API
   Model: meta-llama/Llama-3.1-8B
======================================================================

[Phase 1/4] Loading Configuration
[OK] Config loaded: 3 epochs, batch_size=4, lr=1e-4

[Phase 2/4] Loading Training Data
[OK] Loaded train.jsonl: 10,469 pairs
[OK] Loaded val.jsonl: 1,163 pairs
[OK] Total training batches: 2,617 (per epoch)

[Phase 3/4] Initializing Tinker Training Client
[OK] Tokenizer loaded: LlamaTokenizer (vocab_size=128256)
[OK] Renderer: LlamaChatRenderer
[OK] Training client created with LoRA rank=32
[OK] Connected to Tinker distributed training infrastructure

[Phase 4/4] Training Loop
======================================================================
EPOCH 1/3
======================================================================
```

### Step 8: Monitor Training Progress

**Real-time Monitoring (in Terminal):**

You'll see output like:
```
[Epoch 1/3] Batch 10/2617: loss=2.4531, lr=0.000100, tokens/sec=1234
[Epoch 1/3] Batch 20/2617: loss=2.1245, lr=0.000099, tokens/sec=1256
[Epoch 1/3] Batch 50/2617: loss=1.8932, lr=0.000098, tokens/sec=1289
...
[Epoch 1/3] Batch 2617/2617: loss=1.2453, lr=0.000067
[OK] Epoch 1 complete: avg_loss=1.5234, time=45.2min

--- Validation Sampling ---
Instruction: Based on this MMWR table showing measles cases...
Generated: Among the 152 measles cases reported, 89% were unvaccinated...
Expected: The majority (89%) of measles cases occurred in unvaccinated individuals...
```

**Tinker Console Monitoring:**

1. Open: https://tinker-console.thinkingmachines.ai
2. Navigate to "Training Jobs" or "Active Sessions"
3. Find your job: "EpiBrief-MMWR-LM-v1"
4. View real-time metrics:
   - Loss curve (should decrease)
   - GPU utilization
   - Throughput (tokens/sec)
   - ETA to completion

**What to Watch For:**

✅ **Good signs:**
- Loss decreases steadily (2.5 → 1.8 → 1.2)
- No NaN or Inf values
- Validation samples improve over epochs
- Consistent tokens/sec throughput

⚠️ **Warning signs:**
- Loss increases or plateaus early
- Very slow throughput (<500 tokens/sec)
- Frequent errors in logs

🛑 **Stop training if:**
- Loss becomes NaN or Inf
- Out of memory errors
- Repeated connection failures

### Step 9: Checkpoint Saving

Training automatically saves checkpoints:

**Location:** `logs/training_YYYYMMDD_HHMMSS/`

**Files saved:**
- `checkpoint_epoch_1.pt` - After epoch 1
- `checkpoint_epoch_2.pt` - After epoch 2
- `checkpoint_epoch_3.pt` - Final model (this is what you want)
- `config.json` - Training configuration
- `training_log.txt` - Full training logs
- `metrics.csv` - Loss/LR over time

**To resume from checkpoint** (if training interrupted):
```python
# In 5_train_epibrief_tinker.py, modify:
resume_from_checkpoint = "logs/training_20250129_143022/checkpoint_epoch_2.pt"
```

---

## PHASE 4: POST-TRAINING (30 minutes)

### Step 10: Download Trained Model Weights

**Option A: From Tinker Console (Recommended)**

1. Go to Tinker Console → Your Training Job
2. Click "Download Weights" or "Export Model"
3. Choose format: "SafeTensors" (recommended) or "PyTorch"
4. Save to: `models/epibrief-mmwr-lm-v1/`

**Option B: Via Python Script**

Create `scripts/download_model.py`:
```python
from tinker import service_client

# Download trained LoRA weights
service_client.download_lora_weights(
    job_id="your-job-id-from-console",
    output_path="../models/epibrief-mmwr-lm-v1/lora_weights.safetensors"
)

print("Model weights downloaded successfully!")
```

Run:
```bash
python download_model.py
```

**Expected directory structure:**
```
models/epibrief-mmwr-lm-v1/
├── lora_weights.safetensors  (LoRA adapter weights)
├── config.json               (Model configuration)
└── training_args.json        (Training hyperparameters)
```

### Step 11: Test Fine-Tuned Model

Create `scripts/6_test_model.py`:

```python
"""
Test fine-tuned EpiBrief-MMWR-LM model
"""

from tinker import service_client
from tinker.renderers import Message, get_renderer
from tinker.model_info import get_tokenizer
import json

# Configuration
BASE_MODEL = "meta-llama/Llama-3.1-8B"
LORA_WEIGHTS = "../models/epibrief-mmwr-lm-v1/lora_weights.safetensors"

print("Loading fine-tuned model...")

# Load model with LoRA weights
inference_client = service_client.create_inference_client(
    base_model=BASE_MODEL,
    lora_weights=LORA_WEIGHTS
)

# Load tokenizer and renderer
tokenizer = get_tokenizer(BASE_MODEL)
renderer = get_renderer("llama_chat", tokenizer)

print("Model loaded successfully!\n")

# Test cases
test_cases = [
    {
        "title": "Executive Summary Generation",
        "instruction": """Based on this MMWR article, generate an executive summary following CDC format.

Article: Measles Outbreak in Urban Community — United States, 2024

During January–March 2024, 152 measles cases were reported to the county health department. Among these, 135 (89%) were in unvaccinated individuals, and 98 (64%) were in children aged <5 years. The outbreak was traced to an international traveler who had acquired measles abroad. Secondary transmission occurred in community settings, schools, and healthcare facilities.

Public health response included vaccination campaigns, contact tracing, and community education. The outbreak resulted in 23 hospitalizations (15%) and 2 cases of pneumonia. No deaths occurred.

Generate the summary following CDC's "What is known/added/implications" format."""
    },
    {
        "title": "Data Interpretation from Table",
        "instruction": """Interpret the following table from an MMWR article on flu vaccination coverage:

Table: Influenza Vaccination Coverage by Age Group — United States, 2024 Season
Age Group | N | Vaccinated | % Vaccinated
6mo-4yr   | 1,234 | 567 | 45.9%
5-17yr    | 3,456 | 1,234 | 35.7%
18-49yr   | 12,345 | 3,456 | 28.0%
50-64yr   | 5,678 | 2,345 | 41.3%
≥65yr     | 4,567 | 3,456 | 75.7%

Provide a data interpretation paragraph suitable for an MMWR report."""
    },
    {
        "title": "Public Health Implications",
        "instruction": """Based on this finding from an MMWR article, articulate the public health implications:

Finding: "Analysis of antibiotic prescribing patterns in 500 outpatient clinics revealed that 30% of prescriptions for upper respiratory infections were for conditions unlikely to benefit from antibiotics. This represents approximately 15 million potentially unnecessary prescriptions annually, contributing to antimicrobial resistance and healthcare costs."

Write the public health implications section."""
    }
]

# Run test cases
for i, test in enumerate(test_cases, 1):
    print(f"{'='*70}")
    print(f"TEST CASE {i}: {test['title']}")
    print(f"{'='*70}\n")

    # Format as conversation
    messages = [Message(role="user", content=test["instruction"])]

    # Generate response
    print("Generating response...\n")

    response = inference_client.generate(
        messages=messages,
        max_tokens=512,
        temperature=0.7,
        top_p=0.9
    )

    print("GENERATED OUTPUT:")
    print("-" * 70)
    print(response)
    print("-" * 70)
    print("\n")

print("Testing complete!")
```

**Run tests:**
```bash
python 6_test_model.py
```

**Expected output:**
```
======================================================================
TEST CASE 1: Executive Summary Generation
======================================================================

Generating response...

GENERATED OUTPUT:
----------------------------------------------------------------------
**What is already known about this topic?**
Measles is a highly contagious vaccine-preventable disease that can lead to serious complications, particularly in unvaccinated children.

**What is added by this report?**
During a 2024 outbreak in an urban community, 152 measles cases were reported, with 89% occurring in unvaccinated individuals and 64% in children aged <5 years. The outbreak originated from international travel and resulted in 23 hospitalizations.

**What are the implications for public health practice?**
This outbreak underscores the importance of maintaining high vaccination coverage and ensuring timely vaccination of children. Healthcare providers should verify vaccination status and offer catch-up vaccination to unvaccinated individuals.
----------------------------------------------------------------------
```

### Step 12: Quality Evaluation

**Evaluate on these criteria:**

1. **Factual Accuracy** (Critical)
   - Does model preserve numbers correctly?
   - Are percentages calculated properly?
   - No hallucinated statistics?

2. **CDC Style Adherence**
   - Follows "What is known/added/implications" format?
   - Uses appropriate epidemiological terminology?
   - Professional, objective tone?

3. **Quantitative Reasoning**
   - Interprets tables correctly?
   - Makes appropriate comparisons?
   - Articulates trends and patterns?

4. **Public Health Framing**
   - Identifies actionable implications?
   - Connects findings to practice?
   - Appropriate level of urgency?

**Scoring rubric** (for each test case):
- 5 = Excellent (CDC-publication ready)
- 4 = Good (minor edits needed)
- 3 = Acceptable (significant edits needed)
- 2 = Poor (major issues)
- 1 = Unusable (hallucinations, inaccuracies)

**Target:** Average score ≥4.0 across test cases

---

## TROUBLESHOOTING

### Issue 1: API Key Not Recognized

**Symptoms:**
```
Error: TINKER_API_KEY environment variable not set
```

**Solutions:**
```powershell
# Verify it's set
echo $env:TINKER_API_KEY

# If empty, set it again
$env:TINKER_API_KEY = "your-key-here"

# Try permanent setting
[System.Environment]::SetEnvironmentVariable('TINKER_API_KEY', 'your-key-here', 'User')

# Restart PowerShell and verify
```

### Issue 2: Out of Memory During Training

**Symptoms:**
```
RuntimeError: CUDA out of memory
```

**Solutions:**
1. Reduce batch size in `5_train_epibrief_tinker.py`:
   ```python
   batch_size: int = 2  # Down from 4
   ```

2. Reduce max_length:
   ```python
   max_length: int = 1024  # Down from 2048
   ```

3. Contact Tinker support for larger GPU allocation

### Issue 3: Training Loss Not Decreasing

**Symptoms:**
- Loss stays high (>2.0) after epoch 1
- Loss increases or oscillates wildly

**Solutions:**
1. Lower learning rate:
   ```python
   learning_rate: float = 5e-5  # Down from 1e-4
   ```

2. Check data quality:
   ```python
   # Inspect a few training examples
   python -c "
   import json
   with open('../training_data/train.jsonl') as f:
       for i, line in enumerate(f):
           if i < 3:
               print(json.loads(line))
   "
   ```

3. Verify model is using LoRA (not full fine-tuning)

### Issue 4: Connection Errors to Tinker

**Symptoms:**
```
ConnectionError: Failed to connect to Tinker API
```

**Solutions:**
1. Check internet connection
2. Verify API key is valid (try logging into console)
3. Check Tinker status page: https://status.thinkingmachines.ai
4. Wait 5 minutes and retry (temporary outage)

### Issue 5: Training Data Not Found

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory: '../training_data/train.jsonl'
```

**Solutions:**
1. Verify you're in the `scripts/` directory:
   ```bash
   pwd
   # Should show: .../EpiBrief-MMWR-LM/scripts
   ```

2. Check if split was run:
   ```bash
   dir ..\training_data
   # Should show train.jsonl and val.jsonl
   ```

3. If missing, run split script:
   ```bash
   python 4_split_dataset.py
   ```

---

## SUCCESS CRITERIA

Your fine-tuned model is ready for deployment when:

✅ **Training completed successfully**
- All 3 epochs finished without errors
- Final loss <1.5 (target: 1.0-1.3)
- Validation samples show CDC-style output

✅ **Test cases pass quality checks**
- Average score ≥4.0 on evaluation rubric
- No hallucinated statistics
- Proper CDC formatting

✅ **Model generates coherent outputs**
- Executive summaries follow CDC structure
- Data interpretations are accurate
- Public health implications are actionable

✅ **No critical errors in validation**
- Numbers match source data
- No logical inconsistencies
- Appropriate epidemiological terminology

---

## COST ESTIMATION

**Tinker Pricing** (check console for current rates):

**Training costs:**
- Model size: 8B parameters (LoRA: ~256M trainable)
- Dataset size: 10,469 training examples
- Epochs: 3
- Estimated GPU hours: 2-4 hours
- Estimated cost: $20-$80 (rough estimate)

**Inference costs** (after training):
- Per 1,000 tokens generated
- Check console for exact pricing
- LoRA inference is efficient

**Tips to minimize costs:**
1. Start with 1 epoch to verify setup works
2. Use smaller batch size if training completes quickly
3. Download weights immediately after training
4. Run local inference if possible (with LoRA weights)

---

## NEXT STEPS AFTER SUCCESSFUL TRAINING

### Immediate (Next 24 hours)
1. ✅ Download model weights
2. ✅ Run comprehensive test suite
3. ✅ Evaluate on 10 real MMWR articles (not in training set)
4. ✅ Document model performance metrics

### Short-term (Next week)
1. Compare outputs to current GPT-4/Claude performance
2. Get domain expert feedback (epidemiologist review)
3. Create deployment documentation
4. Set up inference pipeline for production use

### Medium-term (Next month)
1. Evaluate on CDC's actual EpiBrief generation tasks
2. Consider training on larger model (Llama 3.1 70B) if needed
3. Build web interface for EpiBrief generation
4. Publish methodology and results

### Long-term (Next quarter)
1. Expand to multimodal (Option 3 from strategy doc)
2. Fine-tune on additional CDC report types
3. Deploy for actual CDC workflow integration
4. Measure impact on EpiBrief production time/quality

---

## DOCUMENTATION AUDIT TRAIL

**Project Phase Summary:**

| Phase | Status | Output | Quality |
|-------|--------|--------|---------|
| Phase 1: Data Collection | ✅ Complete | 3,419 MMWR articles (2016-2025) | 100% coverage |
| Phase 2A: Article Parsing | ✅ Complete | 3,419 parsed JSON files | 100% success rate |
| Phase 2B: Training Pair Generation | ✅ Complete | 11,632 instruction-response pairs | 64% quantitative focus |
| Phase 2C: Dataset Split | ⏳ Ready | train.jsonl + val.jsonl | Awaiting execution |
| Phase 3: Fine-Tuning | ⏳ Ready | Llama 3.1 8B + LoRA | Script prepared |
| Phase 4: Evaluation | ⏳ Pending | Model quality metrics | Post-training |
| Phase 5: Deployment | ⏳ Pending | Production inference | Post-validation |

**Key Decisions Made:**

1. **Multimodal Strategy:** Option 2 (Enhanced Text + Tables)
   - Rationale: Balances capability with timeline
   - Result: 64% quantitative training pairs

2. **Model Selection:** Llama 3.1 8B Base
   - Rationale: Best medical reasoning (AMEGA: 464.8 vs 362.3)
   - Alternative considered: Qwen3 8B (rejected: lower medical performance)
   - Alternative considered: nanochat (rejected: too small for task)

3. **Infrastructure:** Tinker API
   - Rationale: Professional distributed training without DevOps
   - Benefit: 2-4 hours vs days of setup time

4. **Training Parameters:**
   - LoRA rank: 32 (efficient adaptation)
   - Learning rate: 1e-4 (conservative for stability)
   - Epochs: 3 (standard for instruction tuning)
   - Batch size: 4 (memory-efficient)

**Risk Assessment:**

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|---------|------------|
| Training fails (technical) | Low | High | Tinker handles infrastructure reliability |
| Model quality insufficient | Medium | High | 11,632 high-quality pairs reduce risk |
| Cost overrun | Low | Medium | Clear pricing, efficient LoRA approach |
| Timeline delay | Low | Low | All preparation complete, training automated |

---

## SUPPORT RESOURCES

**Tinker Documentation:**
- Main docs: https://tinker-docs.thinkingmachines.ai/
- Getting started: https://tinker-docs.thinkingmachines.ai/install
- Training guide: https://tinker-docs.thinkingmachines.ai/train
- API reference: https://tinker-docs.thinkingmachines.ai/api

**Tinker Console:**
- URL: https://tinker-console.thinkingmachines.ai
- Use for: Monitoring, downloading weights, viewing logs

**Project Documentation:**
- [PROJECT_VISION.md](PROJECT_VISION.md) - Overall project goals
- [MULTIMODAL_STRATEGY.md](MULTIMODAL_STRATEGY.md) - Why Option 2
- [MODEL_SELECTION_ANALYSIS.md](MODEL_SELECTION_ANALYSIS.md) - Why Llama 3.1 8B
- [TINKER_SETUP_GUIDE.md](TINKER_SETUP_GUIDE.md) - Detailed Tinker instructions
- [HTML_STRUCTURE_ANALYSIS.md](HTML_STRUCTURE_ANALYSIS.md) - Parser design rationale

**Contact:**
- Tinker Support: support@thinkingmachines.ai
- Tinker Community: (check docs for Discord/forum link)

---

## FINAL PRE-FLIGHT CHECK

Before running training, verify:

- [ ] Tinker API key obtained from console
- [ ] TINKER_API_KEY environment variable set and verified
- [ ] `pip install tinker` completed successfully
- [ ] `training_data/training_pairs.jsonl` exists (11,632 pairs)
- [ ] Run `4_split_dataset.py` to create train/val splits
- [ ] `scripts/5_train_epibrief_tinker.py` reviewed and understood
- [ ] Sufficient time allocated (2-4 hours + monitoring)
- [ ] Tinker Console accessible for monitoring
- [ ] Understanding of success criteria and evaluation plan

**When all boxes are checked, execute:**

```bash
cd scripts
python 4_split_dataset.py
python 5_train_epibrief_tinker.py
```

**Then monitor in:** https://tinker-console.thinkingmachines.ai

---

**Good luck! You're about to train a world-class epidemiological reasoning model.**

**Your dataset is exceptional. Your preparation was thorough. Execute with confidence.**
