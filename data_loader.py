"""Loading, validating, and preparing the natality data."""
from dataclasses import dataclass, field

import pandas as pd
import streamlit as st

from src import config as C


@dataclass
class ValidationReport:
    """Errors stop the app; warnings are shown but do not."""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_data(df: pd.DataFrame) -> ValidationReport:
    """Run data-quality checks on the raw CSV contents."""
    report = ValidationReport()

    missing = [c for c in C.REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        report.errors.append(f"Missing required columns: {', '.join(missing)}.")
        return report  # later checks depend on these columns

    if df[C.REQUIRED_COLUMNS].isna().any().any():
        n = int(df[C.REQUIRED_COLUMNS].isna().sum().sum())
        report.errors.append(f"Found {n} missing values in required columns.")
        return report

    births = pd.to_numeric(df[C.COL_BIRTHS], errors="coerce")
    if births.isna().any():
        report.errors.append("The births column contains non-numeric values.")
    else:
        if (births < 0).any():
            report.errors.append("The births column contains negative values.")
        if (births % 1 != 0).any():
            report.errors.append("The births column contains non-integer values.")
        small = int((births <= C.SUPPRESSION_THRESHOLD).sum())
        if small:
            report.warnings.append(
                f"{small} rows have {C.SUPPRESSION_THRESHOLD} or fewer births. "
                "CDC asks that such counts not be published."
            )

    # Month names must agree with month codes, and codes must be 1-12.
    codes = pd.to_numeric(df[C.COL_MONTH_CODE], errors="coerce")
    if codes.isna().any() or not codes.between(1, 12).all():
        report.errors.append("month_code has values outside 1-12.")
    else:
        expected = codes.astype(int).map(lambda m: C.MONTH_ORDER[m - 1])
        if (expected != df[C.COL_MONTH].astype(str).str.strip()).any():
            report.errors.append("Month names do not match month codes.")

    sexes = set(df[C.COL_SEX].astype(str).str.strip().unique())
    if not sexes <= C.EXPECTED_SEXES:
        report.errors.append(f"Unexpected infant-sex values: {sorted(sexes - C.EXPECTED_SEXES)}.")

    states = set(df[C.COL_STATE].astype(str).str.strip())
    unmapped = sorted(states - set(C.STATE_ABBREVIATIONS))
    if unmapped:
        report.errors.append(
            f"No abbreviation for: {', '.join(unmapped)}. They would be missing from the map."
        )

    key = [C.COL_STATE, C.COL_MONTH_CODE, C.COL_SEX]
    dupes = int(df.duplicated(key).sum())
    if dupes:
        report.errors.append(f"{dupes} duplicate state, month, and sex rows.")

    # Complete grid: every state x month x sex combination should appear once.
    expected_rows = len(states) * 12 * len(C.EXPECTED_SEXES)
    if len(df) != expected_rows:
        report.warnings.append(
            f"Expected {expected_rows:,} rows for a complete state x month x sex grid; "
            f"found {len(df):,}."
        )
    if len(states) != len(C.STATE_ABBREVIATIONS):
        report.warnings.append(
            f"Found {len(states)} geographies; expected {len(C.STATE_ABBREVIATIONS)}."
        )
    if df[C.COL_YEAR].nunique() != 1:
        report.warnings.append(f"Data span multiple years: {sorted(df[C.COL_YEAR].unique())}.")

    return report


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean text, add the state abbreviation, and enforce month order."""
    df = df.copy()
    for col in (C.COL_STATE, C.COL_MONTH, C.COL_SEX):
        df[col] = df[col].astype(str).str.strip()
    df[C.COL_ABBR] = df[C.COL_STATE].map(C.STATE_ABBREVIATIONS)
    df[C.COL_MONTH] = pd.Categorical(df[C.COL_MONTH], categories=C.MONTH_ORDER, ordered=True)
    df[C.COL_BIRTHS] = df[C.COL_BIRTHS].astype("int64")
    return df.sort_values([C.COL_MONTH_CODE, C.COL_STATE, C.COL_SEX]).reset_index(drop=True)


@st.cache_data(show_spinner="Loading data...")
def load_data() -> tuple[pd.DataFrame, ValidationReport]:
    """Read the CSV once and return (data, validation report)."""
    raw = pd.read_csv(C.DATA_PATH)
    report = validate_data(raw)
    if report.errors:
        return raw, report
    return prepare_data(raw), report
