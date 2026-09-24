"""Reusable page pieces: header, KPI cards, and empty-state message."""
import pandas as pd
import streamlit as st

from src import config as C
from src.metrics import compute_kpis


def render_header() -> None:
    """Title, short explanation, source, and the two required notices."""
    st.title("U.S. Births in 2025: Geography, Month, and Infant Sex")
    st.write(
        "Explore how birth counts differ across states, months, and infant sex. "
        "Use the sidebar filters, then move between the tabs to see each view."
    )
    st.caption(
        "Source: CDC, National Center for Health Statistics, National Vital Statistics System. "
        f"Provisional natality data via [CDC WONDER]({C.CDC_WONDER_URL}). "
        "Births are counted by the mother's state of residence."
    )
    col_a, col_b = st.columns(2)
    with col_a:
        st.warning("**Provisional data.** These figures may be revised by CDC.", icon=":material/info:")
    with col_b:
        st.info(
            "**Birth counts, not birth rates.** Larger states have more births "
            "mainly because they have more people.",
            icon=":material/tag:",
        )


def render_kpis(df: pd.DataFrame) -> None:
    """Five headline numbers for the current selection."""
    k = compute_kpis(df)
    cols = st.columns(5)
    cols[0].metric("Total births", f"{k.total_births:,}", help="Sum of births in the current selection.")
    cols[1].metric("Geographies selected", f"{k.n_geographies:,}", help="States plus DC included in the selection.")
    cols[2].metric(
        "Average births per month", f"{k.avg_births_per_month:,.0f}",
        help="Total births divided by the number of selected months.",
    )
    cols[3].metric(
        "Highest geography", k.top_state,
        delta=f"{k.top_state_births:,} births", delta_color="off",
        help="Geography with the most births in the selection.",
    )
    cols[4].metric(
        "Highest month", k.top_month,
        delta=f"{k.top_month_births:,} births", delta_color="off",
        help="Month with the most births in the selection.",
    )


def render_empty_state() -> None:
    """Shown instead of charts when the filters match no rows."""
    st.warning(
        "No data matches the current filters. Select at least one geography and one month, "
        "or choose **Reset filters** in the sidebar."
    )
