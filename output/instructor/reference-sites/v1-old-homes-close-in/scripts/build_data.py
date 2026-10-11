"""Build data/age.json for the Old Homes, Close In site.

Run from the repository root:

    pip install pandas
    python scripts/build_data.py

Every number on the site comes from the file this script writes.
"""
import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "college_town_home_sales.csv"
OUT = ROOT / "data" / "age.json"

MIN_PRICE = 1_000      # a valid sale is $1,000 or more
MIN_SQFT = 100         # price per square foot needs at least 100 sq ft of living area
MIN_GROUP = 20         # a median from fewer than 20 sales is not shown
BANDS = [(0, 1, "Under 1 mile"), (1, 2, "1 to under 2 miles"), (2, 5, "2 to under 5 miles"),
         (5, 10, "5 to under 10 miles"), (10, float("inf"), "10 miles or more")]
DECADES = range(1900, 2030, 10)
ADDRESS = ["address_street", "city", "state", "zipcode"]

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
    """Round half up, so 1972.5 becomes 1973."""
    q = Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP)
    return int(q) if digits == 0 else float(q)


def load():
    df = pd.read_csv(SOURCE, dtype=str, keep_default_na=False, na_values=[""])
    for c in ["sale_price", "living_area_sqft", "year_built", "miles_to_campus"]:
        df[c] = pd.to_numeric(df[c])
    for c in ["list_date", "sale_date"]:
        df[c] = pd.to_datetime(df[c], format="%Y-%m-%d")
    assert len(df) == 35_529 and df["listing_id"].is_unique
    valid = (df["sale_price"] >= MIN_PRICE) & (df["living_area_sqft"] >= MIN_SQFT)
    df["pps"] = (df["sale_price"] / df["living_area_sqft"]).where(valid)
    # A new home: built in the year it sold or the year before, or sold before it was finished.
    df["age"] = df["sale_date"].dt.year - df["year_built"]
    df["new"] = df["age"] <= 1
    df["decade"] = df["year_built"] // 10 * 10
    return df


def figures(rows):
    built = rows[rows["year_built"].notna()]
    by_band = []
    for lo, hi, _ in BANDS:
        s = built[(built["miles_to_campus"] >= lo) & (built["miles_to_campus"] < hi)]["year_built"]
        by_band.append({"n": len(s), "median_year": rnd(s.median()) if len(s) >= MIN_GROUP else None})
    priced = built[built["pps"].notna()]
    by_decade = []
    for decade in DECADES:
        s = priced[priced["decade"] == decade]["pps"]
        by_decade.append({"decade": decade, "n": len(s), "median_pps": rnd(s.median(), 2) if len(s) >= MIN_GROUP else None})
    dated = rows[rows["year_built"].notna() & rows["sale_date"].notna()]
    new = dated[dated["new"]]
    return {
        "rows": len(rows),
        "median_year": rnd(built["year_built"].median()),
        "by_band": by_band,
        "by_decade": by_decade,
        "new_homes": len(new),
        "new_share": rnd(len(new) / len(dated), 4),
        "new_no_list_share": rnd(new["list_date"].isna().mean(), 4) if len(new) >= MIN_GROUP else None,
    }


def build():
    df = load()
    dated = df[df["year_built"].notna() & df["sale_date"].notna()]
    areas = {"All campus areas": figures(df)}
    for full, short in SHORT.items():
        areas[short] = figures(df[df["university"] == full])

    # Around Virginia, many new homes appear twice: two rows at one address with prices within
    # 1% and sale dates within 90 days (the build notes' test for one sale recorded twice).
    # We keep every row, but work out Virginia's share of new homes with one copy of each pair.
    va = dated[dated["university"] == "University of Virginia"]
    pairs = 0
    for _, g in df[df["university"] == "University of Virginia"].groupby(ADDRESS):
        p, t = g["sale_price"], g["sale_date"]
        if len(g) == 2 and p.max() - p.min() <= 0.01 * p.max() and (t.max() - t.min()).days <= 90 and g["new"].all():
            pairs += 1

    return {
        "source": "College-town home sales dataset, version 1.0",
        "rows": len(df),
        "rules": {"min_price": MIN_PRICE, "min_sqft": MIN_SQFT, "min_group": MIN_GROUP},
        "bands": [b[2] for b in BANDS],
        "campuses": [{"short": s, "name": n} for n, s in SHORT.items()],
        "counts": {
            "year_built_missing": int(df["year_built"].isna().sum()),
            "sale_date_missing": int(df["sale_date"].isna().sum()),
            "built_1900": int((df["year_built"] == 1900).sum()),
            "built_1901": int((df["year_built"] == 1901).sum()),
            "built_1902_1909_per_year": rnd(df["year_built"].between(1902, 1909).sum() / 8, 1),
            "sold_before_finished": int((df["age"] < 0).sum()),
            "pps_sales": int(df["pps"].notna().sum()),
            "dated_sales": len(dated),
        },
        "areas": areas,
        "listing": {
            "new_no_list_share": rnd(dated[dated["new"]]["list_date"].isna().mean(), 4),
            "older_no_list_share": rnd(dated[~dated["new"]]["list_date"].isna().mean(), 4),
        },
        "virginia_double_records": {
            "new_pairs": pairs,
            "new_share_one_copy": rnd((int(va["new"].sum()) - pairs) / (len(va) - pairs), 4),
        },
    }


def main():
    OUT.write_text(json.dumps(build(), indent=1) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
