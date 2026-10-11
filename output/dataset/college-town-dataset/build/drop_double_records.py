#!/usr/bin/env python3
"""
Remove the second record of each sale the source holds under two parcel numbers, and
rewrite the dataset files.

    pip install pandas openpyxl pyarrow duckdb
    python build/drop_double_records.py          # from the package root, or anywhere

The raw build inputs are not distributed, so this applies the rule to the released CSV.
The rule is build_dataset.drop_double_records(), the same function a full rebuild runs
after removing same-parcel duplicates: an address with exactly two rows whose prices are
within 1% and whose sale dates are within 90 days is one sale recorded twice, and the
more complete record is kept.

It reads ../data/college_town_home_sales.csv, writes all five files with the build's own
writers (CSV, SQLite, Excel, DuckDB, Parquet), checks the DuckDB and Parquet files against
the new CSV value by value (make_parquet.verify), and writes the removed rows, each beside
the record that was kept, to removed_double_records.csv in this folder.

Running it again on the fixed file removes nothing.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_dataset as B  # noqa: E402
import make_parquet as M  # noqa: E402

ADDRESS = ["address_street", "city", "state", "zipcode"]
SHOWN = ["listing_id", "city", "address_street", "parcel_number", "sale_date", "sale_price",
         "list_date", "contract_date", "tax_assessed_value", "living_area_sqft", "miles_to_campus"]


def main() -> int:
    data = HERE.parent / "data"
    csv = data / f"{B.STEM}.csv"
    before = M.load(csv)
    print(f"Loaded {len(before):,} rows from {csv}")

    after = B.drop_double_records(before, ADDRESS, "listing_id")
    removed = before.loc[before.index.difference(after.index)]
    if removed.empty:
        print("Nothing to remove: the file is already fixed.")
        return 0

    # Each removed row beside the record kept for the same sale.
    kept = after.set_index(ADDRESS).loc[removed.set_index(ADDRESS).index].reset_index()
    pairs = pd.concat([kept[SHOWN].add_prefix("kept_"), removed[SHOWN].reset_index(drop=True).add_prefix("removed_")], axis=1)
    pairs.to_csv(HERE / "removed_double_records.csv", index=False)

    out = B.normalize_types(after)
    print(f"Removed {len(removed):,} rows; {len(out):,} remain. Writing files:")
    written = [B.write_csv(out, data), B.write_sqlite(out, data), B.write_xlsx(out, data)]
    parquet, duck = B.write_parquet(out, data), B.write_duckdb(out, data)
    written += [p for p in (parquet, duck) if p]
    for path in written:
        print(f"  {path.name:<40} {path.stat().st_size / 1_048_576:>7.2f} MB")

    if not M.verify(M.load(csv), parquet, duck):
        print("\nFAILED: see above. Do not publish these files.")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
