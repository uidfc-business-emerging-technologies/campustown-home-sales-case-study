"""Build data/answers.json from the College-town home sales dataset.

Run from the repository root:

    pip install pandas
    python scripts/build_data.py

Every number on the site comes from the file this script writes. The definitions
below are the ones the case sets for Variation 2.
"""
import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "college_town_home_sales.csv"
OUT = ROOT / "data" / "answers.json"

MIN_PRICE = 1_000      # a valid sale is $1,000 or more
MIN_SQFT = 100         # price per square foot needs at least 100 sq ft
MIN_GROUP = 20         # groups under 20 sales show "fewer than 20 sales"
MAX_RISE = 0.05        # Question 3: a rise of up to 5% between bands still counts as falling overall
BANDS = [(0, 1, "Under 1 mile"), (1, 2, "1 to under 2 miles"), (2, 5, "2 to under 5 miles"),
         (5, 10, "5 to under 10 miles"), (10, float("inf"), "10 miles or more")]
WINDOW = ("2023-04-01", "2025-03-31")  # Question 4: homes listed in this window, inclusive
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]
ADDRESS = ["address_street", "city", "state", "zipcode"]

# Short names for charts. The full name stays in the tables.
SHORT = {
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


def rnd(x, digits=0):
    """Round half up (23.5 -> 24), the way the dataset's reference figures do."""
    q = Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP)
    return int(q) if digits == 0 else float(q)


def join(names):
    names = list(names)
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def load():
    df = pd.read_csv(SOURCE, dtype=str, keep_default_na=False, na_values=[""])
    for c in ["sale_price", "living_area_sqft", "tax_assessed_value", "miles_to_campus"]:
        df[c] = pd.to_numeric(df[c])
    for c in ["list_date", "contract_date", "sale_date"]:
        df[c] = pd.to_datetime(df[c], format="%Y-%m-%d")
    assert len(df) == 35_529 and df["listing_id"].is_unique
    df["valid"] = df["sale_price"] >= MIN_PRICE
    df["pps"] = (df["sale_price"] / df["living_area_sqft"]).where(df["valid"] & (df["living_area_sqft"] >= MIN_SQFT))
    df["dom"] = (df["contract_date"] - df["list_date"]).dt.days
    df["at_address"] = df.groupby(ADDRESS)["listing_id"].transform("size")
    return df


