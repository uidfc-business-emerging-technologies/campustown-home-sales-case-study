"""Shared loading and definitions for the Campus Comps reference code.

Every figure in the instructor materials is computed with the rules in this
file, which match docs/reference_figures.md (dataset version 1.0):

- Valid sale: sale_price of $1,000 or more.
- Price per square foot: computed per sale, on valid sales with a living
  area of at least 100 sq ft, then the median is taken.
- Days on market: contract_date - list_date, on rows that have both dates.
- Medians, not means.
"""

from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pandas as pd

MIN_VALID_PRICE = 1_000
MIN_LIVING_AREA = 100
DATE_COLUMNS = ["list_date", "contract_date", "sale_date"]
FLOAT_COLUMNS = ["latitude", "longitude", "miles_to_campus", "baths", "tax_annual_amount"]
INT_COLUMNS = [
    "sale_price", "beds", "living_area_sqft", "lot_size_sqft", "year_built", "stories",
    "has_basement", "has_garage", "garage_spaces", "has_cooling", "has_heating",
    "has_fireplace", "tax_assessed_value",
]
ADDRESS_KEY = ["address_street", "city", "state", "zipcode"]

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA = REPO_ROOT / "output" / "students" / "data" / "college_town_home_sales.csv"


def load(path=DEFAULT_DATA):
    """Load the dataset from CSV or Parquet with the same types either way.

    Text columns stay text, so ZIP codes, FIPS codes and parcel numbers keep
    their leading zeros. Only an empty cell counts as missing.
    """
    path = Path(path)
    if path.suffix == ".csv":
        df = pd.read_csv(path, dtype=str, keep_default_na=False, na_values=[""])
    else:
        df = pd.read_parquet(path)
    for col in FLOAT_COLUMNS:
        df[col] = pd.to_numeric(df[col]).astype("float64")
    for col in INT_COLUMNS:
        df[col] = pd.to_numeric(df[col]).astype("Int64")
    for col in DATE_COLUMNS:
        df[col] = pd.to_datetime(df[col], format="%Y-%m-%d") if path.suffix == ".csv" else pd.to_datetime(df[col])
    return df


def add_derived(df):
    """Add the derived columns every analysis uses. Returns a copy."""
    df = df.copy()
    df["valid_price"] = df["sale_price"] >= MIN_VALID_PRICE
    df["price"] = df["sale_price"].where(df["valid_price"]).astype("Float64")
    usable_area = df["valid_price"] & (df["living_area_sqft"] >= MIN_LIVING_AREA)
    df["price_per_sqft"] = (df["sale_price"] / df["living_area_sqft"]).where(usable_area).astype("Float64")
    df["days_on_market"] = (df["contract_date"] - df["list_date"]).dt.days.astype("Int64")
    df["address_sales"] = df.groupby(ADDRESS_KEY)["listing_id"].transform("size")
    df["shared_address"] = df["address_sales"] > 1
    return df


def half_up(value, ndigits=0):
    """Round half away from zero, the way the published tables round."""
    if value is None or pd.isna(value):
        return None
    quantum = Decimal(1).scaleb(-ndigits)
    rounded = Decimal(repr(float(value))).quantize(quantum, rounding=ROUND_HALF_UP)
    return int(rounded) if ndigits == 0 else float(rounded)
