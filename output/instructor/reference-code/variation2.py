"""Variation 2: the figures for each of the six questions, using the case's definitions.

Every function returns unrounded figures. Rounding happens only where a value is
written out, so the answer key, the workbook and the reference site agree.
"""

import numpy as np
import pandas as pd

from definitions import ADDRESS_KEY

MIN_GROUP = 20
BANDS = [
    (0, 1, "Under 1 mile"),
    (1, 2, "1 to under 2 miles"),
    (2, 5, "2 to under 5 miles"),
    (5, 10, "5 to under 10 miles"),
    (10, np.inf, "10 miles or more"),
]
BAND_LABELS = [label for _, _, label in BANDS]
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
# Question 4 uses homes listed in this window, inclusive (see the report).
LISTING_WINDOW = ("2023-04-01", "2025-03-31")
# Question 3: the largest rise between neighboring bands that still counts as "falls overall".
MAX_RISE = 0.05

SHORT_NAMES = {
    "University of Wisconsin-Madison": "UW-Madison",
    "University of Florida": "Florida",
    "Purdue University": "Purdue",
    "University of Illinois Urbana-Champaign": "Illinois",
    "University of Michigan": "Michigan",
    "The University of North Carolina at Chapel Hill": "UNC",
    "University of Virginia": "Virginia",
    "University of Georgia": "Georgia",
    "The University of Iowa": "Iowa",
    "The Pennsylvania State University": "Penn State",
    "University of California, Davis": "UC Davis",
}


def add_band(df):
    edges = [lo for lo, _, _ in BANDS] + [np.inf]
    return pd.cut(df["miles_to_campus"], bins=edges, labels=BAND_LABELS, right=False)


def in_window(df):
    start, end = LISTING_WINDOW
    return (df["list_date"] >= start) & (df["list_date"] <= end)


def q1_price_levels(df):
    valid = df[df["valid_price"]]
    by_area = pd.DataFrame({
        "valid sales": valid.groupby("university").size(),
        "median sale price": valid.groupby("university")["price"].median(),
        "sales with price per sq ft": df.groupby("university")["price_per_sqft"].count(),
        "median price per sq ft": df.groupby("university")["price_per_sqft"].median(),
    })
    by_area["rank by price"] = by_area["median sale price"].rank(ascending=False, method="min").astype(int)
    by_area["rank by price per sq ft"] = by_area["median price per sq ft"].rank(ascending=False, method="min").astype(int)
    return by_area.sort_values("median sale price", ascending=False)


def q2_speed(df):
    grouped = df.groupby("university")
    by_area = pd.DataFrame({
        "sales": grouped.size(),
        "sales with days on market": grouped["days_on_market"].count(),
        "median days on market": grouped["days_on_market"].median(),
    })
    by_area["share missing days on market"] = 1 - by_area["sales with days on market"] / by_area["sales"]
    return by_area.sort_values(["median days on market", "share missing days on market"])


def q3_distance(df):
    """Median price per sq ft by campus area and distance band, with sale counts."""
    rows = df[df["price_per_sqft"].notna()].assign(band=lambda d: add_band(d))
    counts = rows.pivot_table(index="university", columns="band", values="price_per_sqft",
                              aggfunc="size", observed=False).reindex(columns=BAND_LABELS).fillna(0).astype(int)
    medians = rows.pivot_table(index="university", columns="band", values="price_per_sqft",
                               aggfunc="median", observed=False).reindex(columns=BAND_LABELS)
    shown = medians.where(counts >= MIN_GROUP)
    return counts, medians, shown


