"""Build data/sales.json for the Close to Campus site.

Run from the repository root:

    pip install pandas
    python scripts/build_data.py

The site does its own filtering in the browser (campus, budget, distance), so this
script selects the rows and columns the site needs, writes them compactly, and adds
the few figures the data notes quote.
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "college_town_home_sales.csv"
OUT = ROOT / "data" / "sales.json"

MIN_PRICE = 10_000      # sales under $10,000 are not ordinary market sales
MIN_SQFT = 100          # living areas under 100 sq ft are treated as missing
MONTHS = 12             # the most recent 12 months of sales in the data
ADDRESS = ["address_street", "city", "state", "zipcode"]

# Campus landmarks: the points miles_to_campus is measured to, from the dataset's build script.
CAMPUSES = [
    ("University of Illinois Urbana-Champaign", "Illinois", "Champaign-Urbana, IL", "Foellinger Auditorium", 40.1059, -88.2272),
    ("Purdue University", "Purdue", "West Lafayette, IN", "Engineering Fountain", 40.42864, -86.91378),
    ("University of Wisconsin-Madison", "UW-Madison", "Madison, WI", "Bascom Hill", 43.0753, -89.4041),
    ("University of Michigan", "Michigan", "Ann Arbor, MI", "The Diag", 42.2767, -83.7387),
    ("The University of Iowa", "Iowa", "Iowa City, IA", "Old Capitol", 41.661333, -91.535639),
    ("The Pennsylvania State University", "Penn State", "State College, PA", "Old Main", 40.7960, -77.8627),
    ("University of Florida", "Florida", "Gainesville, FL", "Century Tower", 29.648834, -82.34329),
    ("University of Georgia", "Georgia", "Athens, GA", "North Campus", 33.9558, -83.3745),
    ("The University of North Carolina at Chapel Hill", "UNC", "Chapel Hill, NC", "Old Well", 35.912056, -79.051250),
    ("University of Virginia", "Virginia", "Charlottesville, VA", "Central Grounds", 38.0350, -78.5050),
    ("University of California, Davis", "UC Davis", "Davis, CA", "Shields Library", 38.53972, -121.74917),
]


def build():
    df = pd.read_csv(SOURCE, dtype=str, keep_default_na=False, na_values=[""])
    for c in ["sale_price", "living_area_sqft", "beds", "latitude", "longitude", "miles_to_campus"]:
        df[c] = pd.to_numeric(df[c])
    for c in ["list_date", "contract_date", "sale_date"]:
        df[c] = pd.to_datetime(df[c], format="%Y-%m-%d")
    assert len(df) == 35_529 and df["listing_id"].is_unique

    last = df["sale_date"].max()
    first = last - pd.DateOffset(months=MONTHS) + pd.Timedelta(days=1)
    in_window = (df["sale_date"] >= first) & (df["sale_date"] <= last)
    recent = df[in_window & (df["sale_price"] >= MIN_PRICE)].copy()
    excluded = df[in_window & (df["sale_price"] < MIN_PRICE)]
    recent["dom"] = (recent["contract_date"] - recent["list_date"]).dt.days
    recent.loc[recent["living_area_sqft"] < MIN_SQFT, "living_area_sqft"] = pd.NA

    # Were prices steady over the three years? Median price in each full calendar quarter.
    priced = df[df["sale_price"] >= MIN_PRICE].copy()
    priced["quarter"] = priced["sale_date"].dt.to_period("Q")
    full = [q for q in priced["quarter"].dropna().unique()
            if q.start_time >= df["sale_date"].min() and q.end_time.normalize() <= last]
    quarterly = priced[priced["quarter"].isin(full)].groupby("quarter")["sale_price"].median()

    # Pairs at one address with prices within 1% and sale dates within 90 days: the build
    # notes' own test for one sale recorded twice. We keep both rows but say how many there are.
    pairs = 0
    for _, g in recent.groupby(ADDRESS):
        p, t = g["sale_price"], g["sale_date"]
        if len(g) == 2 and p.max() - p.min() <= 0.01 * p.max() and (t.max() - t.min()).days <= 90:
            pairs += 1

    index = {name: i for i, (name, *_rest) in enumerate(CAMPUSES)}
    recent["campus_index"] = recent["university"].map(index)
    recent = recent.sort_values(["campus_index", "miles_to_campus", "listing_id"], kind="stable")

    def col(series, digits=None):
        return [None if pd.isna(v) else int(v) if digits is None else round(float(v), digits) for v in series]

    return {
        "source": "College-town home sales dataset, version 1.0",
        "window": [first.strftime("%Y-%m-%d"), last.strftime("%Y-%m-%d")],
        "rules": {"min_price": MIN_PRICE, "min_sqft": MIN_SQFT},
        "sales_count": len(recent),
        "excluded_under_min_price": len(excluded),
        "lowest_excluded_price": int(excluded["sale_price"].min()),
        "quarterly_median_range": [int(quarterly.min()), int(quarterly.max())],
        "full_quarters": len(quarterly),
        "likely_double_records": pairs,
        "campuses": [{"name": n, "short": s, "town": t, "landmark": lm, "lat": la, "lon": lo}
                     for n, s, t, lm, la, lo in CAMPUSES],
        "sales": {
            "campus": [int(i) for i in recent["campus_index"]],
            "lat": col(recent["latitude"], 4),
            "lon": col(recent["longitude"], 4),
            "miles": col(recent["miles_to_campus"], 1),
            "price": col(recent["sale_price"]),
            "sqft": col(recent["living_area_sqft"]),
            "beds": col(recent["beds"]),
            "dom": col(recent["dom"]),
        },
    }


def main():
    data = build()
    OUT.write_text(json.dumps(data, separators=(",", ":")))
    print("wrote", OUT, data["sales_count"], "sales")


if __name__ == "__main__":
    main()
