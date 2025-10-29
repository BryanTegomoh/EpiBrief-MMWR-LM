# MMWR HTML Structure Analysis
## Comprehensive Parsing Strategy for 3,419 Articles (2016-2025)

**Analysis Date:** October 29, 2025
**Analyst:** Claude (Sonnet 4.5)
**Purpose:** Design world-class parser for Option 2 (Enhanced Text + Tables)

---

## Key HTML Elements Identified

### 1. Article Metadata (Header)
```html
<title>Pediatric Influenza-Associated Encephalopathy...</title>
<meta name="citation_title" content="..."/>
<meta name="citation_author" content="Amara Fazal"/>
<meta name="citation_publication_date" content="2025"/>
<meta name="citation_volume" content="74"/>
<meta name="citation_doi" content="10.15585/mmwr.mm7436a1"/>
<meta property="cdc:first_published" content="September 25, 2025"/>
```

### 2. Summary Box (Critical for Training)
```html
<h3><strong>Summary</strong></h3>
<p><strong>What is already known about this topic?</strong></p>
<p>Influenza-associated encephalopathy (IAE) is a rare, severe neurologic complication...</p>

<p><strong>What is added by this report?</strong></p>
<p>During the high-severity 2024–25 influenza season, 109 U.S. pediatric IAE cases...</p>

<p><strong>What are the implications for public health practice?</strong></p>
<p>All children are at risk for severe neurologic complications...</p>
```

**CRITICAL:** This is gold for training pairs - pure CDC reasoning pattern!

### 3. Abstract
```html
<h2><a id="abstract" class="onThisPageAnchor" title="Abstract"></a>Abstract</h2>
<p>In January 2025, CDC received several reports...</p>
```

### 4. Main Sections
```html
<h2><a id="introduction" class="onThisPageAnchor" title="Introduction"></a>Introduction</h2>
<h2><a id="methods" class="onThisPageAnchor" title="Methods"></a>Methods</h2>
<h2><a id="results" class="onThisPageAnchor" title="Results"></a>Results</h2>
<h2><a id="discussion" class="onThisPageAnchor" title="Discussion"></a>Discussion</h2>
```

Sub-sections (H3):
```html
<h3 class="h3">Data Collection</h3>
<h3 class="h3">Case Categorization</h3>
<h3 class="h3">Characteristics of All Patients with Influenza-Associated Encephalopathy</h3>
<h3 class="h3">Limitations</h3>
<h3 class="h3">Implications for Public Health Practice</h3>
```

### 5. Tables (CRITICAL for Option 2)
```html
<table class="table table-bordered table-responsive">
<caption class="caption-top h4 text-black">
<h5><strong>TABLE. Characteristics of reported pediatric influenza-associated encephalopathy cases...</strong></h5>
</caption>
<thead>
  <tr>
    <th rowspan="2">Characteristic</th>
    <th colspan="2">All cases</th>
    <th colspan="2">ANE</th>
    <th colspan="2">Other IAE</th>
  </tr>
  <tr>
    <th>n/N*</th>
    <th>Column %</th>
    ...
  </tr>
</thead>
<tbody>
  <tr>
    <td>Total (row %)</td>
    <td>109</td>
    <td>100</td>
    <td>37</td>
    <td>34</td>
    <td>72</td>
    <td>66</td>
  </tr>
  <tr>
    <td>Median age, yrs (IQR)</td>
    <td>5 (3–10)</td>
    ...
  </tr>
</tbody>
</table>
```

**Key observations:**
- Headers use `rowspan` and `colspan` (need smart parsing)
- Data includes fractions (44/109), percentages (40), ranges (3-10)
- Some cells have `—` for N/A
- Complex multi-level headers

### 6. Figures
```html
<h5 class="h5"><a id="F1_down"></a>FIGURE. Categorization of cases...</h5>
<div class="mb-2">
  <img src="/mmwr/volumes/74/wr/figures/mm7436a1-F_Pediatric_influenza-large.gif"
       alt="The figure is an organizational chart..."
       title="Pediatric Influenza-Associated Encephalopathy..."/>
</div>
<p><b>Abbreviations:</b> ANE = acute necrotizing encephalopathy; IAE = influenza-associated encephalopathy.</p>
```

**Strategy:** Extract alt text, title, caption, abbreviations

