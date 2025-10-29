# Ready to Train: Pre-Flight Checklist

**Before you run `python 5_train_epibrief_tinker.py` and go to sleep, complete these steps:**

---

## Step 1: Get Your Tinker API Key (15 minutes)

### A. Access Tinker Console
1. Open: https://tinker-console.thinkingmachines.ai
2. Log in with the credentials from your Thinking Machines email
3. Navigate to "API Keys" section
4. Click "Generate New Key" or "Create API Key"

### B. Copy Your Key
- **CRITICAL:** Copy the key immediately - you'll only see it once!
- It should look like: `tinker_abc123def456...` (longer)
- Save it somewhere secure (password manager)

---

## Step 2: Set Environment Variable (2 minutes)

### Windows PowerShell (Recommended):
```powershell
# Set API key for current session
$env:TINKER_API_KEY = "your-actual-api-key-here"

# Verify it's set
echo $env:TINKER_API_KEY
```

**IMPORTANT:** If you close PowerShell and reopen, you'll need to set it again!

### Make It Permanent (Optional but Recommended):
```powershell
# This sets it permanently for your user account
[System.Environment]::SetEnvironmentVariable('TINKER_API_KEY', 'your-actual-api-key-here', 'User')

# Close and reopen PowerShell, then verify:
echo $env:TINKER_API_KEY
```

---

## Step 3: Install Tinker SDK (2 minutes)

```bash
pip install tinker
```

**Verify installation:**
```bash
python -c "import tinker; print('Tinker installed:', tinker.__version__)"
```

---

## Step 4: Split Dataset (5 minutes)

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

Saving train split to: ..\training_data\train.jsonl
Saving val split to: ..\training_data\val.jsonl

======================================================================
[OK] Dataset split complete!
[OK] Ready for Tinker fine-tuning
======================================================================
```

**Verify files created:**
```bash
dir ..\training_data
```

You should see:
- `train.jsonl` (10,469 lines)
- `val.jsonl` (1,163 lines)
- `training_pairs.jsonl` (11,632 lines - original)

---

## Step 5: Verify Everything is Ready

Run this quick check:

```powershell
# Check 1: API key set
if ($env:TINKER_API_KEY) {
    Write-Host "[OK] API key is set" -ForegroundColor Green
} else {
    Write-Host "[ERROR] API key NOT set!" -ForegroundColor Red
}

# Check 2: Tinker installed
python -c "import tinker; print('[OK] Tinker SDK installed')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Tinker not installed!" -ForegroundColor Red
}

# Check 3: Training data exists
if (Test-Path "..\training_data\train.jsonl") {
    Write-Host "[OK] Training data exists" -ForegroundColor Green
} else {
    Write-Host "[ERROR] train.jsonl not found!" -ForegroundColor Red
}

if (Test-Path "..\training_data\val.jsonl") {
    Write-Host "[OK] Validation data exists" -ForegroundColor Green
} else {
    Write-Host "[ERROR] val.jsonl not found!" -ForegroundColor Red
}
```

---

## Step 6: Start Training (2-4 hours)

**NOW you can run:**
```bash
cd scripts
python 5_train_epibrief_tinker.py
```

### What You'll See:

**Initial output:**
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
[OK] Total training batches: 2,618 (per epoch)

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

**During training (this will run for 2-4 hours):**
```
[Epoch 1/3] Batch 10/2618: loss=2.4531, lr=0.000100, tokens/sec=1234
[Epoch 1/3] Batch 20/2618: loss=2.1245, lr=0.000099, tokens/sec=1256
...
```

### Monitor Progress:

**Option 1: Watch Terminal**
- Loss should decrease over time (2.5 → 1.8 → 1.2)
- Watch for any errors

**Option 2: Tinker Console**
- Open: https://tinker-console.thinkingmachines.ai
- Navigate to "Training Jobs" or "Active Sessions"
- Find: "EpiBrief-MMWR-LM-v1"
- See real-time metrics, GPU usage, ETA

---

## What If Something Goes Wrong?

### Error: "TINKER_API_KEY environment variable not set"
**Solution:** Go back to Step 2, set the API key

### Error: "No module named 'tinker'"
**Solution:** Go back to Step 3, install Tinker

### Error: "FileNotFoundError: train.jsonl"
**Solution:** Go back to Step 4, run the split script

### Error: Connection timeout or API errors
**Solution:**
- Check internet connection
- Verify API key is correct (re-copy from console)
- Check Tinker status: https://status.thinkingmachines.ai (if exists)
- Wait 5 minutes and retry

### Training seems stuck
**Check:**
- Tinker Console for actual progress
- Last line in terminal - when was it updated?
- If truly stuck >30 minutes with no output, Ctrl+C and restart

---

## After Training Completes

**You'll see:**
```
======================================================================
TRAINING COMPLETE
======================================================================

✓ Model saved to Tinker path: /path/to/model
✓ Local checkpoint directory: C:\Users\bryan\...\logs\epibrief-training
✓ Total batches processed: 7,854
✓ Total training pairs seen: 31,416

================================================================================
TO DOWNLOAD LORA WEIGHTS FOR LOCAL INFERENCE:
================================================================================
rest_client = service_client.create_rest_client()
future = rest_client.download_checkpoint_archive_from_tinker_path('/path/to/model')
with open('epibrief-lora-weights.tar.gz', 'wb') as f:
    f.write(future.result())

Then extract and use with your base model (meta-llama/Llama-3.1-8B)
```

**Next steps after training:**
1. Download the LoRA weights from Tinker Console
2. Run test script: `python 6_test_model.py`
3. Evaluate quality on test cases
4. Celebrate! 🎉

---

## Complete Pre-Flight Checklist

Before running training, verify:

- [ ] Tinker API key obtained from console
- [ ] `TINKER_API_KEY` environment variable set
- [ ] Verified with `echo $env:TINKER_API_KEY`
- [ ] Tinker SDK installed: `pip install tinker`
- [ ] Verified with `python -c "import tinker"`
- [ ] Dataset split: `python 4_split_dataset.py` completed
- [ ] `train.jsonl` exists (10,469 pairs)
- [ ] `val.jsonl` exists (1,163 pairs)
- [ ] You're in the `scripts/` directory
- [ ] You have 2-4 hours for training to complete
- [ ] (Optional) Computer won't go to sleep during training

**When all boxes checked:**
```bash
python 5_train_epibrief_tinker.py
```

Then monitor via Tinker Console and go to sleep if you want!

---

## Training Duration & Cost

**Time:** 2-4 hours (distributed training on Tinker infrastructure)
**Cost:** Approximately $20-80 (check Tinker Console for exact pricing)
**Output:** Fine-tuned Llama 3.1 8B with LoRA weights for epidemiological reasoning

---

## Questions?

- **Training guide:** [TRAINING_EXECUTION_GUIDE.md](TRAINING_EXECUTION_GUIDE.md)
- **Tinker setup:** [TINKER_SETUP_GUIDE.md](TINKER_SETUP_GUIDE.md)
- **Bug fixes:** [BUGFIX_SUMMARY.md](BUGFIX_SUMMARY.md)
- **Tinker support:** support@thinkingmachines.ai

---

**You're almost there! Just 4 setup steps, then train and sleep.** 🚀
