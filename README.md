# EpiBrief-MMWR-LM

**A Public Health Language Model Trained on CDC MMWR Reports**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## Overview

**EpiBrief-MMWR-LM** is an experimental public health language model fine-tuned exclusively on historical CDC Morbidity and Mortality Weekly Report (MMWR) articles. This project aims to create an AI system that can communicate public health findings, outbreak investigations, and surveillance data using the authoritative style and structured reasoning patterns characteristic of CDC MMWR publications.

### Key Features

- **Specialized Training Corpus**: 10+ years (2015-2025) of CDC MMWR articles
- **Structured Dataset**: ~2,500-4,000 instruction/response training pairs
- **Domain Alignment**: Trained to internalize CDC communication patterns, not just retrieve text
- **Public Health Focus**: Outbreak investigations, surveillance methods, epidemiologic reasoning
- **Reproducible Pipeline**: Complete data collection, parsing, and training workflow

---

## ⚠️ Important Disclaimer

**This is an independent research project and is NOT an official CDC product.**

This model uses publicly available CDC MMWR reports as training data. It is not endorsed by, affiliated with, or representative of the Centers for Disease Control and Prevention (CDC) or any government agency. This is a research prototype for educational and experimental purposes.

---

## Project Structure

```
EpiBrief-MMWR-LM/
├── raw/                      # Downloaded HTML files (not in git)
│   ├── 2015/
│   ├── 2016/
│   └── ... → 2025/
├── parsed_json/              # Structured article metadata
├── training_data/            # Final JSONL training pairs
├── logs/                     # Processing logs
├── scripts/
│   ├── 1_scrape_mmwr.py     # Web scraper for CDC MMWR archive
│   ├── 2_parse_articles.py  # HTML parser to structured JSON
│   ├── 3_build_training_pairs.py  # Generate instruction/response pairs
│   └── 4_validate_dataset.py      # Dataset quality validation
├── requirements.txt          # Python dependencies
├── .gitignore
└── README.md
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

## Dataset Statistics (Expected)

| Metric | Value |
|--------|-------|
| Years covered | 2015-2025 (11 years) |
| Total articles | 800-1,200 (HTML only) |
| Training pairs | 3,000-5,000 |
| Avg pairs/article | ~4-6 |
| Top pathogens | COVID-19, influenza, measles, hepatitis, HIV |
| Report types | Outbreak investigations, surveillance summaries, recommendations |
| Temporal coverage | Varies (COVID-19 dominates 2020-2023) |

**Note:** Actual counts will vary based on HTML availability and parsing success rate.

---

## Model Training (Phase 2)

> **Note:** Model training is NOT included in this repository. This repo focuses on dataset construction.

After completing Phase 1 (dataset construction), you can proceed to Phase 2: Model Training using cloud GPU resources.

### Recommended Approach: LoRA Fine-Tuning

**Base Model:** Llama 3.1 8B Instruct
**Method:** LoRA (Low-Rank Adaptation)
**Hardware:** A100 40GB GPU (rented from RunPod/Lambda Labs)
**Training time:** 4-6 hours
**Cost:** $10-20 (one-time)

### Training Script (Not included - for reference)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model
from datasets import load_dataset

# Load base model
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3.1-8B-Instruct",
    load_in_4bit=True
)

# Configure LoRA
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05
)

model = get_peft_model(model, lora_config)

# Load your training data
dataset = load_dataset('json', data_files='training_data/epibrief_training.jsonl')

# Train (see training scripts in future releases)
```

**Expected model release:** HuggingFace Hub as `YourUsername/epibrief-llama3.1-8b`

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

## Roadmap

### ✅ Phase 1: Dataset Construction (Current)
- [x] Web scraper for MMWR archive
- [x] HTML parser to structured JSON
- [x] Training pair generator
- [x] Dataset validator
- [x] Documentation

### 🚧 Phase 2: Model Training (Next)
- [ ] LoRA fine-tuning script
- [ ] Model evaluation metrics
- [ ] Human evaluation protocol
- [ ] HuggingFace model card
- [ ] Release to HuggingFace Hub

### 📝 Phase 3: Publication & Dissemination
- [ ] arXiv preprint
- [ ] Public GitHub repo (EpiBrief - separate from this private repo)
- [ ] Demo notebook
- [ ] LinkedIn/Twitter announcement
- [ ] Submit to JMIR Public Health & Surveillance

### 🔬 Phase 4: Evaluation & Improvement
- [ ] Benchmark against GPT-4 on MMWR-style tasks
- [ ] Expert evaluation by CDC epidemiologists
- [ ] Iterative improvements based on feedback
- [ ] Extend to WHO Weekly Epidemiological Records

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
