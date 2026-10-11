"""Common wrong answers to the Variation 2 questions, computed rather than described.

Each function returns a table with one row per campus area (or month), holding the
correct figure next to the figure a specific mistake produces, so a grader can
recognize the mistake from the number alone.
"""

import numpy as np
import pandas as pd

import variation2 as v2
from definitions import ADDRESS_KEY

MONTH_NAMES = v2.MONTHS


def _by_area(**columns):
    return pd.DataFrame(columns)


def q1(df):
    valid = df[df["valid_price"]]
    price = valid["sale_price"].astype(float)
    # In JavaScript, a blank or zero living area divides to Infinity, and the
    # median then includes those values.
    blank_as_zero = price / valid["living_area_sqft"].astype(float).fillna(0)
    return {
        "Median sale price": _by_area(**{
            "correct: median of valid sales": valid.groupby("university")["price"].median(),
            "mean instead of median": valid.groupby("university")["price"].mean(),
        }),
        "Median price per sq ft": _by_area(**{
            "correct: median of per-sale values": df.groupby("university")["price_per_sqft"].median(),
            "median price / median living area": valid.groupby("university")["price"].median()
            / valid.groupby("university")["living_area_sqft"].median(),
            "mean of per-sale values": df.groupby("university")["price_per_sqft"].mean(),
            "no area floor, blank or 0 sq ft divided as 0": blank_as_zero.groupby(valid["university"]).median(),
        }),
    }


def q2(df):
    blank_as_zero = df["days_on_market"].astype(float).fillna(0)
    to_sale = (df["sale_date"] - df["list_date"]).dt.days
    to_sale = to_sale.where(df["list_date"].notna() & df["sale_date"].notna())
    only_list_missing = df["list_date"].isna().groupby(df["university"]).mean()
    return {
        "Median days on market": _by_area(**{
            "correct: list_date to contract_date": df.groupby("university")["days_on_market"].median(),
            "measured to sale_date": to_sale.groupby(df["university"]).median(),
            "blanks treated as zero": blank_as_zero.groupby(df["university"]).median(),
            "mean instead of median": df.groupby("university")["days_on_market"].mean(),
        }),
        "Share missing days on market": _by_area(**{
            "correct: missing either date": 1 - df["days_on_market"].notna().groupby(df["university"]).mean(),
            "counting only a missing list_date": only_list_missing,
        }),
    }


def _small_cells(counts, medians):
    cells = counts.stack().to_frame("sales").join(medians.stack().to_frame("median that should not be shown"))
    return cells[(cells["sales"] > 0) & (cells["sales"] < v2.MIN_GROUP)]


def q3(df):
    counts, medians, shown = v2.q3_distance(df)
    rows = df[df["price_per_sqft"].notna()].assign(band=lambda d: v2.add_band(d))
    pooled = rows.groupby("band", observed=False)["price_per_sqft"].median().reindex(v2.BAND_LABELS)
    mean = rows.pivot_table(index="university", columns="band", values="price_per_sqft",
                            aggfunc="mean", observed=False).reindex(columns=v2.BAND_LABELS)
    edges = [0, 1, 2, 5, 10, np.inf]
    inclusive = pd.cut(rows["miles_to_campus"], bins=edges, labels=v2.BAND_LABELS, right=True, include_lowest=True)
    inclusive_medians = rows.groupby(["university", inclusive], observed=False)["price_per_sqft"].median().unstack()
    return {
        "All areas pooled, by band": pd.DataFrame({
            "sales": rows.groupby("band", observed=False).size().reindex(v2.BAND_LABELS),
            "median price per sq ft": pooled,
        }),
        "Small cells shown instead of suppressed": _small_cells(counts, medians),
        "Mean instead of median": mean,
        "Band edges that include the upper limit": inclusive_medians.reindex(columns=v2.BAND_LABELS),
    }


