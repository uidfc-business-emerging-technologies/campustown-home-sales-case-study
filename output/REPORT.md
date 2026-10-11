# Report to Park: Campus Comps case package

Date: October 11, 2026. This report covers the work in `HANDOFF.md`, sections 1 to 14. Everything is in `output/`, and the pull request on the branch `claude/new-session-re1c94` shows the history one step at a time.

## 1. Summary

**What was built:**

- **Student materials, revised after a pilot of each variation.** The three case documents and the setup guide are rebuilt from an updated `content.js`. Section 4 lists every change and its reason. The students' copy of the data description sheet drops only "Suggested starting questions", in markdown and Word. The dataset is copied unchanged.
- **Reference code.** One command (`python run_all.py`) checks the inputs, reproduces all 82 Appendix A figures, and computes every Variation 2 figure and the common wrong answers. It also writes the answer key workbook and charts, fills in the orientation's figures, and writes each reference site's data file. It runs offline, and a clean environment produces byte-identical output. A notebook recomputes a student's number under the student's own definitions, with three worked examples.
- **Variation 2 answer key,** in Word and a matching Excel workbook. It covers the figures, a chart, a model answer, the common wrong answers with the figures they produce, and a tolerance for each question.
- **Instructor orientation** (section 9.1) and the **post-assignment survey** (Appendix B).
- **Three reference sites,** one per variation, each with a model README and agent log. Each was tested at 375 and 1280 pixels, in light and dark, served from a subfolder. Every number they show was checked against the reference code.

**Two findings you should know about first:**

1. **Many repeated addresses are one sale recorded twice, not separate condo units.** The description sheet says the 240 sales at 103 repeated addresses are condo or apartment units. That holds in State College. But 87 of the 103 addresses (174 rows) meet the build notes' own test for a duplicate: two rows, prices within 1% and sale dates within 90 days. 79 of them are around Virginia, mostly new homes. In most pairs, one row came from the listing and the other from the county record, with a different parcel number, so the build's parcel check missed them. The Variation 2 pilot found this on its own. I did not change the data. Section 6 sets out the options.
2. **Question 4 needed a listing window.** Listings from 2021 and 2022 appear only if they sold after March 2023, so their median days on market runs from about 90 to 473 days. Listings from late 2025 are cut off before slow sales close. Question 4 now covers homes listed from April 1, 2023 through March 31, 2025. That window covers each calendar month exactly twice.

**What you need to do next:**

1. Decide the open decisions in section 6, starting with the repeated addresses.
2. Replace "[Author name]" in `source/case-documents/content.js` and `source/word-documents/build.js`, then rebuild (`output/README.md` gives the commands).
3. Confirm the license (CC BY-NC-SA 4.0).
4. Review the student document changes in section 4.
5. Merge the pull request, then publish with GitHub Pages ("Deploy from a branch", main, root). Each site will be at `https://OWNER.github.io/REPOSITORY/output/instructor/reference-sites/FOLDER/`. No file in the repository uses Liquid template syntax, so the default GitHub Pages build will not fail on it.
6. Open one reference site in a real browser on a phone. The tests used a headless browser at phone width, not a phone.

## 2. Contents

`output/`, one line per file:

