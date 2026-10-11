"""Export the two raw build inputs from the source database, then optionally verify them.

Writes, next to this script:
    raw_extract.csv   Query 1 in extract_query.sql, one row per property   (35,822 rows)
    raw_events.csv    Query 2 in extract_query.sql, one row per event       (284,955 rows)

With --verify, it then rebuilds the dataset into a temporary folder with build_dataset.py
and checks that the rebuilt CSV is byte-identical to data/college_town_home_sales.csv.
A match proves the raw files are the ones the published dataset was built from.

Usage, from the dataset package root (the folder that holds build/ and data/):

    pip install "psycopg[binary]" pandas openpyxl pyarrow duckdb
    export DATABASE_URL='postgresql://USER:PASSWORD@HOST:PORT/postgres?sslmode=require'
    python build/export_raw.py --verify

DATABASE_URL is a connection string for the PlanetScale Postgres database
`hasdata-data-collection` (organization `subwaymatch`, branch `main`). Create a role with
read access on the database's Connect page in the PlanetScale dashboard and copy its
connection string. Keep it in your shell only: never write it into a file in this repository.

The queries are the same as in extract_query.sql with one formatting difference: the five
boolean columns are cast to text, so the CSV holds `true` and `false` (what build_dataset.py
expects) rather than the `t` and `f` that COPY writes for a boolean column.
"""
import argparse
import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

FILTER = "status IN ('SOLD', 'RECENTLY_SOLD') AND COALESCE(address_undisclosed, false) = false"

BOOLEAN_COLS = ["reso_basement_yn", "reso_has_garage", "reso_has_cooling",
                "reso_has_heating", "reso_has_fireplace"]

EXTRACT_COLS = [
    "property_id", "address_street", "address_city", "address_state", "address_zipcode",
    "address_county", "county_fips", "parcel_number", "latitude", "longitude", "date_posted",
    "price", "home_type", "beds", "baths", "living_area", "lot_size", "year_built",
    "reso_stories", "reso_basement_yn", "reso_has_garage", "reso_garage_parking_capacity",
    "reso_has_cooling", "reso_has_heating", "reso_has_fireplace", "reso_architectural_style",
    "reso_roof_type", "reso_tax_annual_amount", "reso_tax_assessed_value",
    "reso_high_school_district",
]

QUERY_EXTRACT = (
    "SELECT "
    + ", ".join(f"{c}::text AS {c}" if c in BOOLEAN_COLS else c for c in EXTRACT_COLS)
    + f" FROM zillow_properties WHERE {FILTER} ORDER BY property_id"
)

QUERY_EVENTS = """
SELECT z.property_id,
       (a.e->>'date')::date AS event_date,
       a.e->>'event'        AS event
FROM zillow_properties z
CROSS JOIN LATERAL jsonb_array_elements(
    CASE WHEN jsonb_typeof(z.price_history) = 'array' THEN z.price_history ELSE '[]'::jsonb END
) WITH ORDINALITY AS a(e, o)
WHERE z.status IN ('SOLD', 'RECENTLY_SOLD') AND COALESCE(z.address_undisclosed, false) = false
ORDER BY z.property_id, event_date, a.o DESC
"""

EXPECTED_ROWS = {"raw_extract.csv": 35_822, "raw_events.csv": 284_955}


def sha1(path: Path) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def export(url: str) -> None:
    import psycopg  # imported here so --verify-only runs without it

    with psycopg.connect(url) as conn, conn.cursor() as cur:
        for name, sql in (("raw_extract.csv", QUERY_EXTRACT), ("raw_events.csv", QUERY_EVENTS)):
            path = HERE / name
            with open(path, "wb") as f:
                with cur.copy(f"COPY ({sql}) TO STDOUT WITH (FORMAT csv, HEADER)") as copy:
                    for data in copy:
                        f.write(data)
            with open(path, "rb") as f:
                rows = sum(1 for _ in f) - 1
            status = "ok" if rows == EXPECTED_ROWS[name] else f"EXPECTED {EXPECTED_ROWS[name]:,}"
            print(f"  wrote {name:<16} {rows:>9,} rows  {status}")
            if rows != EXPECTED_ROWS[name]:
                raise SystemExit("Row count differs from the build notes. Stop and check the source table.")


def verify() -> bool:
    published = ROOT / "data" / "college_town_home_sales.csv"
    with tempfile.TemporaryDirectory() as tmp:
        cmd = [sys.executable, str(HERE / "build_dataset.py"),
               "--input", str(HERE / "raw_extract.csv"),
               "--events", str(HERE / "raw_events.csv"),
               "--outdir", tmp]
        print("\nRebuilding into a temporary folder to verify...")
        subprocess.run(cmd, check=True)
        rebuilt = Path(tmp) / "college_town_home_sales.csv"
        same = sha1(rebuilt) == sha1(published)
    print("\nVerification:", "PASS, the rebuilt CSV is byte-identical to the published one"
          if same else "FAIL, the rebuilt CSV differs from data/college_town_home_sales.csv")
    return same


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verify", action="store_true", help="rebuild the dataset and compare it with the published CSV")
    ap.add_argument("--verify-only", action="store_true", help="skip the export and only verify existing raw files")
    args = ap.parse_args()

    if not args.verify_only:
        url = os.environ.get("DATABASE_URL")
        if not url:
            raise SystemExit("Set DATABASE_URL to the database's connection string first (see the top of this file).")
        print("Exporting raw build inputs:")
        export(url)
    if args.verify or args.verify_only:
        return 0 if verify() else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
