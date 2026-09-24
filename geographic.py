"""Geographic Analysis tab: ranking, map, and top/bottom comparison."""
import pandas as pd
import streamlit as st

from src import charts, config as C, metrics


def _pick_n(label: str, available: int, default: int, key: str, minimum: int = 1) -> int:
    """Slider for how many geographies to show; skipped when there is nothing to choose."""
    if available <= minimum:
        return available
    return st.slider(label, minimum, available, min(default, available), key=key)


def render(df: pd.DataFrame) -> None:
    totals = metrics.state_totals(df)

    st.plotly_chart(charts.choropleth(totals), width="stretch")
    st.caption(
        "Darker states have more births. Because these are counts, populous states look darker "
        "regardless of birth rates. Geographies outside the selection are left blank. "
        "The District of Columbia is too small to see on this map; find it in the ranking below."
    )

    st.subheader("Ranking")
    top_n = _pick_n("Geographies to show", len(totals), 15, "rank_n", minimum=min(5, len(totals)))
    st.plotly_chart(charts.state_ranking(totals, top_n), width="stretch")

    st.subheader("Highest and lowest")
    if len(totals) < 2:
        st.info("Select at least two geographies to compare the highest and lowest.")
        return
    n = _pick_n("Geographies in each group", len(totals) // 2, 5, "tb_n")
    top, bottom = metrics.top_and_bottom(totals, n)
    st.plotly_chart(charts.top_bottom(top, bottom), width="stretch")
    st.caption("Both panels use the same horizontal scale, so bar lengths can be compared directly.")