- `README.md`: What is in the package, and how to rebuild every generated file
- `REPORT.md`: This report
- `instructor/Instructor Orientation.docx`: Instructor orientation (section 9.1)
- `instructor/Post-Assignment Survey.docx`: Post-assignment survey (Appendix B), the same for every variation
- `instructor/Variation 2 Answer Key.docx`: Variation 2 answer key: figures, charts, model answers, common wrong answers, tolerances
- `instructor/Variation 2 Answer Key.xlsx`: The same answer key as a workbook, one sheet per question
- `instructor/reference-code/README.md`: How to run the reference code and the site tests
- `instructor/reference-code/acceptance_checks.py`: Section 13 document checks: case document diff, answers in student files, words, dashes, Word file hygiene
- `instructor/reference-code/answer_key.py`: Writes the answer key workbook, charts, key markdown and the V2 site's answers.json
- `instructor/reference-code/appendix_a.py`: The Appendix A figures and the check
- `instructor/reference-code/definitions.py`: Loads the data with consistent types; shared rules and rounding
- `instructor/reference-code/orientation.py`: Computes the 43 data figures in the orientation and fills them in
- `instructor/reference-code/recompute_student_number.ipynb`: Notebook: recompute a student's number under the student's own definitions (three worked examples)
- `instructor/reference-code/requirements-notebook.txt`: Pinned packages for the notebook
- `instructor/reference-code/requirements.txt`: Pinned packages for run_all.py
- `instructor/reference-code/results/acceptance_checks.txt`: Output of acceptance_checks.py
- `instructor/reference-code/results/appendix_a_check.csv`: All 82 Appendix A figures, expected against computed
- `instructor/reference-code/results/case_document_diff.txt`: Text diff of the three case documents
- `instructor/reference-code/results/orientation_figures.json`: The 43 figures filled into the orientation
- `instructor/reference-code/results/variation2_checks.txt`: Section 7 evidence for each Variation 2 question
- `instructor/reference-code/run_all.py`: The one command
- `instructor/reference-code/site_tests/check_numbers.py`: Compares every number the sites show with the reference code
- `instructor/reference-code/site_tests/check_sites.js`: Headless browser test: subfolder, 375 and 1280 px, light and dark, console errors, controls, screenshots
- `instructor/reference-code/site_tests/site_controls.js`: The controls on each site and how the test exercises them
- `instructor/reference-code/sites.py`: The V1 and V3 site data files, and the check against each site's own script
- `instructor/reference-code/v2_data_checks.py`: Section 7 checks of the Variation 2 questions
- `instructor/reference-code/variation2.py`: The six Variation 2 questions under the case's definitions
- `instructor/reference-code/wrong_answers.py`: Figures produced by common mistakes, for the answer key
- `instructor/reference-sites/v1-old-homes-close-in/AGENT_LOG.md`: Model agent log
- `instructor/reference-sites/v1-old-homes-close-in/README.md`: Model README with every required item
- `instructor/reference-sites/v1-old-homes-close-in/css/style.css`: Styles, light and dark
- `instructor/reference-sites/v1-old-homes-close-in/data/age.json`: Every figure the V1 page shows (written by run_all.py)
- `instructor/reference-sites/v1-old-homes-close-in/data/college_town_home_sales.csv`: The dataset, as the setup guide places it
- `instructor/reference-sites/v1-old-homes-close-in/docs/data_description_sheet.md`: The students' description sheet, as the setup guide places it
- `instructor/reference-sites/v1-old-homes-close-in/index.html`: The page
- `instructor/reference-sites/v1-old-homes-close-in/js/app.js`: Reads the data file and draws the page
- `instructor/reference-sites/v1-old-homes-close-in/js/charts.js`: SVG chart helpers (no libraries)
- `instructor/reference-sites/v1-old-homes-close-in/scripts/build_data.py`: The site's own script that makes its data file
- `instructor/reference-sites/v2-six-questions/AGENT_LOG.md`: Model agent log
- `instructor/reference-sites/v2-six-questions/README.md`: Model README with every required item
- `instructor/reference-sites/v2-six-questions/css/style.css`: Styles, light and dark
- `instructor/reference-sites/v2-six-questions/data/answers.json`: Every figure the V2 page shows (written by run_all.py)
- `instructor/reference-sites/v2-six-questions/data/college_town_home_sales.csv`: The dataset, as the setup guide places it
- `instructor/reference-sites/v2-six-questions/docs/data_description_sheet.md`: The students' description sheet, as the setup guide places it
- `instructor/reference-sites/v2-six-questions/fonts/OFL-archivo-narrow.txt`: Font license (SIL Open Font License)
- `instructor/reference-sites/v2-six-questions/fonts/OFL-public-sans.txt`: Font license (SIL Open Font License)
- `instructor/reference-sites/v2-six-questions/fonts/archivo-narrow.woff2`: Font file, saved locally
- `instructor/reference-sites/v2-six-questions/fonts/public-sans.woff2`: Font file, saved locally
- `instructor/reference-sites/v2-six-questions/index.html`: The page
- `instructor/reference-sites/v2-six-questions/js/app.js`: Reads the data file and draws the page
- `instructor/reference-sites/v2-six-questions/js/charts.js`: SVG chart helpers (no libraries)
- `instructor/reference-sites/v2-six-questions/scripts/build_data.py`: The site's own script that makes its data file
- `instructor/reference-sites/v3-close-to-campus/AGENT_LOG.md`: Model agent log
- `instructor/reference-sites/v3-close-to-campus/README.md`: Model README with every required item
- `instructor/reference-sites/v3-close-to-campus/css/style.css`: Styles, light and dark
- `instructor/reference-sites/v3-close-to-campus/data/college_town_home_sales.csv`: The dataset, as the setup guide places it
- `instructor/reference-sites/v3-close-to-campus/data/sales.json`: The 12 months of sales the V3 page filters (written by run_all.py)
- `instructor/reference-sites/v3-close-to-campus/docs/data_description_sheet.md`: The students' description sheet, as the setup guide places it
- `instructor/reference-sites/v3-close-to-campus/fonts/OFL-bricolage-grotesque.txt`: Font license (SIL Open Font License)
- `instructor/reference-sites/v3-close-to-campus/fonts/OFL-instrument-sans.txt`: Font license (SIL Open Font License)
- `instructor/reference-sites/v3-close-to-campus/fonts/bricolage-grotesque.woff2`: Font file, saved locally
- `instructor/reference-sites/v3-close-to-campus/fonts/instrument-sans.woff2`: Font file, saved locally
- `instructor/reference-sites/v3-close-to-campus/index.html`: The page
- `instructor/reference-sites/v3-close-to-campus/js/app.js`: Reads the data file and draws the page
- `instructor/reference-sites/v3-close-to-campus/js/charts.js`: SVG chart helpers (no libraries)
- `instructor/reference-sites/v3-close-to-campus/scripts/build_data.py`: The site's own script that makes its data file
- `report-screenshots/v1-old-homes-close-in-1280-dark.png`: Screenshot from the final browser test
- `report-screenshots/v1-old-homes-close-in-1280-light.png`: Screenshot from the final browser test
- `report-screenshots/v1-old-homes-close-in-375-dark.png`: Screenshot from the final browser test
- `report-screenshots/v1-old-homes-close-in-375-light.png`: Screenshot from the final browser test
- `report-screenshots/v2-six-questions-1280-dark.png`: Screenshot from the final browser test
- `report-screenshots/v2-six-questions-1280-light.png`: Screenshot from the final browser test
- `report-screenshots/v2-six-questions-375-dark.png`: Screenshot from the final browser test
- `report-screenshots/v2-six-questions-375-light.png`: Screenshot from the final browser test
- `report-screenshots/v3-close-to-campus-1280-dark.png`: Screenshot from the final browser test
- `report-screenshots/v3-close-to-campus-1280-light.png`: Screenshot from the final browser test
- `report-screenshots/v3-close-to-campus-375-dark.png`: Screenshot from the final browser test
- `report-screenshots/v3-close-to-campus-375-light.png`: Screenshot from the final browser test
- `report-screenshots/v3-close-to-campus-controls-used.png`: Screenshot after the test used the controls
- `source/case-documents/build.js`: Builds the case documents and setup guide
- `source/case-documents/content.js`: The revised text of the case documents and setup guide
- `source/word-documents/build.js`: Builds every other Word document from markdown
- `source/word-documents/charts/q1.png`: Answer key chart (written by run_all.py)
- `source/word-documents/charts/q2.png`: Answer key chart (written by run_all.py)
- `source/word-documents/charts/q3.png`: Answer key chart (written by run_all.py)
- `source/word-documents/charts/q4.png`: Answer key chart (written by run_all.py)
- `source/word-documents/charts/q5.png`: Answer key chart (written by run_all.py)
- `source/word-documents/charts/q6.png`: Answer key chart (written by run_all.py)
- `source/word-documents/instructor_orientation.md`: The orientation with its figures filled in (written by run_all.py)
- `source/word-documents/md2docx.js`: Markdown to Word, in the case documents' style
- `source/word-documents/post_assignment_survey.md`: Source of the survey
- `source/word-documents/templates/instructor_orientation.md`: Source of the orientation; edit this one
- `source/word-documents/variation2_answer_key.md`: Source of the answer key (written by run_all.py)
- `students/Case Document - Variation 1 (Open Brief).docx`: Case document, Variation 1: Open Brief
- `students/Case Document - Variation 2 (Specific Questions).docx`: Case document, Variation 2: Specific Questions
- `students/Case Document - Variation 3 (General Instructions).docx`: Case document, Variation 3: General Instructions
- `students/Data Description Sheet.docx`: Students' copy of the description sheet, Word
- `students/Setup Guide - GitHub Pages.docx`: Setup guide, shared by all variations
- `students/data/college_town_home_sales.csv`: Dataset version 1.0, unchanged
- `students/data/college_town_home_sales.duckdb`: Dataset version 1.0, unchanged
- `students/data/college_town_home_sales.parquet`: Dataset version 1.0, unchanged
- `students/data/college_town_home_sales.sqlite`: Dataset version 1.0, unchanged
- `students/data/college_town_home_sales.xlsx`: Dataset version 1.0, unchanged
- `students/data_description_sheet.md`: Students' copy of the description sheet, markdown ("Suggested starting questions" removed)

