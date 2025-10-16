import pandas as pd

from health_data_harmonizer import Harmonizer

harm = Harmonizer.from_yaml("src/health_data_harmonizer/configs/default.yaml")


def approx(a, b, tol=1e-6):
    return abs(a - b) < tol


def test_transform_basic_with_hba1c_mmolmol_and_binary_diabetes():
    """
    Dataset A:
      - AgeYears, gender (2=female, 1=male)
      - edu_months (months → years)
      - GLU in mg/dL (→ mmol/L)
      - HbA1c in mmol/mol (→ %)
      - dm_status contains 'no' and 'controlled' (→ 0 and 1)
      - LDL/HDL in mg/dL (→ mmol/L)
      - sbp (→ systolic_bp_mmHg)
    """
    df = pd.DataFrame(
        {
            "AgeYears": [65, 72],
            "gender": [2, 1],  # 2=female -> 0, 1=male -> 1
            "edu_months": [192, 156],  # months → years (16, 13)
            "GLU": [108, 90],  # mg/dL → mmol/L (6.0, 5.0)
            "hba1c": [53, 42],  # mmol/mol → % ((x+2.15)/10.929)
            "dm_status": ["no", "controlled"],  # binary -> 0, 1
            "htn": [0, 1],  # binary stays
            "sbp": [120, 142],  # → systolic_bp_mmHg
            "LDL_mg_dL": [130, 100],  # mg/dL → mmol/L
            "HDL_mg_dL": [50, 60],  # mg/dL → mmol/L
        }
    )

    clean, log = harm.transform(
        df,
        source_units={
            "glucose": "mg/dL",
            "hba1c": "mmol/mol",
            "ldl": "mg/dL",
            "hdl": "mg/dL",
        },
    )

    expected_cols = {
        "age",
        "sex",
        "education_years",
        "glucose_mmol_L",
        "hba1c_percent",
        "diabetes_status",
        "hypertension",
        "systolic_bp_mmHg",
        "ldl_mmol_L",
        "hdl_mmol_L",
    }
    assert expected_cols.issuperset(
        set(clean.columns)
    ), f"Missing: {expected_cols - set(clean.columns)}"

    # Sex encoding (2=female->0, 1=male->1)
    assert clean["sex"].tolist() == [0, 1]

    # Education months → years
    assert approx(clean["education_years"].iloc[0], 16.0)
    assert approx(clean["education_years"].iloc[1], 13.0)

    # Glucose mg/dL → mmol/L
    assert approx(clean["glucose_mmol_L"].iloc[0], 108 / 18.0)
    assert approx(clean["glucose_mmol_L"].iloc[1], 90 / 18.0)

    # HbA1c mmol/mol → %
    expected_a1c0 = (53 + 2.15) / 10.929
    expected_a1c1 = (42 + 2.15) / 10.929
    assert approx(clean["hba1c_percent"].iloc[0], expected_a1c0)
    assert approx(clean["hba1c_percent"].iloc[1], expected_a1c1)

    # Diabetes binary mapping
    assert clean["diabetes_status"].tolist() == [0, 1]

    # Systolic rename
    assert clean["systolic_bp_mmHg"].tolist() == [120, 142]

    # LDL/HDL mg/dL → mmol/L (×0.02586)
    assert approx(clean["ldl_mmol_L"].iloc[0], 130 * 0.02586)
    assert approx(clean["ldl_mmol_L"].iloc[1], 100 * 0.02586)
    assert approx(clean["hdl_mmol_L"].iloc[0], 50 * 0.02586)
    assert approx(clean["hdl_mmol_L"].iloc[1], 60 * 0.02586)

    # Log sanity
    assert any("glucose→mmol/L" in s for s in log["unit_conversions"])
    assert any("hba1c→%" in s for s in log["unit_conversions"])


def test_transform_aliases_percent_and_strings_binary_diabetes():
    """
    Dataset B:
      - AGE (alias), sex as 'F'/'M'
      - education already in years
      - glucose already in mmol/L (no conversion)
      - HbA1c already in % (no conversion)
      - diabetes contains 'uncontrolled' and 'no' → 1 and 0 (binary)
      - hypertension as true/false strings → 1/0
      - systolic alias 'systolic'
      - LDL/HDL already mmol/L (no conversion)
      - HbA1c alias: 'hemoglobin A1c'
    """
    df = pd.DataFrame(
        {
            "AGE": [61, 69],
            "sex": ["F", "M"],
            "education": [14, 12],
            "glucose": [6.1, 5.4],  # already mmol/L
            "hemoglobin A1c": [6.2, 5.7],  # already %
            "diabetes": ["uncontrolled", "no"],  # -> 1, 0
            "hypertension": ["true", "false"],  # -> 1, 0
            "systolic": [128, 118],
            "ldl": [2.8, 3.2],  # already mmol/L
            "hdl": [1.3, 1.1],  # already mmol/L
        }
    )

    clean, log = harm.transform(
        df,
        source_units={
            "glucose": "mmol/L",
            "hba1c": "%",
            "ldl": "mmol/L",
            "hdl": "mmol/L",
        },
    )

    # Aliases resolved
    assert "age" in clean.columns
    assert "hba1c_percent" in clean.columns
    assert "systolic_bp_mmHg" in clean.columns

    # Sex F/M -> 0/1
    assert clean["sex"].tolist() == [0, 1]

    # Diabetes 'uncontrolled'/'no' -> 1/0
    assert clean["diabetes_status"].tolist() == [1, 0]

    # Hypertension 'true'/'false' -> 1/0
    assert clean["hypertension"].tolist() == [1, 0]

    # Glucose stays (already mmol/L)
    assert approx(clean["glucose_mmol_L"].iloc[0], 6.1)
    assert approx(clean["glucose_mmol_L"].iloc[1], 5.4)

    # HbA1c stays (already %)
    assert approx(clean["hba1c_percent"].iloc[0], 6.2)
    assert approx(clean["hba1c_percent"].iloc[1], 5.7)

    # LDL/HDL already mmol/L
    assert approx(clean["ldl_mmol_L"].iloc[0], 2.8)
    assert approx(clean["ldl_mmol_L"].iloc[1], 3.2)
    assert approx(clean["hdl_mmol_L"].iloc[0], 1.3)
    assert approx(clean["hdl_mmol_L"].iloc[1], 1.1)

    # Education already years
    assert clean["education_years"].tolist() == [14, 12]
