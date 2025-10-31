# EpiBrief-MMWR-LM

A Specialized Language Model for CDC-Style Epidemiological Reasoning

[Live Demo](https://huggingface.co/spaces/BryanTegomoh/EpiBrief-MMWR-LM) | [Model Weights](https://huggingface.co/BryanTegomoh/EpiBrief-MMWR-LM) | [License](LICENSE)

Fine-tuned Llama 3.1 8B on 11,632 instruction-response pairs from CDC's Morbidity and Mortality Weekly Reports (2016-2025) for epidemiological reasoning.

## Overview

EpiBrief-MMWR-LM is a domain-specialized language model trained on authoritative public health literature to analyze and communicate about infectious disease outbreaks in the style of CDC epidemiologists.

### Example

**Input:**
```
During January-March 2024, 47 measles cases were identified in Minnesota.
Among cases, 42 (89%) were unvaccinated, 35 (74%) were children <5 years.
Index case had international travel. 18 hospitalizations (38%); no deaths.
```

**Output:**
```
Measles is a highly contagious vaccine-preventable viral disease. Increasing U.S.
measles cases have been driven by unvaccinated persons who are exposed while traveling
internationally. U.S. health officials should coordinate response activities to prevent
and limit the spread of measles, assess and improve vaccination coverage, and ensure
MMR vaccination for all eligible children and adults.
```

## Capabilities

- Generate CDC-style executive summaries and outbreak reports
- Interpret surveillance data and calculate epidemiological metrics
- Analyze disease patterns across demographics and time periods
- Provide evidence-based public health recommendations

## Quick Start

### Live Demo
Try the model without installation: [huggingface.co/spaces/BryanTegomoh/EpiBrief-MMWR-LM](https://huggingface.co/spaces/BryanTegomoh/EpiBrief-MMWR-LM)

### Using the Pre-trained Model

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

# Load base model and adapter
base_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B")
model = PeftModel.from_pretrained(base_model, "BryanTegomoh/EpiBrief-MMWR-LM")

# Generate
prompt = "During January 2024, 47 measles cases were reported in Minnesota..."
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=400, temperature=0.7)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Running From Source

```bash
git clone https://github.com/BryanTegomoh/EpiBrief-MMWR-LM.git
cd EpiBrief-MMWR-LM
pip install -r requirements.txt
cd scripts
python test_model_NOW.py
```

## Model Architecture

| Component | Specification |
|-----------|--------------|
| Base Model | Meta-Llama 3.1 8B |
| Fine-tuning Method | LoRA (rank 32, alpha 64) |
| Training Data | 11,632 instruction-response pairs |
| Data Source | CDC MMWR articles (2016-2025) |
| Training Duration | ~8 hours (distributed GPU) |
| Trainable Parameters | ~256M (3.2% of total) |

## Training Data

| Metric | Value |
|--------|-------|
| MMWR Articles | 3,419 (2016-2025) |
| Tables Extracted | 4,615 |
| Training Pairs | 11,632 total |
| Quantitative Focus | 85% of pairs |

### Task Distribution
- Executive summaries: 1,886 pairs (16%)
- Data interpretation: 4,107 pairs (35%)
- Comparative analysis: 3,361 pairs (29%)
- Quantitative reasoning: 2,438 pairs (21%)
- Public health implications: 1,876 pairs (16%)

## Methodology

### Data Pipeline
1. **Collection**: Systematic scraping of CDC MMWR archive (3,419 articles, 2016-2025)
2. **Parsing**: HTML parsing with table reconstruction and CDC summary box extraction
3. **Training Pair Generation**: Creation of 11,632 instruction-response pairs across 6 task types
4. **Model Training**: LoRA fine-tuning on Llama 3.1 8B (3 epochs, Tinker API infrastructure)

Full methodology available in the accompanying research manuscript.

## Use Cases

**Public Health Practice**
- Draft preliminary outbreak summaries
- Interpret surveillance data
- Generate evidence-based recommendations

**Education and Training**
- Teach epidemiological reasoning
- Demonstrate professional scientific writing
- Study CDC communication patterns

**Research**
- Domain-specific fine-tuning methodology
- Quantitative reasoning in language models

## Limitations

This is a research prototype with important constraints:

- Not intended for clinical decision-making
- Requires expert review of all outputs
- Trained on historical data (2016-2025), not real-time
- US public health context and priorities
- May generate plausible but incorrect statements

**Recommended use**: Human-in-the-loop workflows with expert validation.

## Project Structure

```
EpiBrief-MMWR-LM/
├── scripts/
│   ├── 1_scrape_mmwr.py              # Data collection
│   ├── 2_parse_articles_ENHANCED.py  # HTML parsing
│   ├── 3_generate_training_pairs.py  # Training data generation
│   ├── test_model_NOW.py             # Inference testing
│   └── web_interface.py              # Gradio interface
├── training_data/                     # JSONL training files
├── models/epibrief-mmwr-lm-v1/       # Model weights
└── docs/                             # Documentation
```

## Citation

```bibtex
@software{tegomoh2025epibrief,
  author = {Tegomoh, Bryan},
  title = {EpiBrief-MMWR-LM: A Specialized Language Model for Epidemiological Reasoning},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/BryanTegomoh/EpiBrief-MMWR-LM}
}
```

## Author

**Bryan Tegomoh, MD, MPH**
Physician and Epidemiologist

Contact: bryan.tegomoh@berkeley.edu
[LinkedIn](http://www.BryanTegomoh.com) | [PublicHealthAIHandbook.com](http://www.PublicHealthAIHandBook.com)

## Acknowledgments

- CDC MMWR Team for maintaining the public archive
- Meta AI for open-sourcing Llama 3.1
- Thinking Machines (Tinker) for training infrastructure
- Hugging Face for model hosting

## License

Apache License 2.0 - See [LICENSE](LICENSE)

---

Last updated: October 2025
