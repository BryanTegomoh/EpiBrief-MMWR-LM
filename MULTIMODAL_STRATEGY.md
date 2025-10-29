# Multimodal Strategy for EpiBrief-MMWR-LM

## The Reality: MMWR Articles Are Inherently Multimodal

### What We Discovered
Every MMWR article contains:
- **Text content** (narrative, methods, results, discussion)
- **Tables** (epidemiological data, demographics, clinical characteristics)
- **Figures** (charts, graphs, maps, flowcharts)
- **Boxes** (definitions, surveillance criteria, key points)
- **Statistical data** (percentages, confidence intervals, p-values)
- **Geographic visualizations** (outbreak maps, jurisdiction-specific data)

Example from mm7436a1.html (Pediatric Influenza Encephalopathy):
- Figure: Organizational chart of case categorization
- Table: Demographics and clinical characteristics (109 patients)
- Box: Surveillance criteria definition
- Text: Narrative linking all visual elements together

## The Challenge: Current Approach Limitations

### What We're Missing with Text-Only Training:
1. **Quantitative relationships** - Tables show age distributions, mortality rates, geographic spread
2. **Visual patterns** - Figures reveal epidemic curves, cluster patterns, outbreak progression
3. **Structured data** - Boxes contain critical definitions and criteria
4. **Data interpretation** - The connection between "what the data shows" and "what it means"

### Example of Information Loss:
**Table shows:** "Among 109 IAE cases, median age = 5 years (IQR 3-10), 46% female, 52% non-Hispanic White"

**Text-only model learns:** "Children with IAE had median age 5 years"

**Missed context:** The distribution, demographic patterns, representativeness, subgroup analysis

## Strategic Options for This Project

### **Option 1: Text-Only Fine-Tuning** (Current Plan)
**What we extract:**
- Narrative sections (Abstract, Methods, Results, Discussion)
- Written interpretations of data
- Conclusions and recommendations

**Strengths:**
- Clean, straightforward pipeline
- Works with current Llama 3.1 8B architecture
- Fast to implement (2-3 hours)
- Proven approach for text generation

**Limitations:**
- Cannot generate tables/figures
- May miss quantitative nuances
- Cannot reason about visual data
- Limited to prose output

**Best for:** Generating narrative EpiBriefs that summarize findings in text

---

### **Option 2: Enhanced Text Extraction with Table Data**
**What we extract:**
- All text content (Option 1)
- **+ Parsed table data** (rows/columns → structured format)
- **+ Figure captions** (describing what charts show)
- **+ Box content** (definitions, criteria)

**Implementation:**
```python
# Example parsed table
{
  "table_caption": "Demographics of IAE cases",
  "data": {
    "total_cases": 109,
    "median_age": {"value": 5, "unit": "years", "IQR": "3-10"},
    "sex_distribution": {"female": 46, "male": 54, "unit": "percent"},
    "race_ethnicity": {"non_hispanic_white": 52, "other": 48}
  }
}
```

**Training pair example:**
```json
{
  "instruction": "Summarize the demographic characteristics of IAE patients from this table.",
  "input": "Table: Demographics of 109 IAE cases...[structured data]",
  "output": "Among 109 pediatric IAE cases, the median age was 5 years (IQR 3-10 years). Approximately half of patients were female (46%) and non-Hispanic White (52%). These demographics suggest IAE affects young children across demographic groups with relatively balanced distribution by sex."
}
```

**Strengths:**
- Model learns to interpret tabular data
- Can generate data-driven narratives
- Still uses text-only LLM architecture
- Richer training signal

**Additional work:**
- Table parsing logic (~4-6 hours)
- Figure caption extraction (~2 hours)
- More complex training pair generation (~2 hours)
- **Total:** +8-10 hours

**Best for:** Generating EpiBriefs that synthesize both narrative and quantitative data

---

