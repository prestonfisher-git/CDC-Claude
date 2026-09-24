"""Data Table and Download tab."""
import pandas as pd
import streamlit as st

from src import config as C

_DISPLAY_COLS = [C.COL_STATE, C.COL_MONTH, C.COL_SEX, C.COL_BIRTHS]


def _search(df: pd.DataFrame, text: str) -> pd.DataFrame:
    """Case-insensitive search; every word typed must appear in the row's state, month, or sex."""
    words = text.lower().split()
    if not words:
        return df
    haystack = (
        df[C.COL_STATE].astype(str) + " " + df[C.COL_MONTH].astype(str) + " " + df[C.COL_SEX].astype(str)
    ).str.lower()
    mask = pd.Series(True, index=df.index)
    for word in words:
        mask &= haystack.str.contains(word, regex=False)
    return df[mask]


def render(df: pd.DataFrame) -> None:
    text = st.text_input(
        "Search the table", placeholder="Try a state, a month, or Female",
        help="Filters the rows below. Every word you type must match the state, month, or infant sex.",
    )
    shown = _search(df, text)[_DISPLAY_COLS]

    if shown.empty:
        st.warning("No rows match that search. Clear the search box to see all filtered rows.")
        return

    st.caption(f"{len(shown):,} rows, {int(shown[C.COL_BIRTHS].sum()):,} births")
    st.dataframe(
        shown,
        hide_index=True,
        width="stretch",
        column_config={
            C.COL_STATE: "State or geography",
            C.COL_MONTH: "Month",
            C.COL_SEX: "Infant sex",
            C.COL_BIRTHS: st.column_config.NumberColumn("Births", format="localized"),
        },
    )
    st.download_button(
        f"Download {len(shown):,} rows as CSV",
        data=shown.to_csv(index=False).encode("utf-8"),
        file_name="natality_2025_filtered.csv",
        mime="text/csv",
    )
