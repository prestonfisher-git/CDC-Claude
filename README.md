# U.S. Births in 2025: CDC Provisional Natality Dashboard

A Streamlit dashboard for exploring 2025 provisional birth **counts** (not rates) by state,
month, and infant sex. Built for undergraduate business analytics students.

Data source: CDC, National Center for Health Statistics, National Vital Statistics System,
via [CDC WONDER](https://wonder.cdc.gov/natality.html). The figures are provisional and may be revised.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Push this folder to a GitHub repository (keep `data/` in the repo).
2. In Streamlit Community Cloud, choose **New app**, select the repo, and set the main file to `app.py`.
3. Deploy. The data path is built from the repo root, so no changes are needed.

## Project layout

```
app.py                  Entry point: page config, filters, KPIs, tabs
src/config.py           Paths, month order, colors, state abbreviations, source links
src/data_loader.py      Cached loading, validation checks, month ordering
src/filters.py          Sidebar widgets, Select All, Reset, filter summary, apply_filters
src/metrics.py          KPIs and aggregations (pure pandas, no Streamlit)
src/charts.py           One Plotly figure function per chart
src/components.py       Header, KPI cards, empty-state message
src/tabs/               One render() function per tab
data/                   Source CSV
.streamlit/config.toml  Theme
```

## Data checks (`src/data_loader.py`)

Errors stop the app with a message: missing columns, missing or non-numeric values, negative or
non-integer births, month names that disagree with month codes, unexpected infant-sex values,
duplicate state/month/sex rows, and states with no abbreviation (which would vanish from the map).
Warnings appear on the About tab: an incomplete state x month x sex grid, more than one year,
and any count of 9 or fewer (CDC asks that such counts not be published).

## Updating the data

Replace the CSV in `data/` (keep the same columns) and update `DATA_PATH` in `src/config.py` if the
file name changes.

## Design notes

- Count axes start at zero. The female-share chart uses a full 0 to 100% axis with a 50% reference line.
- Female and male use a colorblind-safe blue and orange pair (Okabe-Ito).
- The female-vs-male views ignore the infant-sex filter so they can always compare both sexes.
