"""About the Data tab: source, definitions, limits, and validation results."""
import pandas as pd
import streamlit as st

from src import config as C
from src.data_loader import ValidationReport


def render(df: pd.DataFrame, report: ValidationReport) -> None:
    st.subheader("Source")
    st.markdown(
        "The data come from the CDC National Center for Health Statistics, National Vital Statistics "
        f"System, through [CDC WONDER]({C.CDC_WONDER_URL}). CDC describes the provisional data in its "
        f"[technical notes]({C.CDC_PROVISIONAL_HELP_URL}). "
        "Counts cover live births in the United States to U.S. residents, grouped by the mother's "
        "state of residence."
    )

    st.subheader("What each column means")
    st.table(pd.DataFrame({
        "Column": [C.COL_STATE, C.COL_MONTH, C.COL_MONTH_CODE, C.COL_YEAR, C.COL_SEX, C.COL_BIRTHS],
        "Meaning": [
            "Mother's state of residence (50 states plus the District of Columbia)",
            "Month of birth",
            "Month number, 1 (January) to 12 (December)",
            "Year of birth (2025)",
            "Female or Male",
            "Number of live births",
        ],
    }))

    st.subheader("How to read the figures")
    st.markdown(
        "- **Provisional.** Counts may change as CDC receives and edits more birth records.\n"
        "- **Counts, not rates.** A state with more people has more births. Comparing states fairly "
        "would need a rate, such as births per 1,000 women of childbearing age, which this file "
        "does not include.\n"
        "- **Month lengths differ.** February has fewer days, so it tends to have fewer births.\n"
        "- **Residence, not location.** A birth is assigned to the mother's home state, not the "
        "state where the hospital is."
    )

    st.subheader("Data checks")
    if not report.warnings:
        st.success(
            f"All checks passed. The file has {len(df):,} rows covering "
            f"{df[C.COL_STATE].nunique()} geographies, 12 months, and 2 infant-sex groups."
        )
    for message in report.warnings:
        st.warning(message)
