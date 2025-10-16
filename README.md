## 🩺 Health-Data-Harmonizer

**Turning messy health data into clean, consistent science.**

### 💡 The Story

If you’ve ever worked with health data from multiple cohorts, you know the chaos.
The same variable might hide behind five different names, three encodings, and two units — sometimes all in the same study.

During my PhD research on brain aging and diabetes, I faced this daily.
What should’ve been a simple merge turned into hours of detective work:

- HbA1c could appear in % or mmol/mol

- Sex could be F/M, 1/2, or female/male

- Education could be measured in years or months

- Glucose, LDL, and HDL could switch between mg/dL and mmol/L

Each dataset needed its own fragile preprocessing pipeline — hard to reuse, harder to trust.

So I built something small, reproducible, and reliable:

**Health-Data-Harmonizer** — a tiny **Python library** you can call directly in your data pipeline to standardize and harmonize biomedical variables across cohorts.

It’s configuration-driven, transparent, and easy to extend.
You load your YAML config once, run .transform(), and get a clean, consistent DataFrame — ready for analysis or modeling.

Reproducible. Interpretable. Beautifully simple. ✨

### What It Does

Goal: Make healthcare cohorts consistent by standardizing a small, high-value set of variables:
age, sex, education_years, glucose_mmol_L, hba1c_percent, diabetes_status, hypertension, systolic_bp_mmHg, ldl_mmol_L, hdl_mmol_L
- ✅ Handles aliases (e.g. AGE, AgeYears, AGE_AT_SCAN)
- ✅ Normalizes units (e.g. glucose mg/dL → mmol/L, LDL/HDL mg/dL → mmol/L)
- ✅ Encodes categoricals (e.g. F/M or 2/1 → binary)
- ✅ Detects and converts education in months → years
- ✅ Adds range checks, imputation, and a detailed log of all transformations

### 🚀 Quick Start
```python
import pandas as pd
from health_data_harmonizer import Harmonizer

# Load harmonizer with default config
harm = Harmonizer.from_yaml("src/health_data_harmonizer/configs/default.yaml")

# Example messy dataset
df = pd.DataFrame({
    "AgeYears": [65, 72],
    "gender": [2, 1],
    "edu_months": [192, 156],
    "GLU": [108, 90],
    "hba1c": [53, 42],
    "dm_status": ["no", "controlled"]
})

# Harmonize it
clean, log = harm.transform(
    df,
    source_units={"glucose": "mg/dL", "hba1c": "mmol/mol"}
)

print(clean.head())
print(log)
```
### 🧩 Why It Matters

Healthcare data is powerful but messy.
Health-Data-Harmonizer helps you keep your preprocessing transparent, reusable, and reproducible —
so you can focus on science, not data wrangling.

### 👤 Author & Contact

**Mahboubeh Motaghi**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mahboubeh-motaghi-phd-58033759)
[![Google Scholar](https://img.shields.io/badge/Google%20Scholar-Profile-4285F4?logo=google-scholar&logoColor=white)](https://scholar.google.com/citations?user=CkXNH2MAAAAJ&hl=en)
[![Email](https://img.shields.io/badge/Email-Contact-informational?logo=gmail&logoColor=white)](mailto:mahboubeh.motaghi@gmail.com)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)