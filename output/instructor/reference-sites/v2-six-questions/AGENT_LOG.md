# Agent log

This log records how this sample site was actually built with an AI coding agent, as a model of the log the case asks students to keep.

## 2026-10-09: Load and check the data

- **Asked:** "Read the data description sheet and the six Variation 2 questions. Load the Parquet file and confirm it matches the sheet before computing anything."
- **Agent produced:** a check that the file has 35,529 rows and 34 columns and that `listing_id` is unique. It then recomputed the campus-level medians in the dataset's instructor reference figures (sale price, price per square foot, days on market).
- **Checked:** every median matched except Iowa days on market, 23.5 against 24 in the reference. The reference rounds to whole days, so this is rounding, not an error. We kept 23.5.

## 2026-10-09: Compute the answers

- **Asked:** "Write `scripts/build_data.py` to compute all six answers with the case's definitions and save them to `data/answers.json`. Don't type any numbers into the page by hand."
- **Agent produced:** the script, with the price floor ($1,000), the 100 sq ft floor, the 20-sale rule and the distance bands as named constants at the top.
- **Checked:** the counts in the output against the description sheet: 28,043 sales with days on market, and 240 sales at 103 repeated addresses. Both match.

## 2026-10-09: Question 5 explanation (the agent's assumption was wrong)

- **Asked:** "What could explain the gap between assessed value and sale price?"
- **Agent produced:** a first plan built on state assessment rules, starting from the assumption that Illinois would sit near one third, because Illinois assesses most property at a third of market value.
- **Caught:** the data shows Illinois at 0.82, not about 0.33, so the assessed values in this dataset are not on that basis. We dropped the claim. We kept explanations only for the areas the data actually singles out (Penn State 0.18, Michigan 0.33, UC Davis 1.00), and found a source for each one. Lesson: check a plausible-sounding rule against the numbers before writing it down.

## 2026-10-09: Build the page

- **Asked:** "Build the page in plain HTML, CSS and JavaScript, with no frameworks. Each question gets an answer, two or three key figures, a chart and a table. Add a Data notes section."
- **Agent produced:** `index.html`, `css/style.css`, `js/charts.js` (small SVG chart helpers) and `js/app.js`.
- **Checked:** the Question 1 answer said Georgia's homes are larger than Florida's. We asked the agent to prove it, and it added median square feet to the data (1,902 against 1,756) and to the table.
- **Caught:** the Question 3 answer listed only Florida, Georgia and Iowa as areas where a farther band costs more. Re-reading the table showed UW-Madison (1 to 2 miles) and Purdue (5 to 10 miles) do too, so we fixed the sentence.

## 2026-10-09: Test on a phone and in dark mode

- **Asked:** "Test the page at 375 and 1280 pixels wide, in light and dark mode, served from a subfolder the way GitHub Pages serves it. Report console errors and any sideways scrolling."
- **Found and fixed:**
    - The page scrolled sideways on a phone because a grid column sized itself to its longest line. Fixed with `minmax(0, 1fr)` columns.
    - The rank chart's labels were cut off on a phone. On narrow screens it now shows names only, and the values stay in the tooltip and table.
    - In Question 5, the value labels for 0.97 and 1.00 overlapped the reference line. They now sit to the right of the line.
- **Result:** no console errors and no sideways scrolling at either width, in either theme.

## 2026-10-09: Check three numbers a second way

- **Asked:** "Recompute three headline numbers with SQL in DuckDB, directly from the Parquet file, without using `build_data.py`."
- **Result:** all three match. See "How we checked our numbers" in the README.