### **Option 3: Future Multimodal Architecture** (Phase 3+)
**What we would use:**
- Vision-language models (Llama 3.2 Vision, GPT-4V, Claude 3.5 Sonnet)
- Image inputs (tables as images, figures, charts)
- Multimodal training pairs

**Training pair example:**
```json
{
  "instruction": "Analyze this epidemic curve and describe the outbreak pattern.",
  "image": "base64_encoded_figure_image",
  "output": "The epidemic curve shows a sharp rise in cases beginning in week 45, peaking at 23 cases in week 48, followed by gradual decline. This pattern is consistent with a point-source outbreak with secondary transmission."
}
```

**Strengths:**
- Can truly "see" and interpret visual data
- Generate both text and visual content
- Most complete CDC-style reasoning

**Challenges:**
- Requires vision-enabled LLM (larger, more expensive)
- Need to download/process images separately
- Training infrastructure more complex
- Significantly more compute resources

**Timeline:** 2-3 weeks additional work

**Best for:** Full CDC-style reports with generated tables/figures

---

## My Recommendation: Phased Approach

### **Phase 2A: Text-Only (START HERE)** ✅
- Complete current pipeline as planned
- Generate 7,000-10,000 text training pairs
- Fine-tune Llama 3.1 8B
- **Goal:** Prove concept with narrative generation
- **Timeline:** 2-3 hours

### **Phase 2B: Enhanced with Table Parsing** (NEXT)
- Add table extraction to parser
- Generate data-interpretation training pairs
- **Goal:** Model learns to synthesize quantitative data
- **Timeline:** +1-2 days

### **Phase 3: Multimodal (FUTURE)**
- Evaluate vision models
- Download figures/charts as images
- Build multimodal training dataset
- **Goal:** Full visual reasoning capability
- **Timeline:** 2-3 weeks

---

## What This Means for Your EpiBrief Vision

### Current Capability (Text-Only Model):
**Input:** "Summarize key findings from the latest measles outbreak data"

**Output:**
```
During January-March 2025, 145 measles cases were reported across 8 jurisdictions,
representing a 340% increase from the same period in 2024. Among cases with known
vaccination status, 89% were unvaccinated. Hospitalization rate was 31%, with
complications including pneumonia (18%) and encephalitis (2%). These findings
underscore the critical importance of maintaining high MMR vaccination coverage.
```

### Enhanced Capability (With Table Parsing):
**Input:** "Analyze demographic patterns in this measles outbreak"

**Output:**
```
The 145 measles cases disproportionately affected children aged 1-4 years (62%),
with median age 3 years (IQR 2-7). Geographic distribution showed clustering in
3 jurisdictions (Minnesota, New York, Washington) accounting for 78% of cases.
Unvaccinated individuals represented 89% of cases despite comprising only 5% of
the population, yielding a relative risk of 17.8 (95% CI: 12.4-25.6) for measles
among unvaccinated versus vaccinated individuals.
```

### Future Capability (Multimodal):
**Input:** "Create an EpiBrief with epidemic curve for this outbreak"

**Output:**
- Narrative summary (as above)
- **+ Generated epidemic curve chart**
- **+ Geographic distribution map**
- **+ Demographic breakdown table**

---

## Decision Point

**What do you want EpiBrief to do?**

1. **Generate narrative summaries** → Text-only is sufficient
2. **Interpret and discuss data** → Add table parsing
3. **Create full visual reports** → Need multimodal approach

**My recommendation:** Start with Option 1 (text-only), evaluate results, then enhance with table parsing (Option 2) if needed. This keeps momentum while building toward richer capabilities.

---

## Next Steps

Once you decide on the approach, I'll:
1. Update parsing script to match chosen strategy
2. Design training pair templates accordingly
3. Implement extraction logic
4. Generate and validate dataset
5. Prepare for model training (Phase 3)

**Question for you:** What level of sophistication do you need for the initial version? Are narrative summaries sufficient, or do you need quantitative reasoning from the start?
