# Agent log

This log records how this site was actually built with an AI coding agent, as a model of the log the case asks students to keep.

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

## 2026-10-11: Follow the setup guide's layout, and check the script against a second one

- **Asked:** "Keep the data the way the setup guide says: the CSV in `data/` and the description sheet in `docs/`. Make `scripts/build_data.py` read the CSV, with ZIP, FIPS and parcel numbers as text."
- **Agent produced:** the updated script, with every rule as a named constant at the top.
- **Checked:** its `data/answers.json` is identical, value for value, to a second calculation written separately.

## 2026-10-11: Question 4 now uses a listing window

- **Asked:** "The case now limits Question 4 to homes listed from April 1, 2023 through March 31, 2025. Update the answer."
- **Agent produced:** the new figures. April and May are now the fastest months (6 days) and December the slowest (21), where the all-years version had a three-way tie at 7 days and December at 25.
- **Checked:** why the window matters. Homes listed in 2021 and 2022 appear in the data only if they sold after March 2023, so their median days on market runs from about 90 to 473 days, and they pulled the late-year months up.

## 2026-10-11: Numbers typed into the page (we broke our own rule)

- **Caught:** our first instruction said "Don't type any numbers into the page by hand", but the answer paragraphs, key figures and data notes all had numbers typed into `index.html`. Several were now wrong after the Question 4 change.
- **Asked:** "Fill in every number in the text from `data/answers.json`, and work out the names (fastest areas, the exception in Question 3) from the data too."
- **Result:** no number in `index.html` is typed by hand. If a figure changes, the sentence changes with it.

## 2026-10-11: Small groups in Question 6 (the agent missed the rule)

- **Caught:** the Question 6 chart and table showed a median distance for areas with only 2 to 6 sales at repeated addresses. The case says a median from fewer than 20 sales must show "fewer than 20 sales".
- **Fixed:** those cells now say "fewer than 20 sales", the chart shows only Penn State, Virginia and all areas together, and the counts are still shown, as the case asks.

## 2026-10-11: What the repeated addresses are

- **Asked:** "The description sheet says the 240 sales at repeated addresses are separate condo units. Check whether that holds in every area."
- **Found:** it holds in State College, where each unit has its own parcel number and price. But in 87 of the 103 addresses, the two sales have prices within 1% and sale dates within 90 days, the build notes' own test for one sale recorded twice. 79 of those are around Virginia, mostly new homes, with one row from the listing and one from the county record.
- **Decided:** count every sale, because the question defines the groups that way, but say what we found in the Question 6 answer and the data notes. This also explains why Virginia's repeated addresses look far from campus.

## 2026-10-11: Rules for "falls" and "far from 1", and the sources

- **Asked:** "The case now asks us to say what we count as falling (Question 3) and as far from 1 (Question 5). Put both rules in the data notes. Then check each Question 5 source."
- **Checked:** the Michigan brochure and the California question-and-answer sheet we cited were secondary. We replaced them with the Michigan State Tax Commission's assessing guide, the California Board of Equalization's handbook, and the Pennsylvania Department of Revenue's list of common level ratio factors (Centre County 6.10, about one sixth of market value).

## 2026-10-11: Final test

- **Asked:** "Test again at 375 and 1280 pixels, light and dark, served from a subfolder, using only the keyboard for the charts. Then compare every table cell with the answer key."
- **Found and fixed:** on a phone, a chart tooltip closed as soon as it opened, because moving keyboard focus to a mark scrolled the page and the scroll closed the tooltip. A tooltip opened by the keyboard now follows its mark instead.
- **Result:** no console errors or sideways scrolling, and every table cell and every number in the text matches the answer key.
