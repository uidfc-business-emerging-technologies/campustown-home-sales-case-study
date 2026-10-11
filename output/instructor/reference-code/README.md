# Reference code

Python code that computes every figure in the instructor materials from the College-town home sales dataset (version 1.0). It runs offline and gives the same output every time.

## Run it

Python 3.11 or later.

```bash
python -m venv .venv
source .venv/bin/activate          # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run_all.py
```

`run_all.py` reads `output/students/data/college_town_home_sales.csv` (pass `--data PATH` to use another copy; the Parquet file works too). In one command it:

1. Checks the inputs: 35,529 rows, 34 columns, a unique `listing_id`, and no raw build files anywhere in `output/`. It stops if any check fails.
2. Reproduces all 82 figures in Appendix A of the handoff (the data description sheet and `reference_figures.md`) and stops if any figure differs. Results: `results/appendix_a_check.csv`.
3. Computes every Variation 2 figure and the common wrong answers.
4. Writes the answer key workbook (`instructor/Variation 2 Answer Key.xlsx`), one chart per question, and the markdown source of the Word answer key (`source/word-documents/variation2_answer_key.md`).
5. Writes the summary file each reference site reads, and stops if a site's own `scripts/build_data.py` would produce a different file.

Then build the Word answer key from its markdown (needs Node.js and the `docx` package):

```bash
cd ../../source/word-documents
npm install docx@9.7.1
node build.js
```

## Files

| File | What it does |
|---|---|
| `run_all.py` | The one command |
| `definitions.py` | Loads the data with consistent types, and the shared rules: valid sale, price per square foot, days on market, rounding |
| `appendix_a.py` | The Appendix A figures and the check |
| `variation2.py` | The six Variation 2 questions under the case's definitions |
| `wrong_answers.py` | The figures that common mistakes produce, for the answer key |
| `answer_key.py` | Writes the workbook, the charts, the key's markdown and the V2 site's `answers.json` |
| `sites.py` | The V1 and V3 site summaries, and the check against each site's own script |
| `v2_data_checks.py` | The section 7 checks of the Variation 2 questions; writes `results/variation2_checks.txt` |
| `recompute_student_number.ipynb` | For grading Variations 1 and 3: recomputes a student's number under the student's own definitions, with three worked examples |
| `site_tests/` | Browser and number tests for the reference sites (see below) |
| `requirements.txt` | Pinned packages for `run_all.py` |
| `requirements-notebook.txt` | Adds Jupyter for the notebook |

## Test the reference sites

Serve the folder that holds the three sites from a subfolder, the way GitHub Pages serves a project site, then run the browser test (needs Node.js and Playwright) and the number check:

```bash
mkdir -p /tmp/serve && ln -s "$(pwd)/../reference-sites" /tmp/serve/repo-name
(cd /tmp/serve && python -m http.server 8765 &)
cd site_tests
node check_sites.js http://localhost:8765/repo-name screenshots texts
python check_numbers.py texts
```

`check_sites.js` loads each site at 375 and 1280 pixels wide, in light and dark, and fails on any console error, failed request or sideways scrolling. It also exercises every control and saves a screenshot of each view. `check_numbers.py` compares every number the sites show with figures computed here: Variation 2 against the answer key, Variation 1 against its summary, and Variation 3 recomputed from the full dataset at five settings.