## 3. Verification

| # | Acceptance check (section 13) | Result | Evidence |
|---|---|---|---|
| 1 | The code reproduces every figure in Appendix A exactly | Pass | 82 of 82 figures match (`instructor/reference-code/results/appendix_a_check.csv`). Two medians fall on a half (Iowa days on market 23.5, UNC miles 3.75), and the code rounds half up, as the published tables do. |
| 2 | The three case documents differ only in the variation label and "Your task" | Pass | Outside "Your task" and the label, the three documents' 108 paragraphs are identical. The diff is below. |
| 3 | No student file contains answers | Pass | All 206 distinctive answer-key values were searched for in the 6 student text files. There are no matches in the case documents or the setup guide. The description sheet, which is unchanged apart from the removed section, already prints 20 of them (details below). |
| 4 | No document mentions peer review or auditing other students' work | Pass | A search of every document and text file in `output/` for "peer", "audit" and "review each other" found nothing (file counts in the evidence below). |
| 5 | No document names a specific AI coding agent product or an agent-specific file name | Pass | The same files were searched for 21 product and file names. |
| 6 | Every .docx opens, is editable, has the funding line, and has no comments, tracked changes or hidden text | Pass | All 8 Word files: funding line in the footer; no comments, tracked changes, hidden text or editing protection; blank author. All 8 open in LibreOffice (page counts below). |
| 7 | No document contains an em dash or an en dash | Pass | None in any Word file or text file in `output/`. |
| 8 | Every number in an instructor document traces to the code's output | Pass | Listed below. |
| 9 | The reference code runs from a clean environment with one command | Pass | In a new virtual environment, `pip install -r requirements.txt` then `python run_all.py` ran in about 28 seconds. Its output was byte-identical to the working copy: the workbook, the charts, the key, the orientation figures and all three site data files. |
| 10 | Each reference site works from a subfolder, with no console errors at 375 and 1280 px, working controls, and numbers that match | Pass | 12 of 12 browser runs pass (3 sites, 2 widths, light and dark). 492 displayed values match the reference code, with none differing. Screenshots: `output/report-screenshots/`. |

