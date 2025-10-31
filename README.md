# 🦠 EpiBrief-MMWR-LM

**A Specialized Language Model for CDC-Style Epidemiological Reasoning**

[![Live Demo](https://img.shields.io/badge/🤗_Live_Demo-blue?style=for-the-badge)](https://huggingface.co/spaces/BryanTegomoh/EpiBrief-MMWR-LM)
[![Model](https://img.shields.io/badge/🤗_Model-orange?style=for-the-badge)](https://huggingface.co/BryanTegomoh/EpiBrief-MMWR-LM)
[![Paper](https://img.shields.io/badge/📄_Paper-green?style=for-the-badge)](MANUSCRIPT_EpiBrief_MMWR_LM.md)
[![License](https://img.shields.io/badge/License-Apache_2.0-yellow?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://www.python.org/)

> Fine-tuned Llama 3.1 8B on 11,632 instruction-response pairs from 9 years of CDC's Morbidity and Mortality Weekly Reports (2016-2025) to teach AI systems epidemiological reasoning patterns.

**🚀 Try it now:** [Live Demo →](https://huggingface.co/spaces/BryanTegomoh/EpiBrief-MMWR-LM) | **📦 Download Model:** [HuggingFace Hub →](https://huggingface.co/BryanTegomoh/EpiBrief-MMWR-LM)

---

## 📊 What This Model Does

EpiBrief-MMWR-LM is a domain-specialized language model that learned how CDC epidemiologists think, analyze, and communicate about infectious disease outbreaks. Unlike generic medical AI, this system was trained exclusively on authoritative public health literature.

### Example Input/Output

**Input:**
```
During January-March 2024, 47 measles cases were identified in Minnesota.
Among cases, 42 (89%) were unvaccinated, 35 (74%) were children <5 years.
Index case had international travel. 18 hospitalizations (38%); no deaths.
```

**Model Output:**
```
Measles is a highly contagious vaccine-preventable viral disease. Increasing U.S.
measles cases have been driven by unvaccinated persons who are exposed while traveling
internationally. U.S. health officials should coordinate response activities to prevent
and limit the spread of measles, assess and improve vaccination coverage, and ensure
MMR vaccination for all eligible children and adults.
```

---

## 🎯 Key Capabilities

- ✅ **Executive Summaries** - Generate CDC-style "What is known/added/implications" summaries
- ✅ **Data Interpretation** - Transform surveillance tables into epidemiological narratives
- ✅ **Quantitative Reasoning** - Calculate rates, interpret trends, assess statistical significance
- ✅ **Outbreak Analysis** - Analyze disease patterns across demographics and time
- ✅ **Public Health Guidance** - Translate findings into actionable recommendations

---

## 🚀 Quick Start

### Try the Live Demo (No Installation)
**→ [huggingface.co/spaces/BryanTegomoh/EpiBrief-MMWR-LM](https://huggingface.co/spaces/BryanTegomoh/EpiBrief-MMWR-LM)**

### Use Pre-trained Model (Recommended)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

# Load base model
base_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B")

# Load EpiBrief LoRA adapter
model = PeftModel.from_pretrained(base_model, "BryanTegomoh/EpiBrief-MMWR-LM")

# Generate
prompt = "During January 2024, 47 measles cases were reported in Minnesota..."
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=400, temperature=0.7)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Run From Source

```bash
# Clone the repository
git clone https://github.com/BryanTegomoh/EpiBrief-MMWR-LM.git
cd EpiBrief-MMWR-LM

# Install dependencies
pip install -r requirements.txt

# Run test script
cd scripts
python test_model_NOW.py
```

---

## 🏗️ Model Architecture

| Component | Specification |
|-----------|--------------|
| **Base Model** | Meta-Llama 3.1 8B (base variant) |
| **Fine-tuning** | LoRA (rank 32, alpha 64) |
| **Training Data** | 11,632 instruction-response pairs |
| **Data Source** | CDC MMWR articles (2016-2025) |
| **Training Duration** | ~8 hours (distributed GPU) |
| **Parameters** | 8.03B total, ~256M trainable (3.2%) |

**Why Llama 3.1 8B?** Best medical reasoning performance (AMEGA score: 464.8 vs competitors at 300-400)

---

## 📁 Project Structure

```
EpiBrief-MMWR-LM/
├── scripts/
│   ├── 1_scrape_mmwr.py              # Web scraper (3,419 articles)
│   ├── 2_parse_articles_ENHANCED.py  # HTML parser with table reconstruction
│   ├── 3_generate_training_pairs.py  # Generate 11,632 training pairs
│   ├── test_model_NOW.py             # Inference testing
│   └── web_interface.py              # Gradio demo
│
├── training_data/
│   ├── training_pairs.jsonl          # Full dataset (11,632 pairs)
│   ├── train.jsonl                   # 90% split (10,469 pairs)
│   └── val.jsonl                     # 10% split (1,163 pairs)
│
├── models/epibrief-mmwr-lm-v1/       # Trained LoRA weights
├── docs/                             # Methodology documentation
├── MANUSCRIPT_EpiBrief_MMWR_LM.md    # Full research paper
└── README.md                         # This file
```

---

## 📊 Training Data Statistics

| Metric | Value |
|--------|-------|
| **MMWR Articles Collected** | 3,419 (2016-2025) |
| **Tables Extracted** | 4,615 with smart parsing |
| **Training Pairs Generated** | 11,632 total |
| **Quantitative Focus** | 85% of training pairs |
| **Training Split** | 10,469 pairs (90%) |
| **Validation Split** | 1,163 pairs (10%) |

### Training Pair Distribution

```
Executive Summary           1,886 pairs (16%)
Data Interpretation         4,107 pairs (35%) ⭐ Quantitative
Comparative Analysis        3,361 pairs (29%) ⭐ Quantitative
Quantitative Reasoning      2,438 pairs (21%) ⭐ Quantitative
Public Health Implications  1,876 pairs (16%)
```

**Total quantitative training: 9,906 pairs (85%)**

---

## 🔬 Methodology

**Full details:** See [MANUSCRIPT_EpiBrief_MMWR_LM.md](MANUSCRIPT_EpiBrief_MMWR_LM.md)

### Phase 1: Data Collection
- Systematic web scraping of CDC MMWR archive
- 3,419 articles from 2016-2025
- Ethical scraping (1.5s delays, resume capability)

### Phase 2: Enhanced Parsing
- Smart table reconstruction (rowspan/colspan handling)
- CDC summary box extraction (1,903 articles)
- 100% parsing success rate

### Phase 3: Training Pair Generation
- 6 specialized task types
- Quality thresholds enforced
- 85% quantitative emphasis

### Phase 4: Model Training
- LoRA fine-tuning on Llama 3.1 8B
- 3 epochs, ~8 hours training
- Tinker API infrastructure

---

## 🎓 Use Cases

**For Public Health Professionals:**
- Draft preliminary outbreak summaries
- Interpret surveillance data quickly
- Generate evidence-based recommendations
- Learn CDC communication standards

**For Epidemiology Training:**
- Teach quantitative reasoning
- Demonstrate professional writing
- Practice outbreak analysis
- Study 9 years of MMWR precedents

**For AI Researchers:**
- Domain-specific fine-tuning methodology
- Quantitative reasoning in LLMs
- Evaluation frameworks for specialized AI

---

## ⚠️ Limitations & Responsible Use

**This is a research prototype. Important limitations:**

- ✋ **Not for clinical decisions** - Designed for surveillance, not patient care
- ✋ **Requires expert review** - All outputs must be verified by qualified epidemiologists
- ✋ **No real-time data** - Trained on historical articles (2016-2025)
- ✋ **US-centric** - Reflects CDC priorities and US public health context
- ✋ **Hallucination risk** - May generate plausible-sounding incorrect statements

**Recommended use:** Human-in-the-loop workflows only, with mandatory expert review.

---

## 📄 Citation

```bibtex
@software{tegomoh2025epibrief,
  author = {Tegomoh, Bryan},
  title = {EpiBrief-MMWR-LM: A Specialized Language Model for Epidemiological Reasoning},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/BryanTegomoh/EpiBrief-MMWR-LM}
}
```

---

## 👨‍⚕️ About the Author

**Bryan Tegomoh, MD, MPH**
Physician & Epidemiologist

Building AI systems that augment human expertise in public health. This project demonstrates how domain-specific fine-tuning creates specialized AI assistants that internalize professional reasoning patterns.

- 📧 bryan.tegomoh@berkeley.edu
- 💼 [LinkedIn](http://www.BryanTegomoh.com)
- 🌐 [PublicHealthAIHandbook.com](http://www.PublicHealthAIHandBook.com)

**Interested in AI for public health?** Let's collaborate!

---

## 🙏 Acknowledgments

- **CDC MMWR Team** - For maintaining the public MMWR archive
- **Meta AI** - For open-sourcing Llama 3.1
- **Thinking Machines (Tinker)** - For distributed training infrastructure
- **Hugging Face** - For hosting and demo infrastructure

---

## 📜 License

Apache License 2.0 - See [LICENSE](LICENSE)

**Training Data:** CDC MMWR articles (public domain)
**Model Weights:** Apache 2.0
**Code:** Apache 2.0

---

## 🔗 Links

- **🤗 Live Demo:** [huggingface.co/spaces/BryanTegomoh/EpiBrief-MMWR-LM](https://huggingface.co/spaces/BryanTegomoh/EpiBrief-MMWR-LM)
- **📦 Model Weights:** [huggingface.co/BryanTegomoh/EpiBrief-MMWR-LM](https://huggingface.co/BryanTegomoh/EpiBrief-MMWR-LM)
- **📄 Full Paper:** [MANUSCRIPT_EpiBrief_MMWR_LM.md](MANUSCRIPT_EpiBrief_MMWR_LM.md)
- **📚 Documentation:** [docs/](docs/)

---

**Built with ❤️ for public health**

*Last updated: October 2025*
