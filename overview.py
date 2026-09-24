"""Overview tab: monthly trend and female vs. male comparison."""
import pandas as pd
import streamlit as st

from src import charts, metrics


def render(df: pd.DataFrame, df_both_sexes: pd.DataFrame, sex_filter: str) -> None:
    """df respects every filter; df_both_sexes ignores the infant-sex filter."""
    left, right = st.columns(2)
    with left:
        st.plotly_chart(charts.monthly_trend(metrics.monthly_totals(df)), width="stretch")
        st.caption("Each point is the total for one month across the selected geographies.")
    with right:
        st.plotly_chart(charts.sex_comparison(metrics.monthly_by_sex(df_both_sexes)), width="stretch")
        if sex_filter == "Both":
            st.caption("Compares female and male births in each month.")
        else:
            st.caption("This comparison always shows both sexes, so it ignores the infant-sex filter.")