The check scripts are `instructor/reference-code/acceptance_checks.py` (checks 2 to 7), `run_all.py` (1 and 9), and `site_tests/check_sites.js` with `site_tests/check_numbers.py` (10).

**Document checks (output of `acceptance_checks.py`):**

```
Every .docx opens cleanly: funding line, no comments, tracked changes, hidden text or protection, blank author
  pass  instructor/Instructor Orientation.docx
  pass  instructor/Post-Assignment Survey.docx
  pass  instructor/Variation 2 Answer Key.docx
  pass  students/Case Document - Variation 1 (Open Brief).docx
  pass  students/Case Document - Variation 2 (Specific Questions).docx
  pass  students/Case Document - Variation 3 (General Instructions).docx
  pass  students/Data Description Sheet.docx
  pass  students/Setup Guide - GitHub Pages.docx
The case documents differ only in the variation label and "Your task" (diff: results/case_document_diff.txt)
  pass  outside "Your task" and the label, the three case documents are identical (108 paragraphs)
No student file contains answers
  pass  searched 6 student files for 206 answer-key values
        Case documents and setup guide: 0 matches.
        Description sheet (both copies, unchanged from the dataset package): 20 matches: $342,000, $370,000, $430,000, $571,000, $625,000, $888,500, 1,351, 1,909, 103, 2,816, 2,854, 240, 3,018, 3,022, 3,664, 3.4, 4,616, 5,630, 5,707, 942
        Each of these is a figure the dataset's own description sheet already prints (city medians that equal single-city campus areas, and the 240 sales at 103 addresses).
Words and characters that must not appear
  pass  no peer review or auditing in 68 documents and text files
  pass  no agent product or agent-specific file name in 68 documents and text files
  pass  no em or en dash in 68 documents and text files
```

**The Word files open** (LibreOffice, converted to PDF): Case Document - Variation 1 (Open Brief) (5 pages); Case Document - Variation 2 (Specific Questions) (6 pages); Case Document - Variation 3 (General Instructions) (5 pages); Data Description Sheet (8 pages); Instructor Orientation (9 pages); Post-Assignment Survey (2 pages); Setup Guide - GitHub Pages (5 pages); Variation 2 Answer Key (20 pages).

**Text diff of the case documents** (Variation 1 against Variations 2 and 3; also in `instructor/reference-code/results/case_document_diff.txt`):

