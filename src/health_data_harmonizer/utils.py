import numpy as np
import pandas as pd


def coerce_numeric(s: pd.Series) -> pd.Series:
    return (
        s.astype(str)
        .str.replace(r"[^\d\.\-eE]", "", regex=True)
        .replace({"": np.nan})
        .astype(float)
    )


def map_alias(columns, aliases):
    cols = {c.lower(): c for c in columns}
    for cand in aliases:
        if cand.lower() in cols:
            return cols[cand.lower()]
    return None


def encode_cat(series: pd.Series, mapping: dict) -> pd.Series:
    """Robustly encode categoricals, normalizing yes/no/true/false and strings."""

    def norm(v):
        if pd.isna(v):
            return v
        if isinstance(v, str):
            s = v.strip().lower()
            if s in {"true", "false"}:
                return True if s == "true" else False
            if s in {"yes", "no"}:
                return True if s == "yes" else False
            return s
        return v

    m = {norm(k): v for k, v in mapping.items()}
    return series.map(lambda x: m.get(norm(x), x))


def guess_edu_is_months(s: pd.Series, threshold: int = 40) -> bool:
    """Heuristic: if max education value > threshold, treat as months."""
    try:
        arr = pd.to_numeric(s, errors="coerce").to_numpy()
        return np.nanmax(arr) > threshold
    except Exception:
        return False


def convert_glucose_to_mmol(s: pd.Series, src_unit: str | None) -> pd.Series:
    """Return glucose in mmol/L (if src is mg/dL divide by 18)."""
    if src_unit and src_unit.strip().lower() in {"mg/dl", "mgdl"}:
        return s / 18.0
    return s


def convert_chol_to_mmol(s: pd.Series, src_unit: str | None) -> pd.Series:
    """Return LDL/HDL in mmol/L: mmol/L = mg/dL * 0.02586."""
    if src_unit and src_unit.strip().lower() in {"mg/dl", "mgdl"}:
        return s * 0.02586
    return s


def convert_hba1c_to_percent(s: pd.Series, src_unit: str | None) -> pd.Series:
    """
    Return HbA1c in %.
    If src_unit is 'mmol/mol', convert using NGSP/IFCC relation:
      % = (mmol/mol + 2.15) / 10.929
    If src_unit is '%', return as-is.
    If src_unit is None, heuristic: median > 20 -> assume mmol/mol, else %.
    """
    if s is None:
        return s
    if src_unit:
        u = src_unit.strip().lower()
        if u in {"mmol/mol", "mmolmol", "mmol_per_mol"}:
            return (s + 2.15) / 10.929
        return s  # treat anything else as %
    med = pd.to_numeric(s, errors="coerce").median()
    if pd.notna(med) and med > 20:
        return (s + 2.15) / 10.929
    return s
