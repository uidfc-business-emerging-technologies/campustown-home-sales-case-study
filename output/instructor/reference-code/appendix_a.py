"""Reproduce every Appendix A figure and stop on any difference.

The expected values are copied from data_description_sheet.md and
reference_figures.md in output/dataset/ (version 1.0, after the sales recorded
twice under two parcel numbers were removed). They replace the handoff's
Appendix A, which was copied from the first build's documents (35,529 rows).
They are the only hand-typed numbers in the reference code, and they exist only
to be checked against.
"""

import pandas as pd

from definitions import ADDRESS_KEY, half_up

EXPECTED_WHOLE = {
    "rows": 35_442,
    "columns": 34,
    "listing_id unique": True,
    "cities": 18,
    "states": 11,
    "counties": 20,
    "campus areas": 11,
    "median sale price": 410_000,
    "first sale date": "2023-03-27",
    "last sale date": "2026-03-25",
    "rows with list and contract date": 28_042,
    "rows with list and contract date (%)": 79.1,
    "median days on market": 11,
    "rows sharing a street address": 66,
    "addresses shared by more than one row": 16,
    "living_area_sqft equal to 0": 127,
    "home_type SINGLE_FAMILY": 35_263,
    "home_type HOME_TYPE_UNKNOWN": 177,
    "home_type CONDO": 2,
    "prices under $10,000": 40,
    "prices under $1,000": 4,
    "prices of $0": 1,
    "prices over $5,000,000": 31,
    "highest price": 81_510_000,
    "min miles_to_campus": 0.2,
    "max miles_to_campus": 15.1,
    "median miles_to_campus": 3.4,
}

# University: rows, median price, median $/sq ft, median days on market, median miles.
EXPECTED_BY_CAMPUS = {
    "University of Wisconsin-Madison": (5_706, 434_010, 249.16, 7, 4.8),
    "University of Florida": (5_629, 355_000, 203.24, 25, 4.4),
    "Purdue University": (4_616, 299_900, 168.24, 10, 3.8),
    "University of Illinois Urbana-Champaign": (3_664, 245_000, 150.30, 7, 2.8),
    "University of Michigan": (3_021, 571_000, 259.11, 7, 2.7),
    "The University of North Carolina at Chapel Hill": (3_016, 725_000, 280.25, 10, 3.8),
    "University of Georgia": (2_814, 370_000, 196.82, 27, 3.7),
    "University of Virginia": (2_775, 615_000, 270.03, 7, 3.4),
    "The University of Iowa": (1_909, 342_000, 175.91, 24, 2.2),
    "The Pennsylvania State University": (1_351, 430_000, 207.42, 8, 2.1),
    "University of California, Davis": (941, 889_000, 492.71, 11, 2.0),
}
CAMPUS_FIELDS = ["rows", "median price", "median $/sq ft", "median days on market", "median miles to campus"]


def whole_dataset(raw, df):
    """Whole-dataset figures. `raw` is the file as loaded, `df` has derived columns."""
    both_dates = df["list_date"].notna() & df["contract_date"].notna()
    shared = df[df["shared_address"]]
    home_types = df["home_type"].value_counts()
    price = df["sale_price"]
    return {
        "rows": len(raw),
        "columns": raw.shape[1],
        "listing_id unique": bool(raw["listing_id"].is_unique),
        "cities": df[["city", "state"]].drop_duplicates().shape[0],
        "states": df["state"].nunique(),
        "counties": df[["county", "state"]].drop_duplicates().shape[0],
        "campus areas": df["university"].nunique(),
        "median sale price": half_up(df["price"].median()),
        "first sale date": df["sale_date"].min().strftime("%Y-%m-%d"),
        "last sale date": df["sale_date"].max().strftime("%Y-%m-%d"),
        "rows with list and contract date": int(both_dates.sum()),
        "rows with list and contract date (%)": half_up(100 * both_dates.mean(), 1),
        "median days on market": half_up(df["days_on_market"].median()),
        "rows sharing a street address": len(shared),
        "addresses shared by more than one row": shared[ADDRESS_KEY].drop_duplicates().shape[0],
        "living_area_sqft equal to 0": int((df["living_area_sqft"] == 0).sum()),
        "home_type SINGLE_FAMILY": int(home_types.get("SINGLE_FAMILY", 0)),
        "home_type HOME_TYPE_UNKNOWN": int(home_types.get("HOME_TYPE_UNKNOWN", 0)),
        "home_type CONDO": int(home_types.get("CONDO", 0)),
        "prices under $10,000": int((price < 10_000).sum()),
        "prices under $1,000": int((price < 1_000).sum()),
        "prices of $0": int((price == 0).sum()),
        "prices over $5,000,000": int((price > 5_000_000).sum()),
        "highest price": int(price.max()),
        "min miles_to_campus": half_up(df["miles_to_campus"].min(), 1),
        "max miles_to_campus": half_up(df["miles_to_campus"].max(), 1),
        "median miles_to_campus": half_up(df["miles_to_campus"].median(), 1),
    }


def by_campus(df):
    """The by-campus table, unrounded, one row per university."""
    grouped = df.groupby("university")
    table = pd.DataFrame({
        "rows": grouped.size(),
        "median price": grouped["price"].median(),
        "median $/sq ft": grouped["price_per_sqft"].median(),
        "median days on market": grouped["days_on_market"].median(),
        "median miles to campus": grouped["miles_to_campus"].median(),
    })
    return table.sort_values("rows", ascending=False)


def check(raw, df):
    """Compare every figure with Appendix A. Returns (rows, failures)."""
    results = []
    actual = whole_dataset(raw, df)
    for name, expected in EXPECTED_WHOLE.items():
        results.append(("Whole dataset", name, expected, actual[name]))

    table = by_campus(df)
    digits = [0, 0, 2, 0, 1]
    for university, expected_values in EXPECTED_BY_CAMPUS.items():
        for field, nd, expected in zip(CAMPUS_FIELDS, digits, expected_values):
            value = table.loc[university, field] if university in table.index else None
            results.append((university, field, expected, half_up(value, nd)))

    extra = sorted(set(table.index) - set(EXPECTED_BY_CAMPUS))
    for university in extra:
        results.append((university, "unexpected campus area", None, university))

    frame = pd.DataFrame(results, columns=["group", "figure", "expected", "computed"])
    frame["match"] = frame["expected"] == frame["computed"]
    return frame, frame[~frame["match"]]