### 7. Boxes (Definitions/Criteria)
```html
<h5 class="h5"><a id="B1_down"></a><b>BOX.</b> Required surveillance criteria...</h5>
<p>1. Patient age <18 years</p>
<p>2. Admitted to a U.S. acute care hospital...</p>
<p>3. Laboratory-confirmed influenza virus infection...</p>
<p>4. Documented neurologic abnormalities (meets one or more of the following criteria):</p>
<ul class="list-bullet">
  <li>Diagnosis of encephalopathy or encephalitis</li>
  <li>Neurologic signs or symptoms...</li>
</ul>
```

**Strategy:** Preserve structure (numbered lists, bullets)

### 8. References
```html
<h2><a id="References" class="onThisPageAnchor" title="References"></a>References</h2>
<ol>
  <li>Mizuguchi M. Influenza encephalopathy and related neuropsychiatric syndromes.
      Influenza Other Respir Viruses 2013;7(Suppl 3):67–71.
      <a href="http://doi.org/10.1111/irv.12177">https://doi.org/10.1111/irv.12177</a>
      <a href="http://www.ncbi.nlm.nih.gov/pubmed/24215384">PMID:24215384</a>
  </li>
</ol>
```

### 9. Author Affiliations
```html
<sup>1</sup>Influenza Division, National Center for Immunization and Respiratory Diseases, CDC;
<sup>2</sup>Epidemic Intelligence Service, CDC;
...
```

### 10. Footnotes
```html
<p class="Footnote">* These senior authors contributed equally to this report.</p>
<p class="Footnote"><sup>†</sup> Case report form questions covered demographics...</p>
```

---

## Critical Parsing Challenges

### Challenge 1: Table Complexity
- **Multi-level headers** with rowspan/colspan
- **Mixed data types**: integers, fractions, percentages, ranges, IQR
- **Missing data indicators**: `—`, `N/A`, blank cells
- **Nested subgroups**: Age groups, clinical characteristics categories

**Solution:** Smart table parser that:
1. Reconstructs header structure from rowspan/colspan
2. Maps each data cell to correct column headers
3. Preserves relationships (e.g., "44/109" → numerator 44, denominator 109, percentage 40)
4. Maintains row groupings and hierarchies

### Challenge 2: HTML Structure Variation
- **2016-2018**: May use older CDC template
- **2019-2022**: Mid-generation templates
- **2023-2025**: Current template (as seen in mm7436a1.html)

**Solution:** Flexible parsing with multiple strategies:
1. Try modern template first (2023-2025 structure)
2. Fall back to legacy patterns if needed
3. Logging to track which strategy worked

### Challenge 3: Content Encoding
- **Special characters**: `—` (em dash), `–` (en dash), `≥`, `&nbsp;`
- **HTML entities**: `&lt;`, `&gt;`, `&mdash;`, `&ndash;`
- **Unicode**: Various special medical/statistical symbols

**Solution:** Comprehensive entity decoding and normalization

### Challenge 4: Link Resolution
- Internal links: `<a href="#F1_down">Figure</a>`
- External links: DOIs, PubMed IDs
- PDF links: Related materials

**Solution:** Extract and preserve link context, convert to plain references in text

---

## Parsing Strategy for Option 2 (Enhanced Text + Tables)

### What We Extract:

#### 1. **Metadata** (Always)
```python
{
  "article_id": "mm7436a1",
  "doi": "10.15585/mmwr.mm7436a1",
  "title": "Pediatric Influenza-Associated Encephalopathy...",
  "authors": ["Amara Fazal", "Elizabeth J. Harker", ...],
  "publication_date": "2025-09-25",
  "volume": 74,
  "issue": 36,
  "pages": "556-564",
  "series": "weekly",
  "year": 2025
}
```

#### 2. **Summary Box** (Gold for training!)
```python
{
  "summary": {
    "what_is_known": "Influenza-associated encephalopathy (IAE) is a rare, severe neurologic complication of influenza.",
    "what_is_added": "During the high-severity 2024–25 influenza season, 109 U.S. pediatric IAE cases were identified; 55% of affected children were previously healthy...",
    "implications": "All children are at risk for severe neurologic complications of influenza. Annual influenza vaccination is recommended..."
  }
}
```

#### 3. **Abstract**
```python
{
  "abstract": "In January 2025, CDC received several reports of deaths among children aged <18 years with a severe form of influenza-associated encephalopathy (IAE) termed acute necrotizing encephalopathy (ANE)..."
}
```