```diff
--- Case Document - Variation 1 (Open Brief).docx
+++ Case Document - Variation 2 (Specific Questions).docx
@@ -1,3 +1,3 @@
 Campus Comps: Building a Data Website with an AI Coding Agent
-Variation 1: Open Brief
+Variation 2: Specific Questions
 [Author name]
@@ -30,5 +30,29 @@
 Your task
-Build a website with visualizations using the College-town home sales dataset.
-What it is about, who it is for, how it looks and how it works are up to you. It can be one page or several, analytical or playful, and focused on one town or on all of them.
-The only requirements are the build and publish requirements below and the items under "What to submit."
+Build a website that answers the six questions below.
+For each question, your site must show:
+The figures that answer it
+At least one chart
+One or two sentences that answer the question in plain words
+Write the answers for a general reader, such as someone thinking about moving to one of these towns. You may arrange the answers in any order and layout, and add anything else you like. Your site must also have a Data notes section that restates the definitions below.
+Definitions
+Use these definitions so every answer can be checked. They take the place of the rules that "The data" section asks you to choose.
+Campus area: the university column. There are 11 campus areas.
+Valid sale: a sale with a sale_price of $1,000 or more. Use only valid sales for figures that involve sale_price (Questions 1, 3 and 5). The other questions use every sale.
+Price per square foot: sale_price divided by living_area_sqft. Compute it for each valid sale with a living area of at least 100 square feet, then take the median of those values. (Dividing a median price by a median living area gives a different, wrong answer.)
+Days on market: the number of days from list_date to contract_date, for sales that have both dates. A blank date is never zero.
+Distance bands, based on miles_to_campus:
+Under 1 mile
+1 to under 2 miles
+2 to under 5 miles
+5 to under 10 miles
+10 miles or more
+Small groups: if a median or a share is based on fewer than 20 sales, show "fewer than 20 sales" in place of it. Always show counts of sales and addresses.
+Medians, not means, unless a question says otherwise.
+Questions
+Price levels. For each campus area, what are the median sale price and the median price per square foot? Which areas are highest and lowest on each measure? Does the ranking change between the two measures, and why might it?
+Speed. For each campus area, what is the median days on market? What share of sales has no days on market because a date is missing? Which areas sell fastest, and how could the missing share affect the comparison?
+Distance. For each campus area, what is the median price per square foot in each distance band? In most areas, does price per square foot fall as the distance from campus grows? Say what you count as falling, and name any area where it does not.
+Timing. Across all areas, pooled together, what is the median days on market for each calendar month in which homes were listed? Use only homes listed from April 1, 2023 through March 31, 2025, so that each calendar month covers exactly two years. Group them by the month of list_date. Which months are fastest, and which are slowest?
+Assessment. For each campus area, what is the median ratio of tax_assessed_value to sale_price, for valid sales with an assessed value above 0? Which areas are far from 1 (say what you count as far), and what could explain the gap? Cite a source for any explanation.
+Buildings. Group sales by street address, city, state and ZIP code. In each campus area, how many addresses have more than one sale, and how many sales do they cover? How does the median miles_to_campus of those sales compare with that of all other sales, across all areas and within each area?
 Build and publish requirements
@@ -111,2 +135,2 @@
 Funded by the University of Illinois-Deloitte Foundation Center for Business Emerging Technologies.	Page 
-Campus Comps case: Variation 1: Open Brief
+Campus Comps case: Variation 2: Specific Questions

--- Case Document - Variation 1 (Open Brief).docx
+++ Case Document - Variation 3 (General Instructions).docx
@@ -1,3 +1,3 @@
 Campus Comps: Building a Data Website with an AI Coding Agent
-Variation 1: Open Brief
+Variation 3: General Instructions
 [Author name]
@@ -30,5 +30,16 @@
 Your task
-Build a website with visualizations using the College-town home sales dataset.
-What it is about, who it is for, how it looks and how it works are up to you. It can be one page or several, analytical or playful, and focused on one town or on all of them.
-The only requirements are the build and publish requirements below and the items under "What to submit."
+Choose one question about the data that matters to a specific kind of user, such as a first-time buyer, a new faculty member or a city planner. Build a website that answers it.
+Your site must:
+State its question and its user at the top of the first page.
+Show at least three headline numbers that answer the question.
+Include at least two charts, tables or maps, with at least one control that changes them, such as a campus picker or a price range.
+Have a Data notes section that says which rows you left out and why, and how each figure is defined.
+A suggested process
+This process is recommended, but not graded.
+Read the data description sheet, then ask your agent to profile the data: what each column holds, how complete it is, and what looks odd.
+Write down three candidate questions, then pick the one the data answers most clearly.
+Sketch your page on paper before you prompt the agent.
+Publish a placeholder page on your first day.
+Build in small steps, and check each headline number with a separate calculation.
+Ask someone who has not seen your site to use it for two minutes, then fix whatever confused them.
 Build and publish requirements
@@ -111,2 +122,2 @@
 Funded by the University of Illinois-Deloitte Foundation Center for Business Emerging Technologies.	Page 
-Campus Comps case: Variation 1: Open Brief
+Campus Comps case: Variation 3: General Instructions
```

**Reference sites (output of `check_sites.js` and `check_numbers.py`):**

