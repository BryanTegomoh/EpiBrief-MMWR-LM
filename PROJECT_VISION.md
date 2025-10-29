# EpiBrief-MMWR-LM: Project Vision & Strategy

## Core Mission
Build a specialized language model that learns CDC's epidemiological reasoning, writing style, and analytical patterns from the Morbidity and Mortality Weekly Report (MMWR) to generate high-quality epidemiological briefs (EpiBriefs).

---

## Why This Matters

### The Problem
- **Information Overload:** CDC publishes 250+ MMWR articles annually with complex epidemiological data
- **Synthesis Burden:** Public health professionals need rapid, accurate summaries
- **Pattern Recognition:** Understanding outbreak patterns requires domain expertise
- **Communication Challenges:** Translating technical findings into actionable insights

### The Solution
A fine-tuned language model that:
- **Understands** CDC's analytical frameworks and terminology
- **Synthesizes** epidemiological data into coherent narratives
- **Recognizes** patterns in outbreak reports
- **Communicates** findings in CDC's authoritative style
- **Generates** professional EpiBriefs on demand

---

## What Makes This Different

### Not RAG (Retrieval-Augmented Generation)
RAG systems retrieve and quote existing text. They don't truly understand CDC's reasoning patterns.

### Supervised Fine-Tuning Approach
We're teaching the model to:
- **Reason like CDC epidemiologists** - Pattern recognition, causality, risk assessment
- **Write like MMWR** - Concise, data-driven, action-oriented
- **Compress information** - Distill complex reports into key findings
- **Generate novel synthesis** - Create new EpiBriefs, not just quote existing ones

### The Training Signal
By fine-tuning on 3,419 MMWR articles (2016-2025):
- Model internalizes CDC's communication style
- Learns epidemiological reasoning patterns
- Understands public health framing
- Recognizes outbreak investigation structures

---

## Project Scope

### Phase 1: Dataset Construction ✅ COMPLETE
**Status:** 3,419 articles scraped (2016-2025)

**What we have:**
- Complete HTML articles with metadata
- All publication series (Weekly, Surveillance, Recommendations)
- Modern CDC communication style (last 9 years)
- Major epidemics covered: COVID-19, Zika, Ebola, Mpox, measles, influenza

**What we're building:**
- Parsed article structures (sections, metadata)
- 7,000-10,000 instruction/response training pairs
- Quality-validated training dataset in JSONL format

---

### Phase 2: Dataset Processing (CURRENT)
**Goal:** Convert 3,419 HTML articles → training dataset

**Steps:**
1. **Parse articles** - Extract sections, metadata, structured data
2. **Generate training pairs** - Create instruction/response examples
3. **Validate dataset** - Quality checks, statistics, balance

**Expected output:** `mmwr_training_pairs.jsonl` with 7,000-10,000 pairs

**Timeline:** 2-3 hours

---

### Phase 3: Model Training (FUTURE)
**Base model:** Llama 3.1 8B (or similar open-source LLM)

**Training approach:**
- LoRA (Low-Rank Adaptation) fine-tuning
- Supervised fine-tuning on instruction/response pairs
- Cloud GPU (RunPod, Lambda Labs, etc.)
- Evaluation on held-out test set

**Timeline:** 1-2 days

---

### Phase 4: Deployment & Application (FUTURE)
**Use cases:**
- Generate EpiBriefs from new outbreak data
- Summarize recent MMWR publications
- Draft initial outbreak reports
- Support epidemiological decision-making

---

## The Multimodal Reality

### What MMWR Articles Actually Contain

**Every article includes:**
- **Narrative text** (Abstract, Methods, Results, Discussion)
- **Tables** (demographics, clinical characteristics, outbreak data)
- **Figures** (epidemic curves, geographic maps, flowcharts)
- **Boxes** (definitions, surveillance criteria)
- **Statistical data** (confidence intervals, p-values, rates)

### Strategic Approach

#### **Phase 2A: Text-Only Training** (START HERE)
Extract and train on narrative sections only.

**Pros:**
- Clean, proven approach
- Fast implementation
- Works with standard LLM architecture
- Sufficient for narrative EpiBrief generation

**Output capability:**
"Generate a summary of key findings" → Coherent narrative synthesis

---

#### **Phase 2B: Enhanced with Structured Data** (NEXT)
Add table parsing and figure captions to training data.

**Pros:**
- Model learns to interpret quantitative data
- Can discuss demographic patterns, statistical findings
- Richer training signal
- Still uses text-only LLM

**Additional work:** +8-10 hours

**Output capability:**
"Analyze demographic patterns" → Data-driven interpretation with specific numbers