#### 4. **Main Sections** (Full text)
```python
{
  "sections": {
    "introduction": {
      "text": "The 2024–25 influenza season was historically severe...",
      "subsections": []
    },
    "methods": {
      "text": "",
      "subsections": [
        {
          "title": "Data Collection",
          "text": "On February 28, 2025, CDC released a call for cases..."
        },
        {
          "title": "Case Categorization",
          "text": "Neuroimaging findings and discharge diagnoses underwent review..."
        }
      ]
    },
    "results": {
      "text": "CDC received 192 reports that met surveillance criteria...",
      "subsections": [
        {
          "title": "Characteristics of All Patients with Influenza-Associated Encephalopathy",
          "text": "Among the 109 IAE cases with available data, median patient age was 5 years (IQR = 3–10 years)..."
        }
      ]
    },
    "discussion": {
      "text": "During the 2024–25 influenza season, 109 cases of IAE in children were reported to CDC...",
      "subsections": [
        {
          "title": "Limitations",
          "text": "The findings in this report are subject to at least three limitations..."
        },
        {
          "title": "Implications for Public Health Practice",
          "text": "IAE is a serious neurologic complication of influenza..."
        }
      ]
    }
  }
}
```

#### 5. **Tables** (CRITICAL for Option 2!)
```python
{
  "tables": [
    {
      "id": "T1",
      "caption": "Characteristics of reported pediatric influenza-associated encephalopathy cases — United States, 2024–25 influenza season",
      "headers": [
        ["Characteristic", "All cases (n/N)", "All cases (Column %)", "ANE (n/N)", "ANE (Column %)", "Other IAE (n/N)", "Other IAE (Column %)"]
      ],
      "data": [
        {
          "Characteristic": "Total (row %)",
          "All_cases_n": 109,
          "All_cases_pct": 100,
          "ANE_n": 37,
          "ANE_pct": 34,
          "Other_IAE_n": 72,
          "Other_IAE_pct": 66
        },
        {
          "Characteristic": "Median age, yrs (IQR)",
          "All_cases_value": "5 (3–10)",
          "ANE_value": "4 (1–7)",
          "Other_IAE_value": "6 (4–10)"
        },
        {
          "Characteristic": "Age group: 0–4",
          "All_cases_fraction": "44/109",
          "All_cases_pct": 40,
          "ANE_fraction": "22/37",
          "ANE_pct": 59,
          "Other_IAE_fraction": "22/72",
          "Other_IAE_pct": 31
        }
        // ... more rows
      ],
      "raw_text_summary": "Table shows characteristics of 109 IAE cases, including 37 ANE and 72 other IAE. Median age was 5 years (IQR 3-10). Age distribution: 40% aged 0-4, 42% aged 5-11, 17% aged 12-17. Female sex: 46%. Previously healthy: 55%..."
    }
  ]
}
```

#### 6. **Figures** (Alt text, captions)
```python
{
  "figures": [
    {
      "id": "F1",
      "caption": "Categorization of cases of pediatric influenza-associated encephalopathy reported to CDC — United States, 2024–25 influenza season",
      "alt_text": "The figure is an organizational chart categorizing cases of pediatric influenza-associated encephalopathy reported to CDC in the United States during the 2024–25 influenza season.",
      "abbreviations": {"ANE": "acute necrotizing encephalopathy", "IAE": "influenza-associated encephalopathy"},
      "image_url": "/mmwr/volumes/74/wr/figures/mm7436a1-F_Pediatric_influenza-large.gif",
      "description_from_text": "Shows 192 total reports → 109 IAE (37 ANE + 72 other IAE) + 82 influenza-associated neurologic disease"
    }
  ]
}
```

#### 7. **Boxes** (Definitions, criteria)
```python
{
  "boxes": [
    {
      "id": "B1",
      "title": "Required surveillance criteria for pediatric influenza-associated encephalopathy investigation — United States, 2024–25 influenza season",
      "content": [
        "1. Patient age <18 years",
        "2. Admitted to a U.S. acute care hospital or pronounced dead in a U.S. emergency department during October 1, 2024–May 30, 2025",
        "3. Laboratory-confirmed influenza virus infection within 14 days preceding hospital evaluation, during hospitalization, or in respiratory specimens collected postmortem",
        "4. Documented neurologic abnormalities (meets one or more of the following criteria):",
        "   - Diagnosis of encephalopathy or encephalitis",
        "   - Neurologic signs or symptoms, including but not limited to:",
        "     - seizures",
        "     - altered mental status",
        "     - decreased level of consciousness",
        "     ...",
        "   - Neuroimaging abnormalities such as brain edema, brain inflammation, or brain lesions",
        "   - Electroencephalogram abnormalities (unspecified)",
        "   - Abnormal brain autopsy findings, if available, for children who died"
      ]
    }
  ]
}
```

