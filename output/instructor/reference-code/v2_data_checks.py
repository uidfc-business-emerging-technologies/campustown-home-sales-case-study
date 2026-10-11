"""Handoff section 7: check each Variation 2 question against the data.

    python v2_data_checks.py

Prints the evidence behind each check and writes it to
results/variation2_checks.txt. The report cites these figures.
"""

import io
from contextlib import redirect_stdout
from pathlib import Path

import pandas as pd

import variation2 as v2
from definitions import add_derived, half_up, load

RESULTS = Path(__file__).resolve().parent / "results"
COLLECTION_START = "2023-03-27"  # first sale date in the dataset


def check_q1(df):
    table = v2.q1_price_levels(df)
    moved = table[table["rank by price"] != table["rank by price per sq ft"]]
    print("Q1. Areas whose rank differs between the two measures:")
    for university, row in moved.iterrows():
        print(f"    {university}: rank {row['rank by price']} by price, {row['rank by price per sq ft']} by price per sq ft")


def check_q2(df):
    table = v2.q2_speed(df)
    fastest = table["median days on market"].min()
    tied = table[table["median days on market"] == fastest].index.tolist()
    share = table["share missing days on market"]
    print(f"\nQ2. Fastest median {fastest:g} days, shared by {len(tied)} areas: {', '.join(tied)}")
    print(f"    Share missing days on market: {half_up(100 * share.min(), 1)}% ({share.idxmin()}) "
          f"to {half_up(100 * share.max(), 1)}% ({share.idxmax()})")


def check_q3(df):
    counts, _, shown = v2.q3_distance(df)
    cells = counts.stack()
    small = cells[cells < v2.MIN_GROUP]
    print(f"\nQ3. {len(small)} of {counts.size} area-band cells have fewer than {v2.MIN_GROUP} sales:")
    for (university, band), n in small.items():
        print(f"    {university}, {band}: {n}")
    pattern = v2.q3_pattern(shown)
    print("    Pattern by area:")
    for university, row in pattern.iterrows():
        print(f"    {university}: {row['pattern']} (highest in {row['highest band']})")


def check_q4(df):
    rows = df[df["days_on_market"].notna()]
    listed_before = rows[rows["list_date"] < COLLECTION_START]
    by_year = rows["list_date"].dt.year.value_counts().sort_index()
    print("\nQ4. Listings with days on market, by year listed:", {int(k): int(v) for k, v in by_year.items()})
    print(f"    Listed before the first sale date ({COLLECTION_START}): {len(listed_before)} listings, "
          f"median {listed_before['days_on_market'].median():g} days")
    print("    Median days on market by year and month listed:")
    print(rows.pivot_table(index=rows["list_date"].dt.year, columns=rows["list_date"].dt.month,
                           values="days_on_market", aggfunc="median").to_string())

    listed_2024 = df[df["list_date"].dt.year == 2024]
    list_to_close = (listed_2024["sale_date"] - listed_2024["list_date"]).dt.days
    print("    Share of 2024 listings that took longer than N days from listing to closing:")
    for n in [90, 180, 359]:
        print(f"      {n} days: {half_up(100 * (list_to_close > n).mean(), 1)}%")

    all_years = v2.q4_timing(df, window=False)
    window = v2.q4_timing(df, window=True)
    side_by_side = pd.concat([all_years, window], axis=1, keys=["all years", "listed in the window"])
    print(f"    By month, all years against the window {v2.LISTING_WINDOW[0]} to {v2.LISTING_WINDOW[1]}:")
    print(side_by_side.to_string())


def check_q5(df):
    table = v2.q5_assessment(df)
    print(f"\nQ5. Median assessed value / sale price ({table['sales used'].sum():,} sales):")
    for university, row in table.iterrows():
        print(f"    {university} ({row['state']}): {half_up(row['median assessed / sale price'], 2):.2f}")


def check_q6(df):
    by_area, total = v2.q6_buildings(df)
    print(f"\nQ6. {total['sales at those addresses']} sales at {total['addresses with more than one sale']} addresses; "
          f"median miles {total['median miles, sales at those addresses']:g} against {total['median miles, all other sales']:g} for all other sales")
    print(by_area[by_area["sales at those addresses"] > 0].to_string())

    groups = v2.shared_address_groups(df)
    doubles = groups[groups["likely one sale recorded twice"]]
    print(f"\n    Repeated addresses that meet the build notes' duplicate rule (2 rows, prices within 1%, "
          f"sale dates within 90 days): {len(doubles)} of {len(groups)} addresses, {doubles['sales'].sum()} of {groups['sales'].sum()} rows")
    print(groups.groupby("university").agg(
        addresses=("sales", "size"),
        rows=("sales", "sum"),
        likely_double_records=("likely one sale recorded twice", "sum"),
    ).to_string())
    pairs = doubles[doubles["sales"] == 2]
    split = ((pairs["rows with a list or contract date"] == 1) & (pairs["rows with an assessed value"] == 1)).sum()
    print(f"    Of those pairs, {split} have one row with listing dates and the other with an assessed value, "
          f"{(pairs['distinct prices'] == 1).sum()} have identical prices, "
          f"and {(pairs['days between first and last sale'] == 0).sum()} close on the same day.")


def main():
    df = add_derived(load())
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        for check in [check_q1, check_q2, check_q3, check_q4, check_q5, check_q6]:
            check(df)
    text = buffer.getvalue()
    print(text)
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "variation2_checks.txt").write_text(text)


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    main()
