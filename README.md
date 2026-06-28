# AB Test Engine

> Automated statistical experiment analyzer — upload any A/B test CSV and get instant significance testing, confidence intervals, effect sizes, and a plain-English business verdict.

**Live Demo → [ab-test-engine.streamlit.app](https://ab-test-engine.streamlit.app)**

<img width="2674" height="1650" alt="image" src="https://github.com/user-attachments/assets/6599e7af-0692-4407-8305-1297506108b9" />


---

## What It Does

Most teams run A/B tests but struggle to interpret the statistics correctly. This tool automates the entire analysis pipeline — from raw CSV to business decision — in seconds.

Upload any experiment dataset, map your columns, and get:
- Whether the result is statistically significant
- The confidence interval around the true difference
- The effect size (is it practically meaningful?)
- A plain-English verdict: **Ship It / Keep Control / Inconclusive**

---

## Live Example

Dataset: E-commerce landing page A/B test (294,478 users)

| Metric | Value |
|---|---|
| Control conversion rate | 12.04% |
| Treatment conversion rate | 11.89% |
| Absolute difference | -0.1480% |
| Relative difference | -1.23% |
| Z-statistic | -1.2369 |
| P-value | 0.2161 |
| Significant | No |
| Effect size (Cohen's h) | -0.0046 (Small) |
| 95% CI | [-0.38%, +0.09%] |
| **Verdict** | **Inconclusive — do not ship** |

---

## How It Works

### 1. Data Cleaning & Sanity Checks
Before any statistics, the pipeline validates the data:
- Removes mismatched rows (control users who saw the new page and vice versa)
- Removes duplicate user IDs to prevent inflated counts
- Validates that the conversion column contains only 0/1 values
- Checks group balance (control vs treatment split)

### 2. Two-Proportion Z-Test
Tests whether the difference in conversion rates between groups is statistically significant.

```
H0: conversion_control = conversion_treatment
H1: conversion_control ≠ conversion_treatment
```

The Z-statistic measures how many standard deviations the observed difference is from zero. The p-value tells you the probability of seeing this difference by chance alone.

### 3. Confidence Interval
A 95% confidence interval is computed around the true difference:

```
CI = diff ± 1.96 × SE
SE = sqrt((p1(1-p1)/n1) + (p2(1-p2)/n2))
```

If zero is inside the CI — the result is inconclusive. If zero is outside — the difference is real.

### 4. Effect Size (Cohen's h)
Statistical significance tells you if the difference is real. Effect size tells you if it matters.

```
Cohen's h = 2·arcsin(√p2) - 2·arcsin(√p1)
```

- h < 0.2 → Small effect
- h < 0.5 → Medium effect
- h > 0.5 → Large effect

### 5. Business Verdict
Three possible outcomes:

| Verdict | Condition | Action |
|---|---|---|
| 🚀 Ship It | p < α AND treatment > control | Roll out the new version |
| 🛑 Keep Control | p < α AND treatment < control | Revert, new version is worse |
| ⚠️ Inconclusive | p > α | Run longer or redesign |

---

## Works on Any A/B Test CSV

The tool is not hardcoded to one dataset. Upload any CSV with:
- A group column (control/treatment labels)
- A conversion column (0/1 binary)

Then map your columns in the UI and run the analysis.

---

## Tech Stack

| Layer | Tools |
|---|---|
| Data Processing | Python, Pandas, NumPy |
| Statistics | SciPy, Statsmodels, Pingouin |
| Visualisation | Plotly |
| Dashboard | Streamlit |
| Deployment | Streamlit Cloud |
| Version Control | Git, GitHub |

---

## Project Structure

```
ab-test-engine/
├── data/
│   ├── raw/                  ← original dataset
│   └── processed/            ← cleaned results
├── notebooks/
│   ├── 01_eda.ipynb          ← exploratory data analysis
│   └── 02_hypothesis_testing.ipynb  ← statistical testing
├── src/
│   └── app.py                ← Streamlit dashboard
├── requirements.txt
└── README.md
```

---

## Run Locally

```bash
git clone https://github.com/whoj1ngmu77/ab-test-engine.git
cd ab-test-engine
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd src
streamlit run app.py
```

---

## Dataset

**Kaggle A/B Testing Dataset** — real e-commerce experiment data with 294,478 user sessions.

→ [Download from Kaggle](https://www.kaggle.com/datasets/zhangluyuan/ab-testing)

**Columns:**
- `user_id` — unique user identifier
- `timestamp` — when the user visited
- `group` — control or treatment
- `landing_page` — old_page or new_page
- `converted` — did the user convert? (0 or 1)

---

## Key Concepts Covered

- Null and alternative hypothesis formulation
- Two-proportion Z-test for binary outcomes
- P-value interpretation and significance thresholds
- 95% confidence interval construction
- Cohen's h effect size for proportions
- Type I error (false positive) and alpha threshold
- Practical vs statistical significance
- Data sanity checks for A/B experiments

---

## Future Improvements

- Sample size calculator (pre-experiment power analysis)
- Daily conversion trend chart (novelty effect detection)
- Segmentation analysis (mobile vs desktop, country)
- Multiple testing correction (Bonferroni)
- Sequential testing for early stopping
- PDF export of test results

---

Built by **Gayathri Menon**