#### 8. **References** (With DOIs/PMIDs)
```python
{
  "references": [
    {
      "number": 1,
      "text": "Mizuguchi M. Influenza encephalopathy and related neuropsychiatric syndromes. Influenza Other Respir Viruses 2013;7(Suppl 3):67–71.",
      "doi": "10.1111/irv.12177",
      "pmid": "24215384"
    }
  ]
}
```

---

## Training Pair Generation Strategy

### Type 1: Executive Summary
**Instruction:** "Summarize the key findings from this MMWR report in 2-3 sentences using CDC style."

**Input:** Title + Abstract (first 500 chars)

**Output:** Summary box "What is added" section (full text)

**Rationale:** Teaches compression and key finding identification

---

### Type 2: Data Interpretation (NEW for Option 2!)
**Instruction:** "Describe the demographic characteristics of the affected population based on this table."

**Input:** Table caption + structured table data

**Output:** Results section text that discusses the table

**Example:**
```
Input: Table - Characteristics of IAE cases
  Total: 109 (37 ANE, 72 other IAE)
  Median age: 5 years (IQR 3-10)
  Age 0-4: 44/109 (40%)
  Female: 49/107 (46%)
  Previously healthy: 60/109 (55%)

Output: "Among the 109 IAE cases with available data, median patient age was 5 years (IQR = 3–10 years). Approximately one half of patients were female (46%) and non-Hispanic White (52%). Approximately one half (55%) of patients were previously healthy with no underlying medical conditions."
```

**Rationale:** Teaches model to synthesize tabular data into narrative

---

### Type 3: Methods Extraction
**Instruction:** "Describe the surveillance and data collection methods used in this investigation."

**Input:** Title + Methods section

**Output:** Concise 2-3 sentence methods summary

---

### Type 4: Public Health Implications
**Instruction:** "What are the key public health implications and recommendations from this report?"

**Input:** Title + Discussion/Implications section

**Output:** Summary box "Implications" section

---

### Type 5: Comparative Analysis (Uses Tables!)
**Instruction:** "Compare the clinical outcomes between ANE and other IAE cases."

**Input:** Table data for both groups

**Output:** Discussion text that compares the groups

**Example:**
```
Input:
  ANE: 37 cases, ICU admission 100%, invasive ventilation 89%, mortality 41%
  Other IAE: 72 cases, ICU admission 61%, invasive ventilation 38%, mortality 8%

Output: "Patients reported to CDC with ANE had more severe illness than did those with other IAE; ANE patients had high mortality (41%) and rapid progression to death, and all patients had critical illness."
```

---

### Type 6: Quantitative Reasoning (NEW!)
**Instruction:** "Based on the vaccination data, calculate and interpret the vaccine coverage among eligible patients."

**Input:** Table row on vaccination status

**Output:** "Only 16% of children with IAE who were vaccination-eligible had received the 2024–25 influenza vaccine. This low vaccination rate among affected children highlights a missed prevention opportunity."

---

## Next Steps

1. **Build robust HTML parser** with BeautifulSoup4
2. **Implement table extraction** with smart header reconstruction
3. **Test on diverse sample** (10 articles: 2016, 2018, 2020, 2022, 2024 × 2 series each)
4. **Validate output quality** - Manual review of parsed JSON
5. **Run full parse** on 3,419 articles
6. **Generate training pairs** with 6 types above
7. **Quality validation** - Check distributions, detect issues

---

## Success Criteria

- ✅ **Parse rate >95%** - At least 3,248 of 3,419 articles successfully parsed
- ✅ **Section extraction >90%** - Abstract, Methods, Results, Discussion present
- ✅ **Table extraction >80%** - Complex tables correctly structured
- ✅ **Summary box >95%** - Critical training signal captured
- ✅ **No silent failures** - All errors logged, categorized, investigated

---

**This is not just a parser. This is the foundation of a world-class epidemiological AI.**
