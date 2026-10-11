"""Summary files for the Variation 1 and Variation 3 reference sites.

Each site also carries its own scripts/build_data.py, written the way a student
would. run_all.py writes these reference versions into the sites and stops if a
site's own script would produce anything different.
"""

import importlib.util
import json
import sys

import numpy as np
import pandas as pd

import variation2 as v2
from definitions import half_up

MIN_GROUP = 20


# ---- Variation 1: Old Homes, Close In ---------------------------------------------------
V1_DECADE_START, V1_DECADE_END = 1900, 2020


def v1_summary(df):
    d = df.copy()
    d["age"] = d["sale_date"].dt.year - d["year_built"]
    d["new"] = d["age"] <= 1
    d["band"] = v2.add_band(d)
    d["decade"] = (d["year_built"] // 10 * 10)
    dated = d[d["year_built"].notna() & d["sale_date"].notna()]

    def area_figures(rows):
        built = rows[rows["year_built"].notna()]
        by_band = []
        for label in v2.BAND_LABELS:
            s = built[built["band"] == label]["year_built"]
            by_band.append({"n": int(len(s)), "median_year": half_up(s.median()) if len(s) >= MIN_GROUP else None})
        by_decade = []
        priced = built[built["price_per_sqft"].notna()]
        for decade in range(V1_DECADE_START, V1_DECADE_END + 10, 10):
            s = priced[priced["decade"] == decade]["price_per_sqft"]
            by_decade.append({"decade": decade, "n": int(len(s)),
                              "median_pps": half_up(s.median(), 2) if len(s) >= MIN_GROUP else None})
        r = rows[rows["year_built"].notna() & rows["sale_date"].notna()]
        new = r[r["new"]]
        return {
            "rows": int(len(rows)),
            "median_year": half_up(built["year_built"].median()),
            "by_band": by_band,
            "by_decade": by_decade,
            "new_homes": int(len(new)),
            "new_share": half_up(len(new) / len(r), 4),
            "new_no_list_share": half_up(new["list_date"].isna().mean(), 4) if len(new) >= MIN_GROUP else None,
        }

    areas = {"All campus areas": area_figures(d)}
    for u in v2.SHORT_NAMES:
        areas[v2.SHORT_NAMES[u]] = area_figures(d[d["university"] == u])

    old = dated[~dated["new"]]
    return {
        "source": "College-town home sales dataset, version 1.0",
        "rows": int(len(d)),
        "rules": {"min_price": 1000, "min_sqft": 100, "min_group": MIN_GROUP},
        "bands": v2.BAND_LABELS,
        "campuses": [{"short": s, "name": u} for u, s in v2.SHORT_NAMES.items()],
        "counts": {
            "year_built_missing": int(d["year_built"].isna().sum()),
            "sale_date_missing": int(d["sale_date"].isna().sum()),
            "built_1900": int((d["year_built"] == 1900).sum()),
            "built_1901": int((d["year_built"] == 1901).sum()),
            "built_1902_1909_per_year": half_up((d["year_built"].between(1902, 1909)).sum() / 8, 1),
            "sold_before_finished": int((d["age"] < 0).sum()),
            "pps_sales": int(d["price_per_sqft"].notna().sum()),
            "dated_sales": int(len(dated)),
        },
        "areas": areas,
        "listing": {
            "new_no_list_share": half_up(dated[dated["new"]]["list_date"].isna().mean(), 4),
            "older_no_list_share": half_up(old["list_date"].isna().mean(), 4),
        }
    }


# ---- Variation 3: Close to Campus -------------------------------------------------------
V3_MIN_PRICE = 10_000
V3_MONTHS = 12
V3_CAMPUSES = [
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


def v3_window(df):
    last = df["sale_date"].max()
    return last - pd.DateOffset(months=V3_MONTHS) + pd.Timedelta(days=1), last


def v3_sales(df):
    first, last = v3_window(df)
    window = (df["sale_date"] >= first) & (df["sale_date"] <= last)
    recent = df[window & (df["sale_price"] >= V3_MIN_PRICE)].copy()
    excluded = df[window & (df["sale_price"] < V3_MIN_PRICE)]
    sqft = recent["living_area_sqft"].where(recent["living_area_sqft"] >= 100)

    priced = df[df["sale_price"] >= V3_MIN_PRICE]
    quarter = priced["sale_date"].dt.to_period("Q")
    full = quarter.notna() & (quarter.dt.start_time >= df["sale_date"].min()) & (quarter.dt.end_time.dt.normalize() <= last)
    quarterly = priced[full].groupby(quarter[full])["sale_price"].median()

    index = {c[0]: i for i, c in enumerate(V3_CAMPUSES)}
    recent = recent.assign(ci=recent["university"].map(index), sqft=sqft).sort_values(
        ["ci", "miles_to_campus", "listing_id"], kind="stable")

    def col(series, digits=None):
        return [None if pd.isna(v) else int(v) if digits is None else round(float(v), digits) for v in series]

    return {
        "source": "College-town home sales dataset, version 1.0",
        "window": [first.strftime("%Y-%m-%d"), last.strftime("%Y-%m-%d")],
        "rules": {"min_price": V3_MIN_PRICE, "min_sqft": 100},
        "sales_count": int(len(recent)),
        "excluded_under_min_price": int(len(excluded)),
        "lowest_excluded_price": int(excluded["sale_price"].min()),
        "quarterly_median_range": [int(quarterly.min()), int(quarterly.max())],
        "full_quarters": int(len(quarterly)),
        "campuses": [{"name": n, "short": s, "town": t, "landmark": lm, "lat": la, "lon": lo} for n, s, t, lm, la, lo in V3_CAMPUSES],
        "sales": {
            "campus": [int(i) for i in recent["ci"]],
            "lat": col(recent["latitude"], 4),
            "lon": col(recent["longitude"], 4),
            "miles": col(recent["miles_to_campus"], 1),
            "price": col(recent["sale_price"]),
            "sqft": col(recent["sqft"]),
            "beds": col(recent["beds"]),
            "dom": col(recent["days_on_market"]),
        },
    }


def v3_expected(sales, campus, budget, dist):
    """The site's three headline numbers for one setting, computed in Python for the browser test."""
    s = pd.DataFrame(sales["sales"])
    ci = [c[1] for c in V3_CAMPUSES].index(campus)
    near = s[(s["campus"] == ci) & (s["miles"] <= dist)]
    inb = near[near["price"] <= budget]
    sq, dom = inb["sqft"].dropna(), inb["dom"].dropna()
    return {
        "share": f"{half_up(100 * len(inb) / len(near))}%" if len(near) else "None",
        "counts": f"{len(inb):,} of the {len(near):,}",
        "sqft": f"{half_up(sq.median()):,} sq ft" if len(sq) >= MIN_GROUP else "Too few sales",
        "dom": (f"{dom.median():g} days" if len(dom) >= MIN_GROUP else "Too few sales"),
    }


# ---- checks -------------------------------------------------------------------------------
def run_site_script(site_dir):
    """Import a site's own scripts/build_data.py and return what its build() produces."""
    path = site_dir / "scripts" / "build_data.py"
    spec = importlib.util.spec_from_file_location(f"site_{site_dir.name.replace('-', '_')}", path)
    module = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True  # leave no __pycache__ folder in the site
    spec.loader.exec_module(module)
    return json.loads(json.dumps(module.build()))


def first_difference(a, b, path="$"):
    if type(a) is not type(b):
        return f"{path}: {a!r} != {b!r}"
    if isinstance(a, dict):
        if list(a) != list(b):
            return f"{path}: keys {list(a)} != {list(b)}"
        for k in a:
            diff = first_difference(a[k], b[k], f"{path}.{k}")
            if diff:
                return diff
    elif isinstance(a, list):
        if len(a) != len(b):
            return f"{path}: length {len(a)} != {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            diff = first_difference(x, y, f"{path}[{i}]")
            if diff:
                return diff
    elif a != b:
        return f"{path}: {a!r} != {b!r}"
    return None