```
pass  v1-old-homes-close-in  375px  light  (16 control checks)
pass  v1-old-homes-close-in  375px  dark  (16 control checks)
pass  v1-old-homes-close-in  1280px  light  (16 control checks)
pass  v1-old-homes-close-in  1280px  dark  (16 control checks)
pass  v2-six-questions  375px  light  (8 control checks)
pass  v2-six-questions  375px  dark  (8 control checks)
pass  v2-six-questions  1280px  light  (8 control checks)
pass  v2-six-questions  1280px  dark  (8 control checks)
pass  v3-close-to-campus  375px  light  (9 control checks)
pass  v3-close-to-campus  375px  dark  (9 control checks)
pass  v3-close-to-campus  1280px  light  (9 control checks)
pass  v3-close-to-campus  1280px  dark  (9 control checks)
pass  v1-old-homes-close-in table and figures against the reference summary: 83 values checked, 0 differ
pass  v2-six-questions tables and text against the answer key: 384 values checked, 0 differ
pass  v3-close-to-campus headline numbers at five settings, recomputed from the dataset: 25 values checked, 0 differ
```

The V3 test saves the three headline numbers at five settings of campus, budget and distance. `check_numbers.py` recomputes them from the full dataset without the site's data file.

**Where each number in the instructor documents comes from:**

- **Variation 2 answer key (Word and Excel):** every figure is written by `answer_key.py`, from the functions in `variation2.py` and `wrong_answers.py`. That includes the figures in the model answers and the chart descriptions. The only numbers not from the data are the four web facts in Question 5 (section 7 below) and the tolerances, which are marking rules.
- **Instructor orientation:** the text is a template, and `orientation.py` fills in each data figure. All 43 figures, as filled in (`results/orientation_figures.json`):

  - `rows`: 35,529
  - `campuses`: 11
  - `cities`: 18
  - `states`: 11
  - `dom_rows`: 28,043
  - `dom_share`: 78.9%
  - `dom_missing_share`: 21%
  - `dom`: 11
  - `dom_mean`: 33.9
  - `dom_blank_zero`: 6
  - `dom_to_close`: 50
  - `dom_area_min`: 7
  - `dom_area_max`: 27
  - `mich_dom`: 7
  - `mich_dom_to_close`: 39
  - `shared_rows`: 240
  - `shared_addresses`: 103
  - `dedup_loss`: 137
  - `after_dedup`: 35,392
  - `street_rows`: 312
  - `double_addresses`: 87
  - `double_rows`: 174
  - `double_va`: 79
  - `real_addresses`: 16
  - `real_rows`: 66
  - `psu_addresses`: 13
  - `va_price`: $625,000
  - `va_price_one_copy`: $615,000
  - `price_under_1000`: 4
  - `price_zero`: 1
  - `price_under_10000`: 40
  - `price_over_5m`: 31
  - `max_price`: $81,510,000
  - `median_price`: $410,000
  - `mean_price`: $510,289
  - `single_family`: 35,350
  - `zero_sqft`: 127
  - `ga_pps`: $196.82
  - `ga_pps_blank_zero`: $209.30
  - `ga_area_missing`: 337
  - `dec_all_years`: 25
  - `dec_window`: 21
  - `built_1900`: 192

  The orientation's other numbers are not data figures: class time (20 minutes), team size (2 to 3), the schedule days, the rubric points, and a suggested Accuracy scale.
- **Post-assignment survey:** no data figures.
- **Reference code README:** 35,529 rows, 34 columns and 82 figures, as `run_all.py` prints them.
- **Reference site READMEs:** each number is the site's own figure, confirmed by the DuckDB query beside it. All ten queries were re-run against the CSV and returned the values shown.
- **Notebook:** its outputs are computed when it runs. The three worked examples reproduce the pilots' numbers: $248.42 against $207.88 (19.5%), 11 days from 28,029 sales, and 39 against 7 days.

## 4. Changes to the student documents

All changes are in `source/case-documents/content.js`, rebuilt with `build.js`. The original is in `inputs/case-documents/source/`. I added no answers, hints or example questions, did not narrow Variation 1, and added nothing to Variation 3.

**Shared sections (all three case documents):**

| # | Where | Change | Reason |
|---|---|---|---|
| 1 | The data | "the CSV file (8.6 MB)" became "(about 9 MB)" | The file is 9,056,275 bytes: 8.6 MiB but 9.1 MB. All three pilots flagged the mixed units, since the setup guide puts the figure beside a limit given in MiB. |
| 2 | The data | Names the sheet's section: five problems "under \"Five things that will bite you\"" | V3 pilot. The setup guide sends students to that heading, but the case document never used it. |
| 3 | The data, problem 2 | "Street addresses repeat because condo and apartment units share an address. Never remove duplicates by address." became "Street addresses repeat. Condo and apartment units can share an address, so never remove a sale just because its address repeats." | The old sentence is wrong for most repeated addresses (finding 1). The instruction itself is unchanged. |
| 4 | Build and publish requirements | The summary-file rule now says to commit "the data file it reads" too, and that "A script that prepares data files is fine; the site itself must run without a build step." | V1 and V3 asked whether the full CSV must stay once the site reads a summary file. V2 asked how "no build step" fits with a summary script. |
| 5 | What to submit, README | Each checked number needs "a calculation that confirms it and is separate from the site's own code" | V1 was unsure whether "separate" meant a different tool. |
| 6 | What to submit, reflection | Adds "Submit it to your instructor; it does not go in your repository." | All three pilots were unsure, and the repository is public. |

