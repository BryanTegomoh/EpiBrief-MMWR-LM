# EpiBrief-MMWR-LM Quick Start Guide

Get your dataset built in ~3-5 hours!

---

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] ~2GB free disk space
- [ ] Internet connection
- [ ] 3-5 hours available (most time is automated scraping)

---

## Step-by-Step Instructions

### 1. Install Dependencies (2 minutes)

```bash
cd "c:\Users\bryan\OneDrive\Documents\xAI - Medicine\EpiBrief-MMWR-LM"
pip install -r requirements.txt
```

**Expected packages:**
- requests, beautifulsoup4 (web scraping)
- pandas (data processing)
- tqdm (progress bars)
- matplotlib, seaborn (visualization)

---

### 2. Run the Scraper (2-4 hours)

```bash
cd scripts
python 1_scrape_mmwr.py
```

**What it does:**
- Downloads CDC MMWR articles from 2015-2025
- Saves HTML files to `raw/YYYY/` directories
- Creates index of all articles
- Respects CDC servers (1.5s delay between requests)

**Expected output:**
```
Found 657 articles for year 2020
Downloading 657 articles from 2020...
[████████████████████] 657/657
```

**Resume capability:** If interrupted, just run again - it skips already downloaded files!

**Check progress:** Look in `logs/scrape_mmwr.log`

---

### 3. Parse Articles (10-20 minutes)

```bash
python 2_parse_articles.py
```

**What it does:**
- Extracts structured data from HTML files
- Identifies pathogens, jurisdictions, report types
- Parses sections (Abstract, Methods, Results, etc.)
- Saves JSON files to `parsed_json/`

**Expected output:**
```
Parsing articles: [████████████████████] 657/657
Successfully parsed: 645 articles (98.2% success rate)
```

**Check results:** Open `parsed_json/mm7436a1.json` to see structured data

---

### 4. Generate Training Pairs (5-10 minutes)

```bash
python 3_build_training_pairs.py
```

**What it does:**
- Creates instruction/response training pairs
- 7 different task types per article
- Outputs JSONL format (ready for fine-tuning)

**Expected output:**
```
Generating training pairs: [████████████████████] 645/645
Total pairs generated: 2,847
```

**Check results:** Open `training_data/epibrief_training.jsonl`

---

### 5. Validate Dataset (2-5 minutes)

```bash
python 4_validate_dataset.py
```

**What it does:**
- Checks for duplicates
- Validates field completeness
- Analyzes distribution (years, pathogens, jurisdictions)
- Generates quality report

**Expected output:**
```
DATASET SUMMARY
----------------------------------------------------------------------
Total training pairs: 2,847
Valid pairs: 2,836 (99.6%)
Duplicate pairs: 23

Overall Quality: EXCELLENT
Dataset is ready for fine-tuning!
```

**Check reports:**
- `training_data/_validation_summary.txt` (human-readable)
- `training_data/_validation_report.json` (detailed stats)

---

## Final Directory Structure

```
EpiBrief-MMWR-LM/
├── raw/                          # ~1.5 GB of HTML files
│   ├── 2015/ ... 2025/
│   └── _complete_index.json
├── parsed_json/                  # ~100 MB of structured JSON
│   ├── mm7436a1.json
│   ├── mm7325a1.json
│   └── _complete_parsed_dataset.json
├── training_data/                # ~50 MB training data
│   ├── epibrief_training.jsonl   ← YOUR GOLD ASSET
│   ├── epibrief_training.json
│   ├── _training_metadata.json
│   ├── _validation_report.json
│   └── _validation_summary.txt
└── logs/
    ├── scrape_mmwr.log
    ├── parse_articles.log
    ├── build_training_pairs.log
    └── validate_dataset.log
```

---

## Troubleshooting

### Issue: Scraper fails with connection error
**Solution:**
- Check internet connection
- CDC website may be temporarily down - wait and retry
- Scraper will resume from where it stopped

### Issue: Parser finds no sections in some articles
**Solution:**
- This is normal - some article types (QuickStats, Notes from the Field) have different structures
- These are tracked in `parsing_errors` stat
- As long as >95% parse successfully, you're good

### Issue: Training pair generation creates fewer pairs than expected
**Solution:**
- Some articles lack key sections (Methods, Results)
- This is normal - not every article generates all 7 pair types
- Target: 3-6 pairs per article on average

### Issue: Python module not found
**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

---

## What's Next?

### Immediate Next Steps:
1. **Inspect your dataset:** Open `training_data/epibrief_training.jsonl` and look at a few examples
2. **Read validation report:** Check `training_data/_validation_summary.txt` for quality metrics
3. **Celebrate!** You just built a unique, high-value public health AI dataset

### Phase 2: Model Training (Future)
- Rent an A100 GPU from RunPod or Lambda Labs
- LoRA fine-tune Llama 3.1 8B using your dataset
- Expected cost: $10-20 for 4-6 hours
- See README.md "Model Training" section for details

### Phase 3: Publication
- Create public GitHub repo (separate from this private one)
- Write arXiv preprint
- Release model to HuggingFace Hub
- LinkedIn/Twitter announcement

---

## Key Files You'll Use Most

| File | Purpose |
|------|---------|
| `training_data/epibrief_training.jsonl` | **Your training data** - use this for fine-tuning |
| `parsed_json/_complete_parsed_dataset.json` | Complete structured dataset |
| `training_data/_validation_summary.txt` | Dataset quality report |
| `logs/*.log` | Detailed processing logs if something goes wrong |

---

## Expected Dataset Statistics

If you scraped 2015-2025 successfully, you should see approximately:

| Metric | Expected Value |
|--------|----------------|
| Total articles | 600-700 |
| Training pairs | 2,500-4,000 |
| Valid pairs | >95% |
| Top pathogens | COVID-19, influenza, measles |
| Years covered | 2015-2025 (balanced) |

---

## Tips for Success

1. **Run overnight:** The scraper takes 2-4 hours - start it before bed
2. **Check logs:** If something fails, check `logs/*.log` for details
3. **Don't delete raw HTML:** You can re-parse/regenerate pairs without re-downloading
4. **Incremental updates:** Re-run scraper quarterly to add new MMWR articles
5. **Backup training data:** Copy `training_data/epibrief_training.jsonl` to cloud storage

---

## Questions?

- **Technical issues:** Check logs in `logs/` directory
- **Dataset questions:** Read `README.md` for full documentation
- **Future updates:** Watch this repo for Phase 2 (model training) scripts

---

**You're now ready to build a specialized public health language model!**

Next step: Start with `python scripts/1_scrape_mmwr.py` and let it run.
