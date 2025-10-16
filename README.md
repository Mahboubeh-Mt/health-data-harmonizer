# health-data-harmonizer

**Goal:** make healthcare cohorts consistent by standardizing a small set of variables:  
`age, sex, education_years, glucose_mmol_L, diabetes_status, hypertension, systolic_bp_mmHg, ldl_mmol_L, hdl_mmol_L`.

- Handles **aliases** (different column names)
- Normalizes **units** (glucose mg/dL→mmol/L; LDL/HDL mg/dL→mmol/L)
- Encodes **categoricals** (incl. 2=female, 1=male)
- Simple **imputation** + **range flags**
- Returns a **log** of all changes

## Quickstart
```python
import pandas as pd
from health_data_harmonizer import Harmonizer

harm = Harmonizer.from_yaml("src/health_data_harmonizer/configs/default.yaml")
df = pd.read_csv("examples/data/dataset_a.csv")
clean, log = harm.transform(
    df,
    source_units={"glucose":"mg/dL","ldl":"mg/dL","hdl":"mg/dL"}
)
print(clean.head()); print(log)
```

