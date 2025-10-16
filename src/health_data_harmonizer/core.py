from __future__ import annotations
import yaml
import pandas as pd
from .utils import (
    coerce_numeric, map_alias, convert_glucose_to_mmol,
    convert_chol_to_mmol, encode_cat, guess_edu_is_months,
    convert_hba1c_to_percent,  # NEW
)

CANONICAL_ORDER = [
    "age","sex","education_years",
    "glucose_mmol_L","hba1c_percent",     # NEW
    "diabetes_status","hypertension",
    "systolic_bp_mmHg","ldl_mmol_L","hdl_mmol_L"
]

class Harmonizer:
    def __init__(self, config: dict):
        self.cfg = config

    @classmethod
    def from_yaml(cls, path: str) -> "Harmonizer":
        with open(path, "r") as f:
            cfg = yaml.safe_load(f)
        return cls(cfg)

    def transform(self, df: pd.DataFrame, source_units: dict | None = None):
        x = df.copy()
        log = {"renames":{}, "unit_conversions":[], "encodings":[], "imputations":[], "range_flags":[]}
        aliases = self.cfg["aliases"]
        enc = self.cfg["encodings"]
        ranges = self.cfg["ranges"]
        impute = self.cfg["impute"]
        edu_cfg = self.cfg["education"]

        # 1) alias → canonical
        rename_map = {}
        for canon, alist in aliases.items():
            col = map_alias(x.columns, alist)
            if col and col != canon:
                rename_map[col] = canon
        if rename_map:
            x = x.rename(columns=rename_map)
            log["renames"] = rename_map

        # 2) numeric coercion
        for c in ["age","education","glucose","hba1c","ldl","hdl","systolic_bp"]:  # + hba1c
            if c in x.columns:
                x[c] = coerce_numeric(x[c])

        # 3) units
        su = (source_units or {})
        if "glucose" in x.columns:
            x["glucose_mmol_L"] = convert_glucose_to_mmol(x["glucose"], su.get("glucose"))
            log["unit_conversions"].append("glucose→mmol/L")
        if "hba1c" in x.columns:  # NEW
            x["hba1c_percent"] = convert_hba1c_to_percent(x["hba1c"], su.get("hba1c"))
            log["unit_conversions"].append("hba1c→%")
        if "ldl" in x.columns:
            x["ldl_mmol_L"] = convert_chol_to_mmol(x["ldl"], su.get("ldl"))
            log["unit_conversions"].append("ldl→mmol/L")
        if "hdl" in x.columns:
            x["hdl_mmol_L"] = convert_chol_to_mmol(x["hdl"], su.get("hdl"))
            log["unit_conversions"].append("hdl→mmol/L")

        # 4) education → years
        if "education" in x.columns:
            if guess_edu_is_months(x["education"], edu_cfg.get("months_to_years_if_max_gt", 40)):
                x["education_years"] = x["education"] / 12.0
                log["unit_conversions"].append("education months→years")
            else:
                x["education_years"] = x["education"]

        # 5) categorical encodings
        if "sex" in x.columns:
            x["sex"] = encode_cat(x["sex"], enc["sex"])
        if "diabetes_status" in x.columns:
            x["diabetes_status"] = encode_cat(x["diabetes_status"], enc["diabetes_status"])
        if "hypertension" in x.columns:
            x["hypertension"] = encode_cat(x["hypertension"], enc["hypertension"])

        # 6) systolic label
        if "systolic_bp" in x.columns:
            x = x.rename(columns={"systolic_bp": "systolic_bp_mmHg"})

        # 7) simple imputations
        for col, how in impute.items():
            if col in x.columns:
                if how == "median":
                    x[col] = x[col].fillna(x[col].median())
                    log["imputations"].append(f"{col}=median")
                elif how == "mode":
                    modev = x[col].mode(dropna=True)
                    if not modev.empty:
                        x[col] = x[col].fillna(modev.iloc[0])
                        log["imputations"].append(f"{col}=mode")

        # 8) range flags
        for col, bounds in ranges.items():
            if col in x.columns:
                lo, hi = bounds
                bad_idx = x[(x[col] < lo) | (x[col] > hi)].index.tolist()
                if bad_idx:
                    log["range_flags"].append({col: bad_idx})

        keep = [c for c in CANONICAL_ORDER if c in x.columns]
        out = x[keep].copy()
        return out, log
