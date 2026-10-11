"""Build data/sales.json for the Close to Campus site.

Run from the repository root:

    pip install pandas pyarrow
    python scripts/build_data.py

The site does its own filtering in the browser (budget, distance, campus), so this
script only selects the rows and columns the site needs and writes them compactly.
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "college_town_home_sales.parquet"
OUT = ROOT / "data" / "sales.json"

MIN_PRICE = 10_000      # sales under $10,000 are not ordinary market sales
MIN_SQFT = 100          # living areas under 100 sq ft are treated as missing
LAST_SALE = "2026-03-25"
FIRST_SALE = "2025-03-26"  # the most recent 12 months of sales in the data

# Campus landmarks, from the dataset's build notes (the point miles_to_campus is measured to).
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


def main():
    df = pd.read_parquet(SOURCE)
    assert len(df) == 35_529, len(df)
    for c in ["list_date", "contract_date", "sale_date"]:
        df[c] = pd.to_datetime(df[c])

    recent = df[(df["sale_date"] >= FIRST_SALE) & (df["sale_date"] <= LAST_SALE)
                & (df["sale_price"] >= MIN_PRICE)].copy()
    recent["dom"] = (recent["contract_date"] - recent["list_date"]).dt.days
    recent.loc[recent["living_area_sqft"] < MIN_SQFT, "living_area_sqft"] = pd.NA

    index = {name: i for i, (name, *_rest) in enumerate(CAMPUSES)}
    recent = recent.sort_values(["university", "miles_to_campus"])

    def col(series, digits=None):
        out = []
        for v in series:
            if pd.isna(v):
                out.append(None)
            elif digits is None:
                out.append(int(v))
            else:
                out.append(round(float(v), digits))
        return out

    data = {
        "source": "College-town home sales dataset, version 1.0",
        "window": [FIRST_SALE, LAST_SALE],
        "rules": {"min_price": MIN_PRICE, "min_sqft": MIN_SQFT},
        "excluded_under_min_price": int(((df["sale_date"] >= FIRST_SALE) & (df["sale_price"] < MIN_PRICE)).sum()),
        "campuses": [{"name": n, "short": s, "town": t, "landmark": lm, "lat": la, "lon": lo}
                     for n, s, t, lm, la, lo in CAMPUSES],
        "sales": {
            "campus": [index[u] for u in recent["university"]],
            "lat": col(recent["latitude"], 4),
            "lon": col(recent["longitude"], 4),
            "miles": col(recent["miles_to_campus"], 1),
            "price": col(recent["sale_price"]),
            "sqft": col(recent["living_area_sqft"]),
            "beds": col(recent["beds"]),
            "dom": col(recent["dom"]),
        },
    }
    OUT.write_text(json.dumps(data, separators=(",", ":")))
    print("wrote", OUT, len(recent), "sales")


if __name__ == "__main__":
    main()
