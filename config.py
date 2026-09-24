"""Constants shared across the app: paths, ordering, colors, and lookups."""
from pathlib import Path

# Resolve paths relative to the repo root so they work locally and on
# Streamlit Community Cloud (where the working directory can differ).
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "Provisional_Natality_2025_CDC1.csv"

# Column names as they appear in the CSV.
COL_STATE = "state_of_residence"
COL_MONTH = "month"
COL_MONTH_CODE = "month_code"
COL_YEAR = "year_code"
COL_SEX = "sex_of_infant"
COL_BIRTHS = "births"
COL_ABBR = "state_abbr"  # added by the loader

REQUIRED_COLUMNS = [COL_STATE, COL_MONTH, COL_MONTH_CODE, COL_YEAR, COL_SEX, COL_BIRTHS]

# Calendar order; used to build an ordered categorical so charts never
# fall back to alphabetical month order.
MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

SEX_OPTIONS = ["Both", "Female", "Male"]
EXPECTED_SEXES = {"Female", "Male"}

# CDC's data-use terms say not to publish counts of 9 or fewer.
SUPPRESSION_THRESHOLD = 9

# Okabe-Ito colors: distinguishable with common forms of color blindness.
SEX_COLORS = {"Female": "#D55E00", "Male": "#0072B2"}
PRIMARY_COLOR = "#0072B2"
SEQUENTIAL_SCALE = "Blues"   # single-hue, perceptually ordered

# Source links (edit here if CDC moves them).
CDC_WONDER_URL = "https://wonder.cdc.gov/natality.html"
CDC_PROVISIONAL_HELP_URL = "https://wonder.cdc.gov/wonder/help/natality-provisional.html"

# 50 states + DC. The loader verifies every state in the data appears here,
# because a missing key would silently drop that state from the map.
STATE_ABBREVIATIONS = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME",
    "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
    "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
    "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
    "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX",
    "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}
