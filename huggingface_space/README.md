---
title: EpiBrief-MMWR-LM
emoji: 🦠
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: apache-2.0
---

# EpiBrief-MMWR-LM: AI Epidemiologist

**Specialized language model trained on 11,632 CDC MMWR training pairs**

This AI assistant learned epidemiological reasoning from 9 years of CDC's Morbidity and Mortality Weekly Reports (2016-2025). It can:

- Generate CDC-style outbreak summaries
- Interpret surveillance data quantitatively
- Provide evidence-based public health recommendations
- Analyze epidemiological patterns across demographics and time

## Model Details

- **Base Model:** Meta-Llama 3.1 8B
- **Fine-tuning:** LoRA (rank 32, alpha 64)
- **Training Data:** 11,632 instruction-response pairs from CDC MMWR articles
- **Quantitative Focus:** 85% of training pairs emphasize numerical reasoning
- **Training Duration:** ~8 hours on distributed GPU infrastructure

## Developer

**Bryan Tegomoh, MD, MPH**
Physician & Epidemiologist
📧 bryan.tegomoh@berkeley.edu
🔗 [LinkedIn](http://www.BryanTegomoh.com) | [GitHub](https://github.com/BryanTegomoh/EpiBrief-MMWR-LM)

## Citation

```bibtex
@software{tegomoh2025epibrief,
  author = {Tegomoh, Bryan},
  title = {EpiBrief-MMWR-LM: A Specialized Language Model for Epidemiological Reasoning},
  year = {2025},
  url = {https://github.com/BryanTegomoh/EpiBrief-MMWR-LM}
}
```