def q4(df):
    rows = df[df["days_on_market"].notna()]
    window = rows[v2.in_window(rows)]
    all_years = v2.q4_timing(df, window=False)["median days on market"]
    correct = v2.q4_timing(df, window=True)["median days on market"]

    def by_month(frame, date_col, values):
        month = frame[date_col].dt.month
        result = values.groupby(month).median()
        result.index = [MONTH_NAMES[m - 1] for m in result.index]
        return result

    to_sale = (window["sale_date"] - window["list_date"]).dt.days
    listed = df[df["list_date"].notna() & v2.in_window(df)]
    return {
        "Median days on market by month listed": pd.DataFrame({
            "correct: listed April 2023 to March 2025": correct,
            "all years combined (no window)": all_years,
            "month of sale_date instead of list_date": by_month(window, "sale_date", window["days_on_market"]),
            "measured to sale_date": by_month(window, "list_date", to_sale),
            "blanks treated as zero": by_month(listed, "list_date", listed["days_on_market"].astype(float).fillna(0)),
        }),
    }


def q5(df):
    rows = df[df["valid_price"] & (df["tax_assessed_value"] > 0)]
    ratio = rows["tax_assessed_value"] / rows["sale_price"]
    with_invalid = df[df["tax_assessed_value"] > 0]
    ratio_invalid = (with_invalid["tax_assessed_value"] / with_invalid["sale_price"].astype(float)).replace(np.inf, np.nan)
    return {
        "Median assessed value / sale price": _by_area(**{
            "correct: median of per-sale ratios": ratio.groupby(rows["university"]).median(),
            "mean of per-sale ratios": ratio.groupby(rows["university"]).mean(),
            "median assessed value / median sale price": rows.groupby("university")["tax_assessed_value"].median()
            / rows.groupby("university")["sale_price"].median(),
            "ratio inverted (sale price / assessed value)": (1 / ratio).groupby(rows["university"]).median(),
            "mean including sales under $1,000": ratio_invalid.groupby(with_invalid["university"]).mean(),
        }),
    }


def q6(df):
    def summary(frame, key):
        sizes = frame.groupby(key)["listing_id"].transform("size")
        repeated = frame[sizes > 1]
        return repeated.groupby("university").apply(lambda d: d[key].drop_duplicates().shape[0]), repeated.groupby("university").size()

    correct_addresses, correct_sales = summary(df, ADDRESS_KEY)
    street_addresses, street_sales = summary(df, ["address_street"])
    dedup = df.drop_duplicates(subset=ADDRESS_KEY)
    shared = df[df["shared_address"]]
    by_area = pd.DataFrame({
        "correct: addresses": correct_addresses,
        "correct: sales": correct_sales,
        "grouped by street name only: addresses": street_addresses,
        "grouped by street name only: sales": street_sales,
        "extra sales only (sales minus addresses)": correct_sales - correct_addresses,
    }).reindex(sorted(df["university"].unique())).fillna(0).astype(int)
    totals = pd.DataFrame({
        "addresses": [
            shared[ADDRESS_KEY].drop_duplicates().shape[0],
            df[df.groupby("address_street")["listing_id"].transform("size") > 1]["address_street"].nunique(),
            0,
        ],
        "sales": [
            len(shared),
            int((df.groupby("address_street")["listing_id"].transform("size") > 1).sum()),
            int((dedup.groupby(ADDRESS_KEY)["listing_id"].transform("size") > 1).sum()),
        ],
        "median miles to campus of those sales": [
            shared["miles_to_campus"].median(),
            df[df.groupby("address_street")["listing_id"].transform("size") > 1]["miles_to_campus"].median(),
            np.nan,
        ],
    }, index=["correct", "grouped by street name only", "after removing duplicate addresses"])
    return {
        "Repeated addresses by area": by_area,
        "Totals under each method": totals,
    }


ALL = {"Question 1": q1, "Question 2": q2, "Question 3": q3, "Question 4": q4, "Question 5": q5, "Question 6": q6}


def compute(df):
    return {question: fn(df) for question, fn in ALL.items()}
