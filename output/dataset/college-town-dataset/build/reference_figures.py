#!/usr/bin/env python3
"""
Instructor reference figures for the college-town home sales dataset.

    python build/reference_figures.py            # from the package root, or anywhere

Reads ../data/college_town_home_sales.csv (relative to this script) and writes four files
to ../docs/: reference_figures.md, reference_figures_by_city.csv, city_campus_map.md and
city_campus_map.csv. --input and --outdir override the defaults.

These are the numbers a learner's finished site should be able to reproduce, so a mismatch
is easy to spot without reading their code. Every figure uses rules stated in the output,
because "median price" is ambiguous until you say what you did with the $0 sales, and
"days on market" is ambiguous until you say which two dates you subtracted.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
MIN_PRICE = 1_000      # sales below this are treated as non-arm's-length or data errors
MIN_AREA = 100         # square feet; excludes zero and near-zero living areas
GROUP = ["state", "city"]


def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False, na_values=[""])
    for c in ["sale_price", "living_area_sqft", "year_built", "beds", "tax_annual_amount", "miles_to_campus"]:
        df[c] = pd.to_numeric(df[c])
    for c in ["list_date", "contract_date", "sale_date"]:
        df[c] = pd.to_datetime(df[c], format="%Y-%m-%d")
    df["priced"] = df["sale_price"] >= MIN_PRICE
    df["price_per_sqft"] = (df["sale_price"].where(df["priced"])
                            / df["living_area_sqft"].where(df["living_area_sqft"] >= MIN_AREA))
    df["days_on_market"] = (df["contract_date"] - df["list_date"]).dt.days
    df["contract_to_close"] = (df["sale_date"] - df["contract_date"]).dt.days
    df["list_to_close"] = (df["sale_date"] - df["list_date"]).dt.days
    df["shares_address"] = df.groupby(["address_street", "city", "state", "zipcode"])["listing_id"].transform("size") > 1
    return df


def by_city(df: pd.DataFrame) -> pd.DataFrame:
    g, p = df.groupby(GROUP), df[df["priced"]].groupby(GROUP)
    out = pd.DataFrame({
        "university": g["university"].first(),
        "rows": g.size(),
        "rows_priced": p.size(),
        "median_sale_price": p["sale_price"].median(),
        "mean_sale_price": p["sale_price"].mean().round(0),
        "median_price_per_sqft": g["price_per_sqft"].median().round(2),
        "median_living_area_sqft": g["living_area_sqft"].median(),
        "median_year_built": g["year_built"].median(),
        "median_beds": g["beds"].median(),
        "median_tax_annual": g["tax_annual_amount"].median().round(0),
        "rows_with_list_date": g["list_date"].count(),
        "rows_with_contract_date": g["contract_date"].count(),
        "median_days_on_market": g["days_on_market"].median(),
        "median_contract_to_close": g["contract_to_close"].median(),
        "earliest_sale": g["sale_date"].min().dt.date,
        "latest_sale": g["sale_date"].max().dt.date,
        "rows_sharing_address": g["shares_address"].sum(),
    })
    return out.sort_values("rows", ascending=False).reset_index()


def campus_map(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby(["university", "state", "city"])
              .agg(rows=("listing_id", "size"), median_miles_to_campus=("miles_to_campus", "median"))
              .reset_index().sort_values(["university", "rows"], ascending=[True, False]))


def money(v: float) -> str:
    return f"${v:,.0f}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", default=HERE.parent / "data" / "college_town_home_sales.csv", type=Path)
    ap.add_argument("--outdir", default=HERE.parent / "docs", type=Path)
    args = ap.parse_args()
    if not args.input.exists():
        raise SystemExit(f"input not found: {args.input}")
    args.outdir.mkdir(parents=True, exist_ok=True)

    raw_cols = pd.read_csv(args.input, nrows=0).shape[1]
    df = load(args.input)
    city = by_city(df)
    city.to_csv(args.outdir / "reference_figures_by_city.csv", index=False)
    cmap = campus_map(df)
    cmap.to_csv(args.outdir / "city_campus_map.csv", index=False)

    n_low = int((~df["priced"]).sum())
    dom, esc, ltc = df["days_on_market"].dropna(), df["contract_to_close"].dropna(), df["list_to_close"].dropna()
    lines = [
        "# Reference figures (instructor copy)",
        "",
        f"Dataset: {len(df):,} rows, {df['city'].nunique()} cities in {df['state'].nunique()} states, "
        f"{df['university'].nunique()} campuses.",
        "",
        "These are the numbers a correct site should show. They are not the only defensible answers:",
        "a learner who states a different rule and applies it consistently is right too. What",
        "matters is that the figure on the site matches the rule the learner says they used.",
        "",
        "**Rules used here**",
        "",
        f"- Price figures exclude sales under {money(MIN_PRICE)}. There are {n_low} such rows, "
        "including sales of $0. Row counts include them.",
        f"- Price per square foot excludes living areas under {MIN_AREA} sq ft, is computed row by "
        "row, and then a median is taken. Dividing a median price by a median area gives a "
        "different, wrong answer.",
        "- Median, not mean, for prices. The highest sale in the dataset is "
        f"{money(df['sale_price'].max())}.",
        "- Days on market is `contract_date - list_date`, computed only on rows that have both "
        f"({len(dom):,} rows). Using `sale_date - list_date` instead adds the time to close, "
        f"which has a median of {esc.median():.0f} days.",
        "",
        "## By city",
        "",
        "| City | Rows | Median price | Mean price | Median $/sqft | Median sqft | Median year built "
        "| Median days on market | Rows sharing an address |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in city.itertuples():
        lines.append(
            f"| {r.city}, {r.state} | {r.rows:,} | {money(r.median_sale_price)} | {money(r.mean_sale_price)} | "
            f"${r.median_price_per_sqft:,.2f} | {r.median_living_area_sqft:,.0f} | {r.median_year_built:.0f} | "
            f"{r.median_days_on_market:.0f} | {r.rows_sharing_address} |")

    camp = (df.groupby("university")
              .agg(rows=("listing_id", "size"),
                   median_miles=("miles_to_campus", "median"),
                   median_ppsf=("price_per_sqft", "median"),
                   median_dom=("days_on_market", "median"))
              .join(df[df["priced"]].groupby("university")["sale_price"].median().rename("median_price"))
              .sort_values("rows", ascending=False))
    lines += [
        "",
        "## By campus",
        "",
        "Campus is assigned from each property's coordinates, not its city label. Rows are all rows;",
        "prices follow the rules above.",
        "",
        "| University | Rows | Median price | Median $/sqft | Median days on market | Median miles to campus |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for u, r in camp.iterrows():
        lines.append(f"| {u} | {int(r.rows):,} | {money(r.median_price)} | ${r.median_ppsf:,.2f} | "
                     f"{r.median_dom:.0f} | {r.median_miles:.1f} |")

    lines += [
        "",
        "## Whole dataset",
        "",
        "| Figure | Value |",
        "|---|---:|",
        f"| Rows | {len(df):,} |",
        f"| Columns | {raw_cols} |",
        f"| Cities / states / counties | {df['city'].nunique()} / {df['state'].nunique()} / {df['county'].nunique()} |",
        f"| Median sale price | {money(df.loc[df['priced'], 'sale_price'].median())} |",
        f"| Sale dates | {df['sale_date'].min().date()} to {df['sale_date'].max().date()} |",
        f"| Rows with a sale date | {df['sale_date'].notna().sum():,} |",
        f"| Rows with a list date | {df['list_date'].notna().sum():,} ({df['list_date'].notna().mean():.1%}) |",
        f"| Rows with a contract date | {df['contract_date'].notna().sum():,} ({df['contract_date'].notna().mean():.1%}) |",
        f"| Rows with both (days on market computable) | {len(dom):,} ({len(dom) / len(df):.1%}) |",
        f"| Median days on market | {dom.median():.0f} |",
        f"| Median contract to close | {esc.median():.0f} days |",
        f"| Median list to close | {ltc.median():.0f} days |",
        f"| Rows sharing a street address | {int(df['shares_address'].sum()):,} |",
        f"| Largest building | {int(df.groupby(['address_street', 'city', 'state', 'zipcode']).size().max())} sales at one address |",
        "",
        "## Four things to check on a learner's site",
        "",
        "1. **Does the city total match?** If it is short by a few rows, they probably deduplicated by "
        "address and deleted condo units.",
        "2. **Does the median look like the table above?** One far too high usually means a mean was "
        "computed instead, or the $0 sales were left in a min/max display.",
        "3. **Does price per square foot look plausible?** A figure in the thousands means the "
        "zero-square-foot rows were divided by.",
        "4. **Is days on market about a month too long?** Then they subtracted `list_date` from "
        "`sale_date`, which includes the time to close. If it is close to zero for many homes, "
        "they may have treated blanks as zero.",
    ]
    (args.outdir / "reference_figures.md").write_text("\n".join(lines) + "\n")

    total = int(cmap["rows"].sum())
    m = ["# City to campus map", "",
         f"{df['city'].nunique()} cities across {df['university'].nunique()} campuses. Assignment is by "
         "each property's coordinates, not its city label, so a row whose city field is wrong still "
         "lands in the right campus group.", "",
         f"Every city listed here appears in the dataset, and the row counts sum to all {total:,} rows. "
         "Cities with fewer than 90 sales were dropped from the dataset during the build.", "",
         "| University | Cities (rows) | Total rows |", "|---|---|---:|"]
    for u, g in cmap.groupby("university", sort=True):
        m.append(f"| {u} | " + ", ".join(f"{c} ({n:,})" for c, n in zip(g["city"], g["rows"]))
                 + f" | {int(g['rows'].sum()):,} |")
    (args.outdir / "city_campus_map.md").write_text("\n".join(m) + "\n")

    print(f"wrote reference_figures.md, reference_figures_by_city.csv, city_campus_map.md and "
          f"city_campus_map.csv to {args.outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