**Setup guide:**

| # | Where | Change | Reason |
|---|---|---|---|
| 7 | Step 7 and the "Speed" tip | "8.6 MB" became "about 9 MB" | As change 1 |
| 8 | Step 5, the project instructions box | One rule per line | V2 pilot: the box broke sentences mid-line, so pasting it gave broken sentences |

**Variation 2, "Your task":**

| # | Where | Change | Reason |
|---|---|---|---|
| 9 | Question 4 | Adds "Use only homes listed from April 1, 2023 through March 31, 2025, so that each calendar month covers exactly two years. Group them by the month of `list_date`." | Section 7 check (finding 2). December's median is 25 days with all years and 21 in the window. The fastest months become a clean tie (April and May, 6 days) instead of a three-way tie at 7. |
| 10 | Introduction | Adds "Write the answers for a general reader, such as someone thinking about moving to one of these towns." | V2 pilot: the rubric scores fit to an audience, but Variation 2 named none |
| 11 | Definitions | Adds "They take the place of the rules that \"The data\" section asks you to choose." | V2 pilot saw a conflict with "choose a rule for which sales to include" |
| 12 | Valid sale | Adds "Use only valid sales for figures that involve `sale_price` (Questions 1, 3 and 5). The other questions use every sale." | V2 pilot applied the rule to every question, which changed its Question 2 denominators |
| 13 | Small groups | Now "if a median or a share is based on fewer than 20 sales, show \"fewer than 20 sales\" in place of it. Always show counts of sales and addresses." | V2 pilot was unsure whether the rule applied to counts in Question 6 |
| 14 | Question 3 | Adds "Say what you count as falling," | Undefined: common rules give 5, 8 or 10 of 11 areas. The key now gives all three and marks against the student's stated rule. |
| 15 | Question 4 | "Across all areas, pooled together," | V2 pilot was unsure whether to pool areas or take a median of area medians |
| 16 | Question 5 | Adds "(say what you count as far)" and "Cite a source for any explanation." | The threshold was undefined. The pilot explained the gap from general knowledge, without sources. |
| 17 | Question 6 | Adds "across all areas and within each area" | V2 pilot was unsure. The overall figure hides opposite patterns in the two areas with enough such sales. |

Student documents cite only figures already in the data description sheet. The added items are definitions (the Question 4 window dates) or a file size ("about 9 MB", which replaced the old "8.6 MB").

## 5. Pilot findings

Each pilot was a fresh agent session given only that variation's student files (the case document, the setup guide, the students' copy of the description sheet and the data) and the instruction "You are a student. Complete this assignment." Each worked in a local git repository, previewed its site with a local web server, and kept notes on every guess and misreading. None had access to the handoff, the reference code or the other pilots.

| | Variation 1 | Variation 2 | Variation 3 |
|---|---|---|---|
| Major steps | 8 | 14 | 12 |
| Tool actions, elapsed time | 80, about 21 minutes | 92, about 28 minutes | 88, about 22 minutes |
| What it built | A site for people moving to a college town for a university job: where a budget goes furthest, the cost of living near campus, how fast homes sell. Four tiles and four charts. | All six answers, each with figures, a chart and a table, plus answer cards | For new faculty who want to walk or bike to work: the extra cost per square foot under 2 miles from campus, with campus and bedroom pickers |
| Data problems fallen into | None | None | None |
| Numbers | Correct under its stated rules (median $410,000; 11 days) | Every answer within the key's tolerances | Correct under its stated rules, confirmed by its own SQL check |

**What the pilots had to guess** (fixed in section 4 unless noted):

- **All three:** where the reflection goes; MB against MiB.
- **Variations 1 and 3:** whether the full CSV must stay in the repository.
- **Variation 1:** what counts as a separate check.
- **Variation 3:** that the case document never names "Five things that will bite you."
- **Variation 2:** which questions use valid sales; whether the small-group rule covers counts; what "falls" and "far from 1" mean; pooling in Question 4; across or within areas in Question 6; the missing audience; the box's line breaks.
- **Left open on purpose:** which prices to keep (both open-ended pilots chose $10,000 to $5,000,000), the smallest believable living area (300 and 200 sq ft), what "near campus" means, the time window, and whether headline numbers should change with the controls. The orientation tells instructors to expect these questions.

