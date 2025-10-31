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

# EpiBrief-MMWR-LM

Specialized language model for CDC-style epidemiological reasoning, trained on 11,632 instruction-response pairs from CDC's Morbidity and Mortality Weekly Reports (2016-2025).

## Capabilities

- Generate outbreak summaries in CDC style
- Interpret surveillance data quantitatively
- Provide evidence-based public health recommendations
- Analyze epidemiological patterns

## Model Details

- **Base Model:** Meta-Llama 3.1 8B
- **Fine-tuning:** LoRA (rank 32, alpha 64)
- **Training Data:** 11,632 pairs from CDC MMWR articles
- **Quantitative Focus:** 85% of training emphasizes numerical reasoning
- **Training Duration:** ~8 hours on distributed GPU

## Notes

Model weights are stored in this Space via Git LFS. The main codebase is at [github.com/BryanTegomoh/EpiBrief-MMWR-LM](https://github.com/BryanTegomoh/EpiBrief-MMWR-LM).

## Author

**Bryan Tegomoh, MD, MPH**
Physician and Epidemiologist

[GitHub](https://github.com/BryanTegomoh/EpiBrief-MMWR-LM) | [LinkedIn](http://www.BryanTegomoh.com)

## Citation

```bibtex
@software{tegomoh2025epibrief,
  author = {Tegomoh, Bryan},
  title = {EpiBrief-MMWR-LM: A Specialized Language Model for Epidemiological Reasoning},
  year = {2025},
  url = {https://github.com/BryanTegomoh/EpiBrief-MMWR-LM}
}
```
