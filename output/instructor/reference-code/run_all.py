"""Run every reference computation with one command.

    python run_all.py [--data PATH]

1. Checks the inputs (handoff section 4) and stops if any check fails.
2. Reproduces Appendix A and stops if any figure differs.
3. Writes the results to results/.
"""

import argparse
import sys
from pathlib import Path

import appendix_a
from definitions import DEFAULT_DATA, REPO_ROOT, add_derived, load

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
FORBIDDEN_FILES = {"raw_extract.csv", "raw_events.csv"}


def input_checks(raw):
    """Handoff section 4: shape, unique key, and no raw build inputs in output/."""
    problems = []
    if raw.shape != (35_529, 34):
        problems.append(f"expected 35,529 rows and 34 columns, found {raw.shape[0]:,} and {raw.shape[1]}")
    if not raw["listing_id"].is_unique:
        problems.append("listing_id is not unique")
    leaked = [p for p in (REPO_ROOT / "output").rglob("*") if p.name in FORBIDDEN_FILES]
    if leaked:
        problems.append(f"raw build inputs found in output/: {leaked}")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data", default=DEFAULT_DATA, help="dataset file (.parquet or .csv)")
    args = parser.parse_args()

    raw = load(args.data)
    problems = input_checks(raw)
    if problems:
        sys.exit("Input check failed. Stop and report to Park:\n- " + "\n- ".join(problems))
    print(f"Input checks passed: {raw.shape[0]:,} rows, {raw.shape[1]} columns, listing_id unique.")

    df = add_derived(raw)
    results, failures = appendix_a.check(raw, df)
    RESULTS.mkdir(exist_ok=True)
    results.to_csv(RESULTS / "appendix_a_check.csv", index=False)
    if len(failures):
        print(failures.to_string(index=False))
        sys.exit(f"{len(failures)} Appendix A figure(s) differ. Stop and report to Park.")
    print(f"Appendix A reproduced: {len(results)} of {len(results)} figures match.")


if __name__ == "__main__":
    main()
