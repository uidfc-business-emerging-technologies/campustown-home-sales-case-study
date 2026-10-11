"""Build data/answers.json from the College-town home sales dataset.

Run from the repository root:

    pip install pandas pyarrow
    python scripts/build_data.py

Every number on the site comes from the JSON file this script writes.
The definitions below are the ones set by the case (Variation 2).
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "college_town_home_sales.parquet"
OUT = ROOT / "data" / "answers.json"

MIN_PRICE = 1_000          # a valid sale is $1,000 or more
MIN_SQFT = 100             # price per square foot needs at least 100 sq ft
MIN_GROUP = 20             # groups under 20 sales show "fewer than 20 sales"
BANDS = [(0, 1, "Under 1 mi"), (1, 2, "1 to 2 mi"), (2, 5, "2 to 5 mi"),
         (5, 10, "5 to 10 mi"), (10, 1e9, "10+ mi")]

# Short labels for charts; the full name stays in the tables.
CAMPUS = {
    "University of Wisconsin-Madison": ("UW-Madison", "Madison, WI"),
    "University of Florida": ("Florida", "Gainesville, FL"),
    "Purdue University": ("Purdue", "West Lafayette, IN"),
    "University of Illinois Urbana-Champaign": ("Illinois", "Champaign-Urbana, IL"),
    "University of Michigan": ("Michigan", "Ann Arbor, MI"),
    "The University of North Carolina at Chapel Hill": ("UNC", "Chapel Hill, NC"),
    "University of Virginia": ("Virginia", "Charlottesville, VA"),
    "University of Georgia": ("Georgia", "Athens, GA"),
    "The University of Iowa": ("Iowa", "Iowa City, IA"),
    "The Pennsylvania State University": ("Penn State", "State College, PA"),
    "University of California, Davis": ("UC Davis", "Davis, CA"),
}


def med(s):
    s = s.dropna()
    return None if s.empty else float(s.median())


def main():
    df = pd.read_parquet(SOURCE)
    for c in ["list_date", "contract_date", "sale_date"]:
        df[c] = pd.to_datetime(df[c])

    # Sanity checks against the data description sheet.
    assert len(df) == 35_529, len(df)
    assert df["listing_id"].is_unique

    df["dom"] = (df["contract_date"] - df["list_date"]).dt.days
    valid = df[df["sale_price"] >= MIN_PRICE].copy()
    pps = valid[valid["living_area_sqft"] >= MIN_SQFT].copy()
    pps["pps"] = pps["sale_price"] / pps["living_area_sqft"]

    campuses = []
    for full, (short, town) in CAMPUS.items():
        campuses.append({"name": full, "short": short, "town": town,
                         "state": town[-2:], "rows": int((df["university"] == full).sum())})

    # Q1. Price levels
    q1 = []
    for c in campuses:
        v = valid[valid["university"] == c["name"]]
        p = pps[pps["university"] == c["name"]]
        q1.append({"campus": c["short"], "valid_sales": len(v),
                   "median_price": med(v["sale_price"]),
                   "pps_sales": len(p), "median_pps": round(med(p["pps"]), 2),
                   "median_sqft": med(p["living_area_sqft"])})
    for key, rank in [("median_price", "rank_price"), ("median_pps", "rank_pps")]:
        order = sorted(q1, key=lambda r: -r[key])
        for i, r in enumerate(order):
            r[rank] = i + 1

    # Q2. Speed
    q2 = []
    for c in campuses:
        rows = df[df["university"] == c["name"]]
        d = rows["dom"].dropna()
        q2.append({"campus": c["short"], "rows": len(rows), "dom_sales": len(d),
                   "median_dom": med(d), "missing_share": round(1 - len(d) / len(rows), 4)})

    # Q3. Distance bands
    def band_of(m):
        for lo, hi, label in BANDS:
            if lo <= m < hi:
                return label
    pps["band"] = pps["miles_to_campus"].map(band_of)
    q3 = {"bands": [b[2] for b in BANDS], "rows": []}
    for c in campuses:
        p = pps[pps["university"] == c["name"]]
        cells = []
        for label in q3["bands"]:
            s = p[p["band"] == label]["pps"]
            cells.append({"n": int(len(s)),
                          "median_pps": round(med(s), 2) if len(s) >= MIN_GROUP else None})
        q3["rows"].append({"campus": c["short"], "cells": cells})
    q3["all"] = []
    for label in q3["bands"]:
        s = pps[pps["band"] == label]["pps"]
        q3["all"].append({"n": int(len(s)), "median_pps": round(med(s), 2)})

    # Q4. Month of listing (all years combined)
    d = df.dropna(subset=["dom"])
    q4 = []
    for m in range(1, 13):
        s = d[d["list_date"].dt.month == m]["dom"]
        q4.append({"month": m, "n": int(len(s)), "median_dom": med(s)})
    q4_years = d["list_date"].dt.year.value_counts().sort_index()

    # Q5. Assessed value to sale price
    a = valid[valid["tax_assessed_value"] > 0].copy()
    a["ratio"] = a["tax_assessed_value"] / a["sale_price"]
    q5 = []
    for c in campuses:
        s = a[a["university"] == c["name"]]["ratio"]
        q5.append({"campus": c["short"], "state": c["state"], "n": int(len(s)),
                   "median_ratio": round(med(s), 3)})

    # Q6. Addresses with more than one sale
    key = ["address_street", "city", "state", "zipcode"]
    df["at_address"] = df.groupby(key, dropna=False)["listing_id"].transform("count")
    multi = df[df["at_address"] > 1]
    q6 = []
    for c in campuses:
        rows = df[df["university"] == c["name"]]
        m = rows[rows["at_address"] > 1]
        o = rows[rows["at_address"] == 1]
        q6.append({"campus": c["short"], "addresses": int(m.groupby(key).ngroups),
                   "sales": len(m), "median_miles_multi": med(m["miles_to_campus"]),
                   "median_miles_other": med(o["miles_to_campus"])})
    q6_total = {"addresses": int(multi.groupby(key).ngroups), "sales": len(multi),
                "median_miles_multi": med(multi["miles_to_campus"]),
                "median_miles_other": med(df[df["at_address"] == 1]["miles_to_campus"])}

    out = {
        "source": "College-town home sales dataset, version 1.0",
        "rows": len(df),
        "rules": {"min_price": MIN_PRICE, "min_sqft": MIN_SQFT, "min_group": MIN_GROUP},
        "counts": {"valid_sales": len(valid), "pps_sales": len(pps),
                   "dom_sales": int(df["dom"].notna().sum()),
                   "assessed_sales": len(a)},
        "sale_dates": [str(df["sale_date"].min().date()), str(df["sale_date"].max().date())],
        "campuses": campuses,
        "q1": q1, "q2": q2, "q3": q3,
        "q4": q4, "q4_list_years": {str(k): int(v) for k, v in q4_years.items()},
        "q5": q5, "q6": q6, "q6_total": q6_total,
    }
    OUT.write_text(json.dumps(out, indent=1))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