def q3_pattern(shown):
    """Classify each area by how price per sq ft changes across its reportable bands.

    - falls at every step: each reportable band is below the one before it
    - falls overall: the farthest reportable band is below the nearest, with a rise
      of at most MAX_RISE between neighboring bands
    - does not fall: the farthest band is not below the nearest, or a step rises by
      more than MAX_RISE
    """
    rows = []
    for university, values in shown.iterrows():
        series = values.dropna().astype(float)
        steps = series.pct_change().dropna()
        max_rise = steps.max()
        if (steps < 0).all():
            pattern = "falls at every step"
        elif series.iloc[-1] < series.iloc[0] and max_rise <= MAX_RISE:
            pattern = "falls overall"
        else:
            pattern = "does not fall"
        rows.append({
            "university": university,
            "reportable bands": len(series),
            "nearest band": series.index[0],
            "nearest median": series.iloc[0],
            "farthest band": series.index[-1],
            "farthest median": series.iloc[-1],
            "highest band": series.idxmax(),
            "largest rise between neighboring bands": max_rise,
            "pattern": pattern,
        })
    return pd.DataFrame(rows).set_index("university")


def q4_timing(df, window=True):
    rows = df[df["days_on_market"].notna()]
    if window:
        rows = rows[in_window(rows)]
    month = rows["list_date"].dt.month
    by_month = rows.groupby(month)["days_on_market"].agg(["size", "median"])
    by_month.index = [MONTHS[m - 1] for m in by_month.index]
    by_month.columns = ["listings with days on market", "median days on market"]
    return by_month


def q5_assessment(df):
    rows = df[df["valid_price"] & (df["tax_assessed_value"] > 0)]
    ratio = rows["tax_assessed_value"] / rows["sale_price"]
    by_area = pd.DataFrame({
        "sales used": ratio.groupby(rows["university"]).size(),
        "median assessed / sale price": ratio.groupby(rows["university"]).median(),
        "state": rows.groupby("university")["state"].first(),
    })
    return by_area.sort_values("median assessed / sale price")


def q6_buildings(df):
    shared = df[df["shared_address"]]
    other = df[~df["shared_address"]]
    by_area = pd.DataFrame({
        "addresses with more than one sale": shared.groupby("university").apply(
            lambda d: d[ADDRESS_KEY].drop_duplicates().shape[0]),
        "sales at those addresses": shared.groupby("university").size(),
        "median miles, sales at those addresses": shared.groupby("university")["miles_to_campus"].median(),
        "median miles, all other sales": other.groupby("university")["miles_to_campus"].median(),
    }).reindex(sorted(df["university"].unique()))
    by_area[["addresses with more than one sale", "sales at those addresses"]] = (
        by_area[["addresses with more than one sale", "sales at those addresses"]].fillna(0).astype(int))
    total = {
        "addresses with more than one sale": shared[ADDRESS_KEY].drop_duplicates().shape[0],
        "sales at those addresses": len(shared),
        "median miles, sales at those addresses": float(shared["miles_to_campus"].median()),
        "median miles, all other sales": float(other["miles_to_campus"].median()),
    }
    return by_area.sort_values("sales at those addresses", ascending=False), total


def shared_address_groups(df):
    """Classify each repeated address with the build notes' own duplicate rule.

    The build treated two rows as one sale recorded twice when the parcel number
    matched, the prices were within 1% and the sale dates within 90 days. Here the
    parcel condition is dropped: a pair at one address that meets the price and
    date conditions is flagged as a likely double record.
    """
    shared = df[df["shared_address"]]
    groups = []
    for key, rows in shared.groupby(ADDRESS_KEY):
        prices = rows["sale_price"].astype(float)
        dates = rows["sale_date"]
        likely_double = (
            len(rows) == 2
            and prices.max() - prices.min() <= 0.01 * prices.max()
            and (dates.max() - dates.min()).days <= 90
        )
        groups.append({
            "university": rows["university"].iloc[0],
            "city": key[1],
            "sales": len(rows),
            "distinct parcel numbers": rows["parcel_number"].nunique(),
            "distinct prices": rows["sale_price"].nunique(),
            "days between first and last sale": (dates.max() - dates.min()).days,
            "rows with a list or contract date": int((rows["list_date"].notna() | rows["contract_date"].notna()).sum()),
            "rows with an assessed value": int(rows["tax_assessed_value"].notna().sum()),
            "newest year built": rows["year_built"].max(),
            "likely one sale recorded twice": likely_double,
        })
    return pd.DataFrame(groups)
