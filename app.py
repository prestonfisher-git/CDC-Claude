"""Streamlit entry point: streamlit run app.py"""
import streamlit as st

from src import config as C
from src.components import render_empty_state, render_header, render_kpis
from src.data_loader import load_data
from src.filters import apply_filters, render_filter_summary, render_sidebar
from src.tabs import about, data_table, geographic, monthly_sex, overview

st.set_page_config(
    page_title="U.S. Births 2025 (CDC provisional)",
    page_icon=":material/bar_chart:",
    layout="wide",
)


def main() -> None:
    render_header()

    # Stop with a clear message if the data fail a hard validation check.
    data, report = load_data()
    if report.errors:
        st.error("The data file failed validation, so the dashboard cannot load.")
        for message in report.errors:
            st.markdown(f"- {message}")
        st.stop()

    all_states = sorted(data[C.COL_STATE].unique())
    filters = render_sidebar(all_states, C.MONTH_ORDER)
    render_filter_summary(filters)

    # df respects every filter; df_both ignores infant sex so the
    # female-vs-male views can still compare both.
    df = apply_filters(data, filters)
    df_both = apply_filters(data, filters, include_sex=False)
    has_data = not df.empty

    if has_data:
        render_kpis(df)

    tab_names = ["Overview", "Geographic Analysis", "Monthly and Sex Analysis", "Data Table and Download", "About the Data"]
    t_overview, t_geo, t_monthly, t_table, t_about = st.tabs(tab_names)

    with t_overview:
        if has_data:
            overview.render(df, df_both, filters.sex)
        else:
            render_empty_state()
    with t_geo:
        if has_data:
            geographic.render(df)
        else:
            render_empty_state()
    with t_monthly:
        if has_data:
            monthly_sex.render(df, df_both, filters.sex)
        else:
            render_empty_state()
    with t_table:
        if has_data:
            data_table.render(df)
        else:
            render_empty_state()
    with t_about:
        about.render(data, report)


main()
