"""Run every reference computation with one command.

    python run_all.py [--data PATH]

1. Checks the inputs (handoff section 4) and stops if any check fails.
2. Reproduces Appendix A and stops if any figure differs.
3. Computes every Variation 2 figure and the common wrong answers.
4. Writes the answer key workbook, its charts and the markdown source of the
   Word answer key, and fills the data figures into the instructor orientation
   (build the .docx files with output/source/word-documents/build.js).
5. Writes the summary files the reference sites read, and stops if any site's own
   scripts/build_data.py would produce a different file.
"""

import argparse
import json
import sys
from pathlib import Path

import answer_key
import appendix_a
import orientation
import sites
from definitions import DEFAULT_DATA, REPO_ROOT, add_derived, load

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
FORBIDDEN_FILES = {"raw_extract.csv", "raw_events.csv"}
SITES = REPO_ROOT / "output" / "instructor" / "reference-sites"


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

    _, answers = answer_key.write_all(df, site_paths=[SITES / "v2-six-questions" / "data" / "answers.json"])
    print(f"Wrote {answer_key.WORKBOOK.relative_to(REPO_ROOT)} and {answer_key.MARKDOWN.relative_to(REPO_ROOT)}.")
    path, figures = orientation.write(df)
    (RESULTS / "orientation_figures.json").write_text(json.dumps(figures, indent=1) + "\n")
    print(f"Wrote {path.relative_to(REPO_ROOT)} with {len(figures)} computed figures.")

    summaries = {
        "v1-old-homes-close-in": ("age.json", sites.v1_summary(df), {"indent": 1}),
        "v2-six-questions": ("answers.json", answers, {"indent": 1}),
        "v3-close-to-campus": ("sales.json", sites.v3_sales(df), {"separators": (",", ":")}),
    }
    for folder, (name, data, style) in summaries.items():
        text = json.dumps(data, **style) + ("\n" if "indent" in style else "")
        (SITES / folder / "data" / name).write_text(text)
        diff = sites.first_difference(sites.run_site_script(SITES / folder), json.loads(text))
        if diff:
            sys.exit(f"{folder}: the site's own build script disagrees with the reference code at {diff}")
        print(f"Wrote {folder}/data/{name}; the site's own build script produces the same file.")


if __name__ == "__main__":
    main()