**What they misread:** The Variation 2 pilot applied the valid-sale rule to every question, so its Question 2 counts used 35,525 sales instead of 35,529. Its figures still fell within the key's tolerance, and change 12 removes the ambiguity. No other misreading of the case documents was found.

**What they found wrong in the description sheet** (left unchanged, as instructed; see section 6):

- Its SQL examples compute means (`AVG(julianday(contract_date) - julianday(list_date))`, `AVG(sale_price)`), while its warnings, and Variation 2, call for medians.
- It says "Full details are in the build notes", but students do not get the build notes.
- The Variation 2 pilot independently found the repeated-address double records.

**What could not be tested in the pilots:** none of the pilot sessions had a browser, so they checked their pages with scripted tests and chart images. That is a limit of the pilot environment, not of the case: students will have browsers. The reference sites were tested in a headless browser.

**Agent logs:** every pilot logged real mistakes its agent made and caught, as the case asks. The Variation 2 pilot noted that the requirement could tempt a student to invent one. The orientation suggests checking logs against the commit history.

## 6. Open decisions

| Decision | Default used | Notes |
|---|---|---|
| Case title | "Campus Comps: Building a Data Website with an AI Coding Agent" | Set in `content.js` and `source/word-documents/build.js` |
| Author name | The placeholder "[Author name]" | In every Word document |
| License | CC BY-NC-SA 4.0, stated in each case document | Unchanged |
| "Suggested starting questions" | Removed from the students' copy only | The dataset's own copy keeps it |
| Variation label visible to students | Shown in each case document's subtitle and header | Replace with a neutral code if students should not know the other variations exist |
| **Repeated addresses that are one sale recorded twice** (new) | Dataset 1.0 unchanged. The case document's sentence now says units *can* share an address. The orientation and answer key explain the double records, and the key says not to mark down a student who keeps every row. | Options: (a) keep as is; (b) issue dataset 1.1, removing one row of each pair and correcting the description sheet; (c) keep the rows but add the finding to the description sheet as a sixth problem. Option (b) or (c) would change Appendix A figures, so I stopped short of either. |
| **Description sheet SQL examples compute means** (new) | Unchanged, as section 5 instructs | Fix in a 1.1 description sheet if you issue one |
| **Question 4 listing window** (new) | Applied in `content.js`, the key and the V2 site | Confirm the wording |
| **Public repository** (new) | Kept public, as you accepted | Students can find the answer key and the reference sites. The orientation tells instructors so. |
| **Fonts in two reference sites** (new) | Copied into each site's `fonts/` folder with their licenses, so no font service is needed | All four fonts are under the SIL Open Font License |

## 7. Web facts

Each fact below was checked on the web on October 11, 2026.

| Fact | Used in | Source |
|---|---|---|
| Pennsylvania counties assess against irregularly updated "base year" values | Answer key, V2 site (Question 5) | [Babst Calland, "Pennsylvania tax assessment appeals and common level ratios: four observations"](https://www.babstcalland.com/news-article/pennsylvania-tax-assessment-appeals-and-common-level-ratios-four-observations/) (October 6, 2023) |
| Centre County's common level ratio factor is 6.10 (July 2026 list), and the factors are "the mathematical reciprocals of the actual common level ratio", so assessments run at about one sixth of market value | Answer key, V2 site | [Pennsylvania Department of Revenue, "2025 Common Level Ratio Real Estate Valuation Factors"](https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/taxtypes/rtt/documents/clr_factor_current.pdf) |
| Michigan assesses at no more than 50% of true cash value; taxable value rises by at most inflation or 5% a year and is uncapped after a sale | Answer key, V2 site | [Michigan State Tax Commission, Guide to Basic Assessing](https://www.michigan.gov/-/media/Project/Websites/treasury/Assessors/Guide_to_Basic_Assessing_116.pdf) (May 2018) |
| California reassesses at purchase on a change of ownership; the assessed value then rises by at most 2% a year | Answer key, V2 site | [California State Board of Equalization, Assessors' Handbook Section 401](https://www.boe.ca.gov/proptaxes/pdf/ah401.pdf) (reprinted January 2015) |
| Illinois assesses property outside Cook County at 33 1/3 percent of fair market value | V2 site (Question 5) | [Illinois Department of Revenue, PIO-16](https://tax.illinois.gov/content/dam/soi/en/web/tax/research/publications/documents/pios/pio-16.pdf) (revised October 2023) |
| Archivo Narrow, Public Sans, Bricolage Grotesque and Instrument Sans are under the SIL Open Font License 1.1 | Reference sites' `fonts/` folders | The OFL file in each font's folder of [github.com/google/fonts](https://github.com/google/fonts/tree/main/ofl) |

The sample V2 site's earlier sources for Michigan (a Lake County brochure) and California (a question-and-answer sheet) were replaced with the state agencies' own documents above.
