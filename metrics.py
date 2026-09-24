"""Aggregations and KPIs. Pure pandas: no Streamlit imports, easy to test."""
from dataclasses import dataclass

import pandas as pd

from src import config as C


@dataclass
class Kpis:
    total_births: int
    n_geographies: int
    avg_births_per_month: float
    top_state: str
    top_state_births: int
    top_month: str
    top_month_births: int


def compute_kpis(df: pd.DataFrame) -> Kpis:
    """Headline numbers for the current selection. Expects a non-empty frame.

    Ties are broken deterministically: states alphabetically, months by
    calendar order.
    """
    states = state_totals(df)
    months = monthly_totals(df)
    n_months = df[C.COL_MONTH_CODE].nunique()
    total = int(df[C.COL_BIRTHS].sum())

    top_state = states.sort_values([C.COL_BIRTHS, C.COL_STATE], ascending=[False, True]).iloc[0]
    top_month = months.sort_values([C.COL_BIRTHS, C.COL_MONTH_CODE], ascending=[False, True]).iloc[0]

    return Kpis(
        total_births=total,
        n_geographies=df[C.COL_STATE].nunique(),
        avg_births_per_month=total / n_months,
        top_state=str(top_state[C.COL_STATE]),
        top_state_births=int(top_state[C.COL_BIRTHS]),
        top_month=str(top_month[C.COL_MONTH]),
        top_month_births=int(top_month[C.COL_BIRTHS]),
    )


def monthly_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Births per month in calendar order."""
    out = (
        df.groupby([C.COL_MONTH_CODE, C.COL_MONTH], observed=True)[C.COL_BIRTHS]
        .sum()
        .reset_index()
        .sort_values(C.COL_MONTH_CODE)
    )
    out[C.COL_MONTH] = out[C.COL_MONTH].astype(str)
    return out


def monthly_by_sex(df: pd.DataFrame) -> pd.DataFrame:
    """Births per month and infant sex in calendar order."""
    out = (
        df.groupby([C.COL_MONTH_CODE, C.COL_MONTH, C.COL_SEX], observed=True)[C.COL_BIRTHS]
        .sum()
        .reset_index()
        .sort_values([C.COL_MONTH_CODE, C.COL_SEX])
    )
    out[C.COL_MONTH] = out[C.COL_MONTH].astype(str)
    return out


def state_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Births per geography, largest first, with the map abbreviation."""
    out = (
        df.groupby([C.COL_STATE, C.COL_ABBR], observed=True)[C.COL_BIRTHS]
        .sum()
        .reset_index()
        .sort_values([C.COL_BIRTHS, C.COL_STATE], ascending=[False, True])
        .reset_index(drop=True)
    )
    return out


def state_month_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Rows = states (largest first), columns = months in calendar order."""
    pivot = df.pivot_table(
        index=C.COL_STATE, columns=C.COL_MONTH, values=C.COL_BIRTHS,
        aggfunc="sum", observed=True,
    )
    months = [m for m in C.MONTH_ORDER if m in pivot.columns]
    pivot = pivot[months]
    return pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).index]


def top_and_bottom(totals: pd.DataFrame, n: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """The n largest and n smallest geographies (no overlap if len >= 2n)."""
    top = totals.head(n)
    bottom = totals.tail(n).sort_values(C.COL_BIRTHS, ascending=True)
    return top, bottom


def female_share_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """Female, male, and total births per month plus the female share (%)."""
    wide = (
        df.pivot_table(
            index=[C.COL_MONTH_CODE, C.COL_MONTH], columns=C.COL_SEX,
            values=C.COL_BIRTHS, aggfunc="sum", observed=True,
        )
        .reset_index()
        .sort_values(C.COL_MONTH_CODE)
    )
    wide[C.COL_MONTH] = wide[C.COL_MONTH].astype(str)
    wide["Total"] = wide["Female"] + wide["Male"]
    wide["Female share (%)"] = (wide["Female"] / wide["Total"] * 100).round(2)
    return wide[[C.COL_MONTH, "Female", "Male", "Total", "Female share (%)"]]