---

#### **Phase 3: True Multimodal** (FUTURE)
Use vision-language models to process images/charts.

**Pros:**
- Can "see" and interpret visual data
- Potentially generate charts/tables
- Most complete CDC-style reasoning

**Challenges:**
- Requires vision-enabled LLM (larger, more expensive)
- More complex infrastructure
- Significantly more development time

**Timeline:** 2-3 weeks

**Output capability:**
"Create an EpiBrief with epidemic curve" → Full report with generated visualizations

---

## Decision Framework

### What Do You Need EpiBrief to Do?

**Tier 1: Narrative Generation** (Text-only sufficient)
- Summarize outbreak reports
- Draft initial findings
- Generate executive summaries
- Produce public health communications

**Tier 2: Data Interpretation** (Add table parsing)
- Discuss demographic patterns
- Compare statistical findings
- Analyze temporal/geographic trends
- Synthesize quantitative evidence

**Tier 3: Visual Analysis** (Requires multimodal)
- Interpret epidemic curves
- Analyze geographic distributions
- Generate charts/tables
- Create complete visual reports

---

## My Strategic Recommendation

### Phased Development Path

**Phase 2A (Now):** Text-Only Fine-Tuning
- Prove the concept works
- Generate high-quality narrative EpiBriefs
- Fast time-to-results
- **Timeline:** 2-3 hours

**Phase 2B (After validation):** Add Table Parsing
- Enhance with quantitative reasoning
- Richer data interpretation
- Still manageable complexity
- **Timeline:** +1-2 days

**Phase 3 (Future):** Multimodal Architecture
- Evaluate vision models
- Full visual reasoning
- Complete CDC-style capabilities
- **Timeline:** 2-3 weeks

### Why This Approach?

1. **Rapid validation** - Prove value quickly with text-only
2. **Incremental enhancement** - Add capabilities based on actual needs
3. **Risk mitigation** - Don't over-invest before proving concept
4. **Learning path** - Each phase informs the next

---

## Success Metrics

### Phase 2 (Dataset) Success Criteria
- ✅ 3,419 articles successfully parsed (>95% success rate)
- ✅ 7,000-10,000 high-quality training pairs generated
- ✅ Diverse coverage (topics, time periods, report types)
- ✅ Balanced pair type distribution
- ✅ Quality validation metrics meet thresholds

### Phase 3 (Model) Success Criteria
- Model generates coherent, CDC-style narratives
- Factual accuracy on held-out test set
- Appropriate use of epidemiological terminology
- Proper report structure and formatting
- Actionable public health recommendations

### Phase 4 (Deployment) Success Criteria
- EpiBriefs useful to public health professionals
- Faster than manual summary generation
- Maintains scientific accuracy
- Proper uncertainty communication
- Valuable decision support tool

---

## Current Status & Next Steps

### ✅ Completed
- [x] Project scoped and planned
- [x] Scraper built with enumeration approach
- [x] 3,419 articles downloaded (2016-2025)
- [x] Dataset coverage verified (complete through Sept 2025)
- [x] Multimodal strategy analyzed

### 🔄 In Progress
- [ ] Decide on text-only vs. enhanced approach
- [ ] Review and test parsing script
- [ ] Generate training pairs
- [ ] Validate dataset quality

### ⏭️ Upcoming
- [ ] Fine-tune base model (Phase 3)
- [ ] Evaluate model performance
- [ ] Deploy for EpiBrief generation
- [ ] Consider multimodal enhancement

---

## Key Questions for You

1. **Primary use case:** What will you use EpiBrief for initially?
   - Quick outbreak summaries?
   - Teaching/training materials?
   - Decision support?
   - Public communication?

2. **Output sophistication:** What level of detail do you need?
   - Narrative summaries (text-only works)
   - Quantitative analysis (add table parsing)
   - Visual reports (need multimodal)

3. **Timeline priority:** What matters most?
   - Speed to first working model (text-only)
   - Comprehensive capability (multimodal, slower)
   - Balanced approach (enhanced text)

4. **Evaluation:** How will you judge success?
   - Subjective quality assessment
   - Comparison to human-written EpiBriefs
   - Usefulness in actual workflows
   - All of the above

---

## Bottom Line

This is an important project with real potential to support public health decision-making. The foundation is solid (3,419 articles is excellent), and we have clear paths forward.

**My recommendation:** Start with text-only training (Phase 2A) to prove the concept, then enhance based on your actual needs and the model's performance. This keeps momentum while building toward richer capabilities.

**Ready to proceed?** Let me know which approach aligns with your vision, and we'll move forward with dataset processing.
