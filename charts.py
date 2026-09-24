"""Plotly figure builders. Each function takes aggregated data and returns a figure.

Design rules applied everywhere: count axes start at zero, thousands
separators in hover text and ticks, colorblind-safe colors, no decoration.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src import config as C

_LAYOUT = dict(
    template="plotly_white",
    margin=dict(l=10, r=10, t=60, b=10),
    font=dict(size=13),
)
_TICKS = ",d"  # thousands separators on numeric axes


def _style(fig: go.Figure, title: str, height: int = 420) -> go.Figure:
    """Apply the shared layout and a left-aligned title."""
    fig.update_layout(title=dict(text=title, x=0, xanchor="left"), height=height, **_LAYOUT)
    return fig


def monthly_trend(monthly: pd.DataFrame) -> go.Figure:
    """Total births per month as a line; y-axis starts at zero."""
    fig = px.line(
        monthly, x=C.COL_MONTH, y=C.COL_BIRTHS, markers=True,
        category_orders={C.COL_MONTH: C.MONTH_ORDER},
        labels={C.COL_MONTH: "Month", C.COL_BIRTHS: "Births"},
        color_discrete_sequence=[C.PRIMARY_COLOR],
    )
    fig.update_traces(hovertemplate="%{x}: %{y:,} births<extra></extra>")
    fig.update_yaxes(rangemode="tozero", tickformat=_TICKS)
    return _style(fig, "Monthly births in the current selection")


def sex_comparison(monthly_sex: pd.DataFrame) -> go.Figure:
    """Female and male births side by side for each month."""
    fig = px.bar(
        monthly_sex, x=C.COL_MONTH, y=C.COL_BIRTHS, color=C.COL_SEX, barmode="group",
        category_orders={C.COL_MONTH: C.MONTH_ORDER, C.COL_SEX: ["Female", "Male"]},
        color_discrete_map=C.SEX_COLORS,
        labels={C.COL_MONTH: "Month", C.COL_BIRTHS: "Births", C.COL_SEX: "Infant sex"},
    )
    fig.update_traces(hovertemplate="%{x}, %{fullData.name}: %{y:,} births<extra></extra>")
    fig.update_yaxes(rangemode="tozero", tickformat=_TICKS)
    fig.update_layout(legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0))
    return _style(fig, "Female and male births by month")


def state_ranking(totals: pd.DataFrame, top_n: int) -> go.Figure:
    """Horizontal bars for the top_n geographies, largest at the top."""
    data = totals.head(top_n)
    fig = px.bar(
        data, x=C.COL_BIRTHS, y=C.COL_STATE, orientation="h",
        labels={C.COL_BIRTHS: "Births", C.COL_STATE: ""},
        color_discrete_sequence=[C.PRIMARY_COLOR],
    )
    fig.update_traces(hovertemplate="%{y}: %{x:,} births<extra></extra>")
    fig.update_yaxes(categoryorder="array", categoryarray=list(data[C.COL_STATE])[::-1])
    fig.update_xaxes(rangemode="tozero", tickformat=_TICKS)
    return _style(fig, f"Top {len(data)} geographies by births", height=max(360, 22 * len(data) + 120))


def choropleth(totals: pd.DataFrame) -> go.Figure:
    """US state map colored by total births (counts, not rates)."""
    fig = px.choropleth(
        totals, locations=C.COL_ABBR, locationmode="USA-states", scope="usa",
        color=C.COL_BIRTHS, hover_name=C.COL_STATE,
        hover_data={C.COL_ABBR: False, C.COL_BIRTHS: ":,"},
        color_continuous_scale=C.SEQUENTIAL_SCALE,
        labels={C.COL_BIRTHS: "Births"},
    )
    fig.update_coloraxes(colorbar=dict(title="Births", tickformat=_TICKS))
    fig.update_geos(showlakes=False)
    return _style(fig, "Births by state (counts, not rates)", height=480)


def heatmap(matrix: pd.DataFrame) -> go.Figure:
    """State-by-month grid of births; states sorted by total, months in order."""
    fig = go.Figure(go.Heatmap(
        z=matrix.values, x=list(matrix.columns), y=list(matrix.index),
        colorscale=C.SEQUENTIAL_SCALE, xgap=1, ygap=1,
        colorbar=dict(title="Births", tickformat=_TICKS),
        hovertemplate="%{y}, %{x}: %{z:,} births<extra></extra>",
    ))
    fig.update_yaxes(autorange="reversed", type="category")
    fig.update_xaxes(type="category", side="top")
    return _style(fig, "Births by state and month", height=max(400, 16 * len(matrix) + 140))


def top_bottom(top: pd.DataFrame, bottom: pd.DataFrame) -> go.Figure:
    """Highest and lowest geographies with identical x-ranges so bar lengths compare fairly."""
    n_top, n_bottom = len(top), len(bottom)
    fig = make_subplots(
        rows=1, cols=2, shared_xaxes=False, horizontal_spacing=0.18,
        subplot_titles=(f"Highest {n_top}", f"Lowest {n_bottom}"),
    )
    fig.add_trace(go.Bar(
        x=top[C.COL_BIRTHS], y=top[C.COL_STATE], orientation="h",
        marker_color=C.PRIMARY_COLOR, name="Highest",
        hovertemplate="%{y}: %{x:,} births<extra></extra>",
    ), row=1, col=1)
    fig.add_trace(go.Bar(
        x=bottom[C.COL_BIRTHS], y=bottom[C.COL_STATE], orientation="h",
        marker_color="#7A7A7A", name="Lowest",
        hovertemplate="%{y}: %{x:,} births<extra></extra>",
    ), row=1, col=2)

    # Same x-range on both panels so bar lengths are directly comparable.
    x_max = float(top[C.COL_BIRTHS].max()) * 1.05
    fig.update_xaxes(range=[0, x_max], tickformat=_TICKS, title_text="Births")
    fig.update_yaxes(autorange="reversed", row=1, col=1)
    fig.update_layout(showlegend=False)
    return _style(fig, "Highest and lowest geographies by births", height=max(380, 30 * max(n_top, n_bottom) + 140))


def female_share_line(share: pd.DataFrame) -> go.Figure:
    """Female share of births by month on a full 0-100% axis with a 50% reference."""
    fig = px.line(
        share, x=C.COL_MONTH, y="Female share (%)", markers=True,
        category_orders={C.COL_MONTH: C.MONTH_ORDER},
        labels={C.COL_MONTH: "Month"},
        color_discrete_sequence=[C.SEX_COLORS["Female"]],
    )
    fig.update_traces(hovertemplate="%{x}: %{y:.2f}% female<extra></extra>")
    fig.add_hline(y=50, line_dash="dash", line_color="#7A7A7A", annotation_text="50%")
    fig.update_yaxes(range=[0, 100], ticksuffix="%", title_text="Female share of births")
    return _style(fig, "Female share of births by month", height=360)
