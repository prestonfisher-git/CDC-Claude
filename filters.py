"""Sidebar filters and the logic that applies them to the data."""
from dataclasses import dataclass

import pandas as pd
import streamlit as st

from src import config as C

# Session-state keys for each widget.
KEY_STATES, KEY_ALL_STATES = "f_states", "f_all_states"
KEY_MONTHS, KEY_ALL_MONTHS = "f_months", "f_all_months"
KEY_SEX = "f_sex"


@dataclass
class Filters:
    states: list[str]
    months: list[str]   # always in calendar order
    sex: str            # "Both", "Female", or "Male"
    n_states_total: int
    n_months_total: int


def _set_defaults(states: list[str], months: list[str]) -> None:
    """Select everything and reset the sex selector."""
    st.session_state[KEY_STATES] = list(states)
    st.session_state[KEY_ALL_STATES] = True
    st.session_state[KEY_MONTHS] = list(months)
    st.session_state[KEY_ALL_MONTHS] = True
    st.session_state[KEY_SEX] = "Both"


def _toggle_all(key_all: str, key_multi: str, options: list[str]) -> None:
    """Callback: the Select All checkbox selects or clears the multiselect."""
    st.session_state[key_multi] = list(options) if st.session_state[key_all] else []


def _sync_all(key_all: str, key_multi: str, options: list[str]) -> None:
    """Callback: keep the checkbox ticked only when every option is chosen."""
    st.session_state[key_all] = len(st.session_state[key_multi]) == len(options)


def _multiselect_with_all(label: str, options: list[str], key_multi: str, key_all: str, help_text: str) -> list[str]:
    st.checkbox(
        f"Select all ({len(options)})", key=key_all,
        on_change=_toggle_all, args=(key_all, key_multi, options),
    )
    return st.multiselect(
        label, options, key=key_multi, help=help_text,
        on_change=_sync_all, args=(key_all, key_multi, options),
    )


def render_sidebar(all_states: list[str], all_months: list[str]) -> Filters:
    """Draw the sidebar and return the current filter selections."""
    if KEY_STATES not in st.session_state:
        _set_defaults(all_states, all_months)

    st.sidebar.header("Filters")
    with st.sidebar:
        states = _multiselect_with_all(
            "State or geography", all_states, KEY_STATES, KEY_ALL_STATES,
            "Geographies are states plus the District of Columbia, by mother's residence.",
        )
        months = _multiselect_with_all(
            "Month", all_months, KEY_MONTHS, KEY_ALL_MONTHS,
            "Months of 2025 in which the births occurred.",
        )
        sex = st.radio(
            "Infant sex", C.SEX_OPTIONS, key=KEY_SEX, horizontal=True,
            help="Choose Both to compare female and male births.",
        )
        st.button(
            "Reset filters", on_click=_set_defaults, args=(all_states, all_months),
            width="stretch",
        )

    # Multiselect returns clicks in selection order; restore calendar order.
    months = [m for m in all_months if m in months]
    return Filters(states, months, sex, len(all_states), len(all_months))


def describe_filters(f: Filters) -> list[str]:
    """Plain-language lines summarizing what is currently selected."""
    if len(f.states) == f.n_states_total:
        geo = f"All {f.n_states_total} geographies"
    elif len(f.states) <= 3:
        geo = ", ".join(f.states) if f.states else "No geographies"
    else:
        geo = f"{len(f.states)} of {f.n_states_total} geographies"

    if len(f.months) == f.n_months_total:
        month = "All 12 months"
    elif len(f.months) <= 3:
        month = ", ".join(f.months) if f.months else "No months"
    else:
        month = f"{len(f.months)} of {f.n_months_total} months"

    sex = "Female and male births" if f.sex == "Both" else f"{f.sex} births only"
    return [geo, month, sex]


def render_filter_summary(f: Filters) -> None:
    """Show the active filters at the bottom of the sidebar."""
    st.sidebar.divider()
    st.sidebar.subheader("Active filters")
    for line in describe_filters(f):
        st.sidebar.markdown(f"- {line}")


def apply_filters(df: pd.DataFrame, f: Filters, include_sex: bool = True) -> pd.DataFrame:
    """Filter by geography and month, and optionally by infant sex."""
    mask = df[C.COL_STATE].isin(f.states) & df[C.COL_MONTH].isin(f.months)
    if include_sex and f.sex != "Both":
        mask &= df[C.COL_SEX] == f.sex
    return df[mask]
