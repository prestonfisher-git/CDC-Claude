"""Monthly and Sex Analysis tab: state-by-month heatmap and female share."""
import pandas as pd
import streamlit as st

from src import charts, config as C, metrics


def render(df: pd.DataFrame, df_both_sexes: pd.DataFrame, sex_filter: str) -> None:
    st.plotly_chart(charts.heatmap(metrics.state_month_matrix(df)), width="stretch")
    st.caption("Each cell is one state in one month. Darker cells mean more births.")

    st.subheader("Female and male births by month")
    if sex_filter != "Both":
        st.caption("This section always shows both sexes, so it ignores the infant-sex filter.")

    share = metrics.female_share_by_month(df_both_sexes)
    left, right = st.columns([3, 2])
    with left:
        st.plotly_chart(charts.female_share_line(share), width="stretch")
        st.caption("The dashed line marks an even 50/50 split.")
    with right:
        st.dataframe(
            share,
            hide_index=True,
            width="stretch",
            column_config={
                C.COL_MONTH: "Month",
                "Female": st.column_config.NumberColumn(format="localized"),
                "Male": st.column_config.NumberColumn(format="localized"),
                "Total": st.column_config.NumberColumn(format="localized"),
                "Female share (%)": st.column_config.NumberColumn(format="%.2f%%"),
            },
        )