def build():
    df = load()
    areas = sorted(SHORT)  # full names, alphabetical

    campuses = []
    for u in SHORT:
        rows = df[df["university"] == u]
        campuses.append({"name": u, "short": SHORT[u], "towns": join(rows["city"].value_counts().index),
                         "state": rows["state"].iloc[0], "rows": len(rows)})

    # Question 1. Price levels
    q1 = []
    for u in areas:
        v = df[(df["university"] == u) & df["valid"]]
        p = v[v["pps"].notna()]
        q1.append({"campus": SHORT[u], "valid_sales": len(v), "median_price": v["sale_price"].median(),
                   "pps_sales": len(p), "median_pps": p["pps"].median(), "median_sqft": p["living_area_sqft"].median()})
    for key, rank in [("median_price", "rank_price"), ("median_pps", "rank_pps")]:
        for r in q1:
            r[rank] = 1 + sum(bool(o[key] > r[key]) for o in q1)
    q1.sort(key=lambda r: -r["median_price"])
    for r in q1:
        r["median_price"], r["median_pps"], r["median_sqft"] = rnd(r["median_price"]), rnd(r["median_pps"], 2), rnd(r["median_sqft"])
    q1 = [{k: r[k] for k in ["campus", "valid_sales", "median_price", "pps_sales", "median_pps", "median_sqft",
                             "rank_price", "rank_pps"]} for r in q1]

    # Question 2. Speed
    q2 = []
    for u in areas:
        rows = df[df["university"] == u]
        d = rows["dom"].dropna()
        q2.append({"campus": SHORT[u], "rows": len(rows), "dom_sales": len(d), "median_dom": d.median(),
                   "missing_share": 1 - len(d) / len(rows)})
    q2.sort(key=lambda r: (r["median_dom"], r["missing_share"]))
    for r in q2:
        r["median_dom"], r["missing_share"] = float(rnd(r["median_dom"], 1)), rnd(r["missing_share"], 4)

    # Question 3. Distance bands
    q3 = {"bands": [b[2] for b in BANDS], "max_rise": MAX_RISE, "rows": []}
    for u in SHORT:
        p = df[(df["university"] == u) & df["pps"].notna()]
        cells, shown = [], {}
        for lo, hi, label in BANDS:
            s = p[(p["miles_to_campus"] >= lo) & (p["miles_to_campus"] < hi)]["pps"]
            cells.append({"n": len(s), "median_pps": rnd(s.median(), 2) if len(s) >= MIN_GROUP else None})
            if len(s) >= MIN_GROUP:
                shown[label] = s.median()
        values = list(shown.values())
        rises = [b / a - 1 for a, b in zip(values, values[1:])]
        if all(r < 0 for r in rises):
            pattern = "falls at every step"
        elif values[-1] < values[0] and max(rises) <= MAX_RISE:
            pattern = "falls overall"
        else:
            pattern = "does not fall"
        q3["rows"].append({"campus": SHORT[u], "pattern": pattern, "highest_band": max(shown, key=shown.get), "cells": cells})

    # Question 4. Month listed, homes listed in the window
    d = df[df["dom"].notna() & (df["list_date"] >= WINDOW[0]) & (df["list_date"] <= WINDOW[1])]
    q4 = {"window": list(WINDOW), "months": []}
    for m in range(1, 13):
        s = d[d["list_date"].dt.month == m]["dom"]
        q4["months"].append({"month": m, "name": MONTHS[m - 1], "n": len(s), "median_dom": float(rnd(s.median(), 1))})

    # Question 5. Assessed value to sale price
    a = df[df["valid"] & (df["tax_assessed_value"] > 0)].copy()
    a["ratio"] = a["tax_assessed_value"] / a["sale_price"]
    q5 = []
    for u in areas:
        s = a[a["university"] == u]
        q5.append({"campus": SHORT[u], "state": s["state"].iloc[0], "n": len(s), "median_ratio": s["ratio"].median()})
    q5.sort(key=lambda r: r["median_ratio"])
    for r in q5:
        r["median_ratio"] = rnd(r["median_ratio"], 3)

    # Question 6. Addresses with more than one sale
    multi, other = df[df["at_address"] > 1], df[df["at_address"] == 1]
    q6 = {"rows": []}
    for u in areas:
        m, o = multi[multi["university"] == u], other[other["university"] == u]
        q6["rows"].append({"campus": SHORT[u], "addresses": int(m.groupby(ADDRESS).ngroups), "sales": len(m),
                           "median_miles_multi": rnd(m["miles_to_campus"].median(), 2) if len(m) >= MIN_GROUP else None,
                           "median_miles_other": rnd(o["miles_to_campus"].median(), 2)})
    q6["rows"].sort(key=lambda r: -r["sales"])
    q6["total"] = {"addresses": int(multi.groupby(ADDRESS).ngroups), "sales": len(multi),
                   "median_miles_multi": rnd(multi["miles_to_campus"].median(), 2),
                   "median_miles_other": rnd(other["miles_to_campus"].median(), 2)}
    # Pairs at one address with prices within 1% and sale dates within 90 days: the build notes'
    # own test for one sale recorded twice (see "Repeated addresses" in the data notes).
    doubles = []
    for _, g in multi.groupby(ADDRESS):
        p, t = g["sale_price"], g["sale_date"]
        if len(g) == 2 and p.max() - p.min() <= 0.01 * p.max() and (t.max() - t.min()).days <= 90:
            doubles.append((g["university"].iloc[0], p.nunique() == 1))
    q6["likely_double_records"] = {
        "addresses": len(doubles), "rows": 2 * len(doubles), "same_price": sum(bool(same) for _, same in doubles),
        "by_campus": {SHORT[u]: n for u in areas if (n := sum(x == u for x, _ in doubles))},
    }

    return {
        "source": "College-town home sales dataset, version 1.0",
        "rows": len(df),
        "rules": {"min_price": MIN_PRICE, "min_sqft": MIN_SQFT, "min_group": MIN_GROUP},
        "campuses": campuses,
        "counts": {"valid_sales": int(df["valid"].sum()), "invalid_sales": int((~df["valid"]).sum()),
                   "zero_price_sales": int((df["sale_price"] == 0).sum()), "max_price": int(df["sale_price"].max()),
                   "pps_sales": int(df["pps"].notna().sum()), "dom_sales": int(df["dom"].notna().sum()),
                   "assessed_sales": len(a)},
        "sale_dates": [df["sale_date"].min().strftime("%Y-%m-%d"), df["sale_date"].max().strftime("%Y-%m-%d")],
        "q1": q1, "q2": q2, "q3": q3, "q4": q4, "q5": q5, "q6": q6,
    }


def main():
    OUT.write_text(json.dumps(build(), indent=1) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
