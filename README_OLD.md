# EpiBrief-MMWR-LM

**A Specialized Epidemiological Reasoning Model Trained on CDC MMWR Reports**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Model: Llama 3.1 8B](https://img.shields.io/badge/Model-Llama%203.1%208B-green.svg)](https://ai.meta.com/llama/)
[![Training: Tinker API](https://img.shields.io/badge/Training-Tinker%20API-blue.svg)](https://tinker-docs.thinkingmachines.ai/)

---

## 🚀 Project Status: Ready for Training

| Phase | Status | Details |
|-------|--------|---------|
| **Phase 1: Data Collection** | ✅ Complete | 3,419 MMWR articles (2016-2025) |
| **Phase 2A: Enhanced Parsing** | ✅ Complete | 4,615 tables extracted, 1,903 summary boxes |
| **Phase 2B: Training Pairs** | ✅ Complete | 11,632 instruction-response pairs (64% quantitative) |
| **Phase 2C: Dataset Split** | ⏳ Ready | Ready to run `4_split_dataset.py` |
| **Phase 3: Fine-Tuning** | ⏳ Ready | Training script prepared, Tinker API configured |
| **Phase 4: Evaluation** | ⏳ Pending | Post-training validation |
| **Phase 5: Deployment** | ⏳ Pending | Production inference setup |

---

## Overview

**EpiBrief-MMWR-LM** is a specialized language model fine-tuned on CDC MMWR articles to generate high-quality epidemiological briefs with world-class quantitative reasoning capabilities. Unlike generic models, this system learns CDC's epidemiological reasoning patterns, data interpretation methods, and public health communication style.

### What Makes This Special

- **Pure CDC Gold Standard**: Trained exclusively on 3,419 peer-reviewed CDC MMWR reports (2016-2025)
- **Quantitative Focus**: 64% of training pairs focus on data interpretation and table reasoning
- **Enhanced Table Understanding**: Smart parsing with rowspan/colspan reconstruction for accurate data extraction
- **11,632 Training Pairs**: World-class dataset with 6 specialized pair types
- **Best-in-Class Model**: Llama 3.1 8B (AMEGA medical score: 464.8 vs competitors at 300-400)
- **Professional Infrastructure**: Tinker API for distributed training (2-4 hours vs days of setup)

### Key Capabilities (After Training)

✅ Generate CDC-style executive summaries
✅ Interpret epidemiological tables and extract quantitative findings
✅ Articulate public health implications from data
✅ Perform comparative analysis across demographic groups
✅ Extract and synthesize methods from surveillance reports
✅ Reason about rates, percentages, trends, and disease burden

---

## ⚠️ Important Disclaimer

**This is an independent research project and is NOT an official CDC product.**

This model uses publicly available CDC MMWR reports as training data. It is not endorsed by, affiliated with, or representative of the Centers for Disease Control and Prevention (CDC) or any government agency. This is a research prototype for educational and experimental purposes.

---

## Quick Start

### For Training (Next Step)

1. **Get Tinker API Key:**
   - Go to https://tinker-console.thinkingmachines.ai
   - Generate API key
   - Set environment variable: `$env:TINKER_API_KEY = "your-key"`

2. **Install Tinker:**
   ```bash
   pip install tinker
   ```

3. **Split Dataset:**
   ```bash
   cd scripts
   python 4_split_dataset.py
   ```

4. **Start Training:**
   ```bash
   python 5_train_epibrief_tinker.py
   ```

5. **Monitor Progress:**
   - Console: https://tinker-console.thinkingmachines.ai
   - Estimated time: 2-4 hours

**See [TRAINING_EXECUTION_GUIDE.md](TRAINING_EXECUTION_GUIDE.md) for complete step-by-step instructions.**

---

## Project Structure

```
EpiBrief-MMWR-LM/
├── README.md                           # This file
├── PROJECT_VISION.md                   # Project goals and methodology
├── QUICK_START.md                      # Fast-track instructions
├── TRAINING_EXECUTION_GUIDE.md         # Detailed training guide (NEW!)
├── MULTIMODAL_STRATEGY.md             # Why Option 2 (Enhanced Text + Tables)
├── MODEL_SELECTION_ANALYSIS.md        # Why Llama 3.1 8B
├── TINKER_SETUP_GUIDE.md              # Tinker API setup
├── HTML_STRUCTURE_ANALYSIS.md         # Parser design rationale
│
├── raw/                                # 3,419 HTML articles
├── parsed_json/                        # 3,419 parsed JSON files
├── training_data/
│   ├── training_pairs.jsonl            # 11,632 instruction-response pairs
│   ├── train.jsonl                     # 90% split (to be created)
│   └── val.jsonl                       # 10% split (to be created)
│
├── scripts/
│   ├── 1_scrape_mmwr.py                # ✅ Phase 1: Article scraper
│   ├── 2_parse_articles_ENHANCED.py    # ✅ Phase 2A: Enhanced parser
│   ├── 3_generate_training_pairs.py    # ✅ Phase 2B: Pair generator
│   ├── 4_split_dataset.py              # ⏳ Phase 2C: Train/val split
│   ├── 5_train_epibrief_tinker.py      # ⏳ Phase 3: Training script
│   └── 6_test_model.py                 # ⏳ Phase 4: Model testing
│
├── models/                             # Trained models (to be created)
│   └── epibrief-mmwr-lm-v1/
│       ├── lora_weights.safetensors
│       ├── config.json
│       └── training_args.json
│
└── logs/                               # Training logs (auto-generated)
    └── training_YYYYMMDD_HHMMSS/
        ├── checkpoint_epoch_1.pt
        ├── checkpoint_epoch_2.pt
        ├── checkpoint_epoch_3.pt
        ├── training_log.txt
        └── metrics.csv
```

---

## Dataset Construction Pipeline

### Phase 1: Data Collection & Processing

This repository contains the complete pipeline for building the training dataset:

#### Step 1: Web Scraping (1_scrape_mmwr.py)

Downloads CDC MMWR articles from the online archive (https://www.cdc.gov/mmwr/).

**Features:**
- Scrapes year index pages (2015-2025)
- Downloads individual article HTML files
- Respects CDC servers (1.5s delay between requests)
- Resume capability (skips already downloaded)
- Comprehensive logging

**Usage:**
```bash
cd scripts
python 1_scrape_mmwr.py
```

**Output:**
- Raw HTML files in `raw/YYYY/` directories
- Complete index of all articles (tracked in git)
- Download logs

**Expected articles:** 800-1,200 HTML articles (2015-2025)

**Note:** This version scrapes HTML articles only. Some older or special issues may be PDF-only and will be skipped. For Phase 1 goals (2,500+ training pairs), HTML coverage is sufficient.

---

#### Step 2: Article Parsing (2_parse_articles.py)

Extracts structured data from HTML files.

**Features:**
- Metadata extraction (title, authors, date, DOI, volume/issue)
- Section parsing (Abstract, Methods, Results, Discussion, Implications)
- Summary box extraction ("What is known", "What is added", "Implications")
- Automatic classification:
  - Pathogen detection (influenza, COVID-19, measles, etc.)
  - Jurisdiction detection (states, territories)
  - Report type (outbreak investigation, surveillance, recommendations)
  - Topic keywords

**Usage:**
```bash
cd scripts
python 2_parse_articles.py
```

**Output:**
- Structured JSON files in `parsed_json/` directory
- Each article becomes a rich metadata object
- Complete parsed dataset index

**Sample JSON Structure:**
```json
{
  "id": "mm7436a1",
  "title": "Pediatric Influenza-Associated Encephalopathy...",
  "authors": ["Author 1", "Author 2"],
  "publication_date": "2024-09-25",
  "volume": "74",
  "issue": "36",
  "category": "Full Report",
  "doi": "10.15585/mmwr.mm7436a1",
  "summary": {
    "what_is_known": "...",
    "what_is_added": "...",
    "implications": "..."
  },
  "sections": {
    "abstract": "...",
    "introduction": "...",
    "methods": "...",
    "results": "...",
    "discussion": "..."
  },
  "metadata": {
    "pathogens": ["influenza"],
    "jurisdictions": ["United States"],
    "report_type": "surveillance_summary",
    "topics": ["pediatric", "encephalopathy", "surveillance"]
  }
}
```

---

#### Step 3: Training Pair Generation (3_build_training_pairs.py)

Converts structured articles into instruction/response training pairs for supervised fine-tuning.

**Pair Types Generated:**

1. **Executive Summary** - "Summarize key findings for state health director in 2-3 sentences"
2. **Methods Description** - "Describe surveillance methods used"
3. **Public Health Implications** - "What are the implications for public health practice?"
4. **Case Definition** - "Define a confirmed case for surveillance purposes"
5. **Key Statistics** - "State case counts, timeframe, and control measures"
6. **Recommendations** - "What actions should health departments implement?"
7. **Timeline** - "Describe the outbreak timeline and key dates"

**Usage:**
```bash
cd scripts
python 3_build_training_pairs.py
```

**Output:**
- `training_data/epibrief_training.jsonl` (one JSON per line, ready for training)
- `training_data/epibrief_training.json` (formatted JSON for inspection)
- `training_data/_training_metadata.json` (dataset statistics)

**Expected output:** ~2,500-4,000 training pairs from ~600 articles (~4-6 pairs per article)

**Sample Training Pair:**
```json
{
  "instruction": "Summarize the key findings of this CDC MMWR report in 2-3 sentences for a state health director, using CDC MMWR style.",
  "input": "Title: Pediatric Influenza-Associated Encephalopathy...\n\nWhat is added by this report: During the 2023-24 season, 47 cases were identified...",
  "output": "During the 2023-24 influenza season, 47 pediatric influenza-associated encephalopathy cases were identified across multiple states. Most cases occurred in previously healthy children, and several resulted in long-term neurologic sequelae. Enhanced surveillance and timely antiviral treatment are critical for improving outcomes.",
  "pair_type": "executive_summary"
}
```

---

#### Step 4: Dataset Validation (4_validate_dataset.py)

Validates data quality and generates comprehensive statistics.

**Validation Checks:**
- Required fields present (instruction, input, output, pair_type)
- Field types and lengths
- Duplicate detection
- Distribution analysis (temporal, by pathogen, by jurisdiction, by pair type)

**Usage:**
```bash
cd scripts
python 4_validate_dataset.py
```

**Output:**
- `training_data/_validation_report.json` (detailed JSON report)
- `training_data/_validation_summary.txt` (human-readable summary)
- Quality assessment and recommendations

**Sample Validation Output:**
```
DATASET SUMMARY
----------------------------------------------------------------------
Total training pairs: 2,847
Valid pairs: 2,836
Invalid pairs: 11
Duplicate pairs: 23
Validity rate: 99.6%

PAIR TYPE DISTRIBUTION
----------------------------------------------------------------------
executive_summary              628 (22.1%)
methods_description            512 (18.0%)
public_health_implications     489 (17.2%)
results_summary               445 (15.6%)
...

QUALITY ASSESSMENT
----------------------------------------------------------------------
Overall Quality: EXCELLENT

Dataset is ready for fine-tuning!
```

---

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- ~2GB free disk space (for raw HTML files)
- Internet connection (for downloading MMWR articles)

### Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/YourUsername/EpiBrief-MMWR-LM.git
   cd EpiBrief-MMWR-LM
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the pipeline:**
   ```bash
   # Step 1: Download MMWR articles
   cd scripts
   python 1_scrape_mmwr.py

   # Step 2: Parse articles to structured JSON
   python 2_parse_articles.py

   # Step 3: Generate training pairs
   python 3_build_training_pairs.py

   # Step 4: Validate dataset
   python 4_validate_dataset.py
   ```

**Expected runtime:**
- Scraping: 2-4 hours (with rate limiting)
- Parsing: 10-20 minutes
- Training pair generation: 5-10 minutes
- Validation: 2-5 minutes

**Total: ~3-5 hours for complete dataset construction**

---

## Training Data Statistics

### Dataset Overview

| Metric | Value |
|--------|-------|
| **Years covered** | 2016-2025 (9 years) |
| **Total articles** | 3,419 MMWR articles |
| **Training pairs** | 11,632 instruction-response pairs |
| **Tables extracted** | 4,615 tables with smart parsing |
| **Summary boxes** | 1,903 CDC summary boxes |
| **Quantitative focus** | 64% (7,468 table-based pairs) |
| **Parsing success rate** | 100% (all 3,419 articles parsed) |

### Training Pair Distribution

```
Total Training Pairs: 11,632

Distribution by Type:
  Executive Summary           1,886 pairs (16%)
  Data Interpretation         4,107 pairs (35%) ⭐ Quantitative
  Public Health Implications  1,876 pairs (16%)
  Comparative Analysis        3,361 pairs (29%) ⭐ Quantitative
  Quantitative Reasoning      2,438 pairs (21%) ⭐ Quantitative
  Methods Extraction          1 pair (<1%)

Quantitative Reasoning Training: 7,468 pairs (64%)
```

**Why this dataset is world-class:**
- Pure CDC gold standard reasoning (not generic medical text)
- 64% focuses on data interpretation and quantitative reasoning
- Enhanced table understanding with smart parsing
- Balanced task distribution across 6 specialized types
- Quality scores tracked for every pair

---

## Model Training Configuration

### Training Specifications

**Base Model:** `meta-llama/Llama-3.1-8B` (Base, NOT Instruct)
- **Why Llama 3.1 8B?** Best-in-class medical reasoning (AMEGA: 464.8 vs competitors at 300-400)
- **Why Base not Instruct?** Instruct versions may resist fine-tuning; Base learns better

**Training Method:** LoRA (Low-Rank Adaptation)
```python
LoRA Configuration:
  - Rank: 32 (good balance of efficiency/quality)
  - Alpha: 64 (typically 2x rank)
  - Target modules: All attention layers
  - Trainable parameters: ~256M (vs 8B total)
```

**Hyperparameters:**
```python
Learning Rate: 1e-4 (with linear decay)
Batch Size: 4
Max Sequence Length: 2048 tokens
Epochs: 3
Total Training Steps: ~7,850
Training Data: 10,469 pairs (90% split)
Validation Data: 1,163 pairs (10% split)
```

**Infrastructure:** Tinker API (Thinking Machines)
- **Training Time:** 2-4 hours (distributed training)
- **Cost:** ~$20-80 (estimated, check console for exact pricing)
- **Advantages:** No GPU setup, automatic checkpointing, professional infrastructure

**Training Script:** [scripts/5_train_epibrief_tinker.py](scripts/5_train_epibrief_tinker.py)

### Model Alternatives Considered

| Model | Medical Score (AMEGA) | Decision |
|-------|----------------------|----------|
| **Llama 3.1 8B** | **464.8** | ✅ **SELECTED** - Best medical reasoning |
| Qwen3 8B | 362.3 | ❌ Rejected - 102 points lower |
| nanochat 1.9B | ~250 (estimated) | ❌ Rejected - Too small for complex reasoning |
| Llama 3.1 70B | 500+ (estimated) | ⏳ Future upgrade option |

**Source:** arXiv:2502.08954v1 (February 2025) - Recent medical benchmark comparison

---

## Intended Use Cases

### ✅ Appropriate Uses

- **Public health training:** Teaching CDC MMWR writing style to epidemiology students
- **Decision support:** Rapid briefing generation for health department leadership
- **Research:** Studying how AI can internalize domain-specific communication patterns
- **Outbreak response:** Accelerating situational awareness document drafting

### ❌ Inappropriate Uses

- **Clinical diagnosis:** This model does NOT diagnose patients
- **Treatment decisions:** Not for individual patient care recommendations
- **Policy decisions:** Should not replace human expert judgment for policy
- **Automated reporting:** Outputs must be reviewed by qualified epidemiologists

---

## Limitations & Biases

### Data Limitations

1. **Geographic bias:** Primarily US-focused (CDC MMWR covers US public health)
2. **Temporal bias:** More recent years may have different content (e.g., COVID-19 dominance 2020-2023)
3. **Language:** English only
4. **Completeness:** Not all public health topics equally represented
5. **HTML-only scraping:** Phase 1 captures HTML articles only; PDF-only reports are skipped (acceptable for achieving 3,000+ training pairs)
6. **Parsing variance:** Older articles (pre-2015) may use different HTML structure; scraper optimized for 2015-2025
7. **Section detection:** Not all articles have standard sections (Methods, Results, etc.); "Notes from the Field" and QuickStats use different formats

### Model Limitations

1. **No real-time data:** Model trained on historical articles; does not access current surveillance data
2. **No PHI:** Model should never be used with patient-identifiable information
3. **Hallucination risk:** Like all LLMs, may generate plausible-sounding but incorrect statements
4. **US-centric:** Communication style reflects US public health system

### Ethical Considerations

- **Misinformation risk:** Model outputs must be fact-checked by qualified professionals
- **Authority confusion:** Users must understand this is NOT official CDC guidance
- **Equity:** May not generalize well to low-resource or non-US settings

---

## Citation

If you use this dataset or model in your research, please cite:

```bibtex
@software{epibrief_mmwr_lm_2025,
  author = {Tegomoh, Bryan},
  title = {EpiBrief-MMWR-LM: A Public Health Language Model Trained on CDC MMWR Reports},
  year = {2025},
  url = {https://github.com/YourUsername/EpiBrief-MMWR-LM},
  note = {Independent research project. Not affiliated with CDC.}
}
```

**Data source citation:**
```
Centers for Disease Control and Prevention. Morbidity and Mortality Weekly Report (MMWR).
Available at: https://www.cdc.gov/mmwr/
```

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Data Source License

CDC MMWR articles are in the **public domain** as works of the U.S. federal government and may be reproduced without permission. However, CDC requests attribution.

**From CDC MMWR website:**
> "All material in the MMWR Series is in the public domain and may be used and reprinted without permission; citation as to source, however, is appreciated."

---

## Project Timeline and Milestones

### ✅ Completed (January 2025)
- [x] Phase 1: Data Collection (3,419 MMWR articles scraped)
- [x] Phase 2A: Enhanced Parser (100% success rate, 4,615 tables extracted)
- [x] Phase 2B: Training Pair Generation (11,632 high-quality pairs)
- [x] Model Selection Research (Llama 3.1 8B chosen based on medical benchmarks)
- [x] Training Script Development (Tinker API integration)
- [x] Comprehensive Documentation (8 detailed guides created)

### ⏳ In Progress (Current)
- [ ] Phase 2C: Dataset Split (ready to run `4_split_dataset.py`)
- [ ] Phase 3: Fine-Tuning (awaiting API key setup)

### 🔜 Upcoming (Next 1-2 weeks)
- [ ] Phase 4: Model Evaluation
  - Test on held-out MMWR articles
  - Compare to GPT-4/Claude baselines
  - Domain expert review
- [ ] Phase 5: Deployment
  - Download trained weights
  - Local inference setup
  - API deployment (FastAPI)

### 📊 Future Enhancements
- [ ] Multimodal expansion (Option 3: figures/graphs)
- [ ] Longer context window (full article analysis)
- [ ] Continuous training on new MMWRs
- [ ] Extension to WHO/ECDC reports

**Total Duration:** 2-3 weeks from conception to deployment

**Current Progress:** ~75% complete (data + preparation done, training ready)

---

## Contributing

This is currently a solo research project. Contributions, suggestions, and feedback are welcome!

**How to contribute:**
1. Open an issue to discuss proposed changes
2. Fork the repository
3. Create a feature branch
4. Submit a pull request

**Areas where contributions are especially valuable:**
- Improved parsing for edge cases (older MMWR formats)
- Additional training pair types
- Evaluation metrics for public health reasoning
- Extension to other surveillance bulletins (WHO, ECDC, etc.)

---

## Acknowledgments

- **CDC MMWR Team:** For decades of high-quality public health surveillance reporting
- **HuggingFace:** For model hosting infrastructure
- **Anthropic, Meta, Mistral:** For open-source base models

---

## Contact

**Bryan Tegomoh**
Public Health Researcher
Email: [Your Email]
LinkedIn: [Your LinkedIn]
GitHub: [Your GitHub]

---

## Frequently Asked Questions (FAQ)

### Q: Is this an official CDC project?
**A:** No. This is an independent research project using publicly available CDC data. It is not endorsed by or affiliated with the CDC.

### Q: Can I use this for clinical decision-making?
**A:** No. This model is for research and educational purposes only. It should never be used for individual patient diagnosis or treatment decisions.

### Q: How is this different from RAG (Retrieval-Augmented Generation)?
**A:** RAG retrieves and quotes existing text. This model is fine-tuned to internalize CDC's reasoning patterns, communication style, and public health framing. It learns *how* CDC thinks, not just *what* CDC says.

### Q: Can I train my own model with this dataset?
**A:** Yes! The dataset construction pipeline is fully open-source. Follow the instructions in this README to build your own dataset and fine-tune a model.

### Q: What if the scraper breaks due to CDC website changes?
**A:** The scripts are designed for the CDC MMWR website structure as of October 2025. If CDC redesigns their website, the scripts may need updates. Please open an issue if you encounter problems.

### Q: Can I extend this to other languages or countries?
**A:** Absolutely! The methodology can be adapted to:
- WHO Weekly Epidemiological Records (global)
- ECDC Surveillance Reports (Europe)
- Other national surveillance bulletins

Consider this a template for domain-specific public health LLMs.

### Q: How often should I update the dataset?
**A:** CDC MMWR publishes weekly. You can re-run the scraper periodically (e.g., quarterly or annually) to incorporate new articles. The scripts support incremental updates (they skip already-downloaded files).

---

## Version History

- **v1.0.0** (2025-10-28): Initial release
  - Complete dataset construction pipeline (scrape, parse, training pairs, validation)
  - 2015-2025 MMWR coverage
  - ~2,500-4,000 training pairs
  - Comprehensive documentation

---

**Built with dedication to improving public health communication through AI.**

*"Good data, good models, good outcomes."*
