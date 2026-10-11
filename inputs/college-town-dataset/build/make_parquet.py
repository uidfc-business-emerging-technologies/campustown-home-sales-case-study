#!/usr/bin/env python3
"""
Write the Parquet and DuckDB copies of the college-town home sales dataset from the
published CSV, then check both against it.

    pip install pyarrow duckdb
    python build/make_parquet.py                 # from the package root, or anywhere

With no arguments it reads ../data/college_town_home_sales.csv relative to this script and
writes the two files beside that CSV. --input and --outdir override either.

The schema is not repeated here. Column order, types, the primary key, the indexes and the
writers themselves all come from build_dataset.py in this folder, so these two files are
identical in structure to the ones a full rebuild produces. The CSV is converted rather than
rebuilt, so the values cannot drift from the released dataset.

Both files are read back and compared with the CSV value by value, column by column, and the
script exits with an error if anything differs.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_dataset as B  # noqa: E402


def default_input() -> Path:
    for candidate in (HERE.parent / "data" / f"{B.STEM}.csv", HERE / f"{B.STEM}.csv", Path(f"{B.STEM}.csv")):
        if candidate.exists():
            return candidate
    return HERE.parent / "data" / f"{B.STEM}.csv"


def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False, na_values=[""])
    if list(df.columns) != B.FINAL_COLS:
        raise SystemExit(f"{path} does not have the expected {len(B.FINAL_COLS)} columns in order. "
                         f"Is it from build {B.BUILD_VERSION}?")
    return B.normalize_types(df)


def as_text(s: pd.Series) -> pd.Series:
    """One comparable text form per value, whatever type a reader returned."""
    def one(v):
        if v is None or v is pd.NA or (not isinstance(v, str) and pd.isna(v)):
            return None
        if hasattr(v, "isoformat"):                      # date, datetime, Timestamp
            return v.isoformat()[:10]
        if isinstance(v, float):                         # includes numpy float64
            return repr(float(v))
        if hasattr(v, "item"):                           # other numpy scalars
            return str(v.item())
        return str(v)
    return s.astype(object).map(one)


def compare(label: str, expected: pd.DataFrame, got: pd.DataFrame, types: dict, want_types: dict) -> list[str]:
    problems = []
    if list(got.columns) != B.FINAL_COLS:
        problems.append("column order differs")
    if len(got) != len(expected):
        problems.append(f"row count {len(got):,} vs {len(expected):,}")
    bad_types = {c: (types.get(c), want_types[c]) for c in B.FINAL_COLS if types.get(c) not in want_types[c]}
    if bad_types:
        problems.append("types: " + ", ".join(f"{c} is {t} (want {w[0]})" for c, (t, w) in bad_types.items()))
    if not problems:
        try:
            # Readers hand back integer columns with blanks as floats, and dates as dates or
            # timestamps. Put them through the same normalization as the CSV first.
            got = B.normalize_types(got.set_index("listing_id").loc[expected["listing_id"]].reset_index())
        except Exception as exc:                          # e.g. a non-integral value in an int column
            problems.append(f"could not normalize the file's values: {exc}")
            got = expected.iloc[0:0]
        for c in (B.FINAL_COLS if len(got) else []):
            if not as_text(got[c]).equals(as_text(expected[c])):
                diff = int((as_text(got[c]).fillna("<null>") != as_text(expected[c]).fillna("<null>")).sum())
                problems.append(f"{c}: {diff:,} values differ")
    print(f"  {label:<8} {'PASS' if not problems else 'FAIL'}  "
          f"{len(got):,} rows x {got.shape[1]} columns, every value and type checked against the CSV")
    for p in problems:
        print(f"           - {p}")
    return problems


def parquet_types() -> dict:
    t = {}
    for c in B.FINAL_COLS:
        if c in B.DATE_COLS:
            t[c] = ("date32[day]", "DATE")
        elif c in B.INT_COLS or c in B.FLAG_COLS:
            t[c] = ("int64", "BIGINT")
        elif c in B.FLOAT_COLS:
            t[c] = ("double", "DOUBLE")
        else:
            t[c] = ("string", "large_string", "VARCHAR")
    return t


def verify(expected: pd.DataFrame, parquet: Path | None, duck: Path | None) -> bool:
    print("\nVerification:")
    problems = []
    if parquet:
        try:
            import pyarrow.parquet as pq
            schema = pq.read_schema(parquet)
            types = {f.name: str(f.type) for f in schema}
            got = pq.read_table(parquet).to_pandas(date_as_object=True)
        except ImportError:                                   # no pyarrow: read it with duckdb
            try:
                import duckdb
            except ImportError:
                print("  Parquet  NOT VERIFIED: install pyarrow or duckdb to check the file")
                return False
            con = duckdb.connect()
            src = f"read_parquet('{parquet.as_posix()}')"
            types = {r[0]: r[1] for r in con.execute(f"DESCRIBE SELECT * FROM {src}").fetchall()}
            got = con.execute(f"SELECT * FROM {src}").df()
            con.close()
        problems += compare("Parquet", expected, got, types, parquet_types())
    if duck:
        import duckdb
        con = duckdb.connect(str(duck), read_only=True)
        types = dict(con.execute(
            f"SELECT column_name, data_type FROM information_schema.columns "
            f"WHERE table_name = '{B.TABLE_NAME}' ORDER BY ordinal_position").fetchall())
        got = con.execute(f"SELECT * FROM {B.TABLE_NAME}").df()
        pk = con.execute(
            f"SELECT constraint_column_names FROM duckdb_constraints() "
            f"WHERE table_name = '{B.TABLE_NAME}' AND constraint_type = 'PRIMARY KEY'").fetchall()
        idx = {r[0] for r in con.execute(
            f"SELECT index_name FROM duckdb_indexes() WHERE table_name = '{B.TABLE_NAME}'").fetchall()}
        con.close()
        want = {c: (B.duckdb_type(c),) for c in B.FINAL_COLS}
        problems += compare("DuckDB", expected, got, types, want)
        want_idx = {f"idx_{'_'.join(cols)}" for cols in B.INDEXES}
        if not pk or list(pk[0][0]) != ["listing_id"]:
            problems.append("DuckDB primary key")
            print("           - primary key on listing_id is missing")
        if want_idx - idx:
            problems.append("DuckDB indexes")
            print(f"           - missing indexes: {sorted(want_idx - idx)}")
    return not problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", default=None, type=Path, help="published CSV (default: ../data/ next to this script)")
    ap.add_argument("--outdir", default=None, type=Path, help="where to write (default: beside the CSV)")
    args = ap.parse_args()

    args.input = args.input or default_input()
    if not args.input.exists():
        raise SystemExit(f"Input CSV not found: {args.input}\nPass it explicitly, e.g.\n"
                         f"    python build/make_parquet.py --input data/{B.STEM}.csv --outdir data")
    args.outdir = args.outdir or args.input.resolve().parent
    args.outdir.mkdir(parents=True, exist_ok=True)

    df = load(args.input)
    print(f"Loaded {len(df):,} rows, {df.shape[1]} columns from {args.input}")
    parquet = B.write_parquet(df, args.outdir)
    duck = B.write_duckdb(df, args.outdir)
    for path in (p for p in (parquet, duck) if p):
        print(f"  {path.name:<40} {path.stat().st_size / 1_048_576:>7.2f} MB")
    if not (parquet or duck):
        return 1
    if not verify(df, parquet, duck):
        print("\nFAILED: see above. Do not publish these files.")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
