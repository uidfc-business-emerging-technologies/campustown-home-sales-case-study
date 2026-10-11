# Report to Park: Campus Comps case package

Date: October 11, 2026. This report covers the work in `HANDOFF.md`, sections 1 to 14. Everything is in `output/`, and the pull request on the branch `claude/new-session-re1c94` shows the history one step at a time.

## 1. Summary

**What was built:**

- **A corrected dataset, still version 1.0.** At your request, the 87 sales the source recorded twice under two parcel numbers are now one row each, in all five formats, with the description sheet, build notes, README and reference figures corrected to match (section 6). The package is in `output/dataset/college-town-dataset/` and replaces the one in `inputs/`.
- **Student materials, revised after a pilot of each variation.** The three case documents and the setup guide are rebuilt from an updated `content.js`. Section 4 lists every change and its reason. The students' copy of the data description sheet drops only "Suggested starting questions", in markdown and Word. The students' data is the corrected dataset.
- **Reference code.** One command (`python run_all.py`) checks the inputs, reproduces all 82 Appendix A figures as the corrected documents give them, and computes every Variation 2 figure and the common wrong answers. It also writes the answer key workbook and charts, fills in the orientation's figures, and writes each reference site's data file. It runs offline, and a clean environment produces byte-identical output. A notebook recomputes a student's number under the student's own definitions, with three worked examples.
- **Variation 2 answer key,** in Word and a matching Excel workbook. It covers the figures, a chart, a model answer, the common wrong answers with the figures they produce, and a tolerance for each question.
- **Instructor orientation** (section 9.1) and the **post-assignment survey** (Appendix B).
- **Three reference sites,** one per variation, each with a model README and agent log. Each was tested at 375 and 1280 pixels, in light and dark, served from a subfolder. Every number they show was checked against the reference code.

**Two findings you should know about first:**

1. **Most repeated addresses were one sale recorded twice, not separate condo units. The data is now fixed.** The description sheet said the 240 sales at 103 repeated addresses were condo or apartment units. That held in State College. But 87 of the 103 addresses (174 rows) met the build notes' own test for a duplicate: two rows, prices within 1% and sale dates within 90 days. 79 of them were in Charlottesville. In most pairs, one row came from the listing and the other from the county record, with a different parcel number, so the build's parcel check missed them. The Variation 2 pilot found this on its own. As you asked, I removed one row of each pair and kept version 1.0: the dataset now has 35,442 rows, and 66 rows at 16 addresses share an address. 20 of the 82 Appendix A figures change (section 6). The pilots ran on the original 35,529-row file.
2. **Question 4 needed a listing window.** Listings from 2021 and 2022 appear only if they sold after March 2023, so their median days on market runs from about 90 to 473 days. Listings from late 2025 are cut off before slow sales close. Question 4 now covers homes listed from April 1, 2023 through March 31, 2025. That window covers each calendar month exactly twice.

**What you need to do next:**

1. In `output/dataset/college-town-dataset/`, run `python build/export_raw.py --verify` with your database login. It should report PASS: the build, with the new step, rebuilds the corrected CSV byte for byte. I checked everything the correction depends on against the source database (section 6), but not a full rebuild, because the connector returns query results to me, not files.
2. Publish `output/dataset/college-town-dataset/` in place of the original package, and decide the open decisions in section 7.
3. Replace "[Author name]" in `source/case-documents/content.js` and `source/word-documents/build.js`, then rebuild (`output/README.md` gives the commands).
4. Confirm the license (CC BY-NC-SA 4.0).
5. Review the student document changes in section 4.
6. Merge the pull request, then publish with GitHub Pages ("Deploy from a branch", main, root). Each site will be at `https://OWNER.github.io/REPOSITORY/output/instructor/reference-sites/FOLDER/`. No file in the repository uses Liquid template syntax, so the default GitHub Pages build will not fail on it.
7. Open one reference site in a real browser on a phone. The tests used a headless browser at phone width, not a phone.

## 2. Contents

`output/`, one line per file:

- `README.md`: What is in the package, and how to rebuild every generated file
- `REPORT.md`: This report
- `dataset/college-town-dataset/README.md`: The dataset package's README, with the corrected figures
- `dataset/college-town-dataset/build/build_dataset.py`: The dataset build, with the new two-parcel step (section 6)
- `dataset/college-town-dataset/build/drop_double_records.py`: Applies the two-parcel step to the published CSV and rewrites the five files (section 6)
- `dataset/college-town-dataset/build/export_raw.py`: Exports the raw build inputs from the source database and checks they rebuild `data/`, as on main
- `dataset/college-town-dataset/build/extract_query.sql`: The two source queries, unchanged
- `dataset/college-town-dataset/build/make_parquet.py`: CSV to Parquet and DuckDB, checked value by value, unchanged
- `dataset/college-town-dataset/build/reference_figures.py`: Writes the reference figures and the campus map, unchanged
- `dataset/college-town-dataset/build/removed_double_records.csv`: The 87 removed rows, each beside the row kept for the same sale
- `dataset/college-town-dataset/data/college_town_home_sales.csv`: The corrected dataset, version 1.0
- `dataset/college-town-dataset/data/college_town_home_sales.duckdb`: The corrected dataset, version 1.0
- `dataset/college-town-dataset/data/college_town_home_sales.parquet`: The corrected dataset, version 1.0
- `dataset/college-town-dataset/data/college_town_home_sales.sqlite`: The corrected dataset, version 1.0
- `dataset/college-town-dataset/data/college_town_home_sales.xlsx`: The corrected dataset, version 1.0
- `dataset/college-town-dataset/docs/city_campus_map.csv`: Which cities fall under which campus, regenerated from the corrected data
- `dataset/college-town-dataset/docs/city_campus_map.md`: Which cities fall under which campus, regenerated from the corrected data
- `dataset/college-town-dataset/docs/data_description_sheet.md`: The description sheet, corrected
- `dataset/college-town-dataset/docs/dataset_build_notes.md`: The build notes, with the new step and the corrected counts
- `dataset/college-town-dataset/docs/reference_figures.md`: Instructor reference figures, regenerated from the corrected data
- `dataset/college-town-dataset/docs/reference_figures_by_city.csv`: Instructor reference figures, regenerated from the corrected data
- `instructor/Instructor Orientation.docx`: Instructor orientation (section 9.1)
- `instructor/Post-Assignment Survey.docx`: Post-assignment survey (Appendix B), the same for every variation
- `instructor/Variation 2 Answer Key.docx`: Variation 2 answer key: figures, charts, model answers, common wrong answers, tolerances
- `instructor/Variation 2 Answer Key.xlsx`: The same answer key as a workbook, one sheet per question
- `instructor/reference-code/README.md`: How to run the reference code and the site tests
- `instructor/reference-code/acceptance_checks.py`: Section 13 document checks: case document diff, answers in student files, words, dashes, Word file hygiene
- `instructor/reference-code/answer_key.py`: Writes the answer key workbook, charts, key markdown and the V2 site's answers.json
- `instructor/reference-code/appendix_a.py`: The Appendix A figures and the check
- `instructor/reference-code/definitions.py`: Loads the data with consistent types; shared rules and rounding
- `instructor/reference-code/orientation.py`: Computes the data figures in the orientation and fills them in
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
- `students/data/college_town_home_sales.csv`: The corrected dataset, version 1.0, the same files as in `dataset/`
- `students/data/college_town_home_sales.duckdb`: The corrected dataset, version 1.0, the same files as in `dataset/`
- `students/data/college_town_home_sales.parquet`: The corrected dataset, version 1.0, the same files as in `dataset/`
- `students/data/college_town_home_sales.sqlite`: The corrected dataset, version 1.0, the same files as in `dataset/`
- `students/data/college_town_home_sales.xlsx`: The corrected dataset, version 1.0, the same files as in `dataset/`
- `students/data_description_sheet.md`: Students' copy of the description sheet, markdown ("Suggested starting questions" removed)

## 3. Verification

| # | Acceptance check (section 13) | Result | Evidence |
|---|---|---|---|
| 1 | The code reproduces every figure in Appendix A exactly | Pass | 82 of 82 figures match (`instructor/reference-code/results/appendix_a_check.csv`), taken from the corrected description sheet and `reference_figures.md`. 20 of them differ from the handoff's Appendix A, which predates the correction (section 6). One median falls on a half (Iowa days on market, 23.5), and the code rounds half up, as the published tables do. |
| 2 | The three case documents differ only in the variation label and "Your task" | Pass | Outside "Your task" and the label, the three documents' 108 paragraphs are identical. The diff is below. |
| 3 | No student file contains answers | Pass | All 203 distinctive answer-key values were searched for in the 6 student text files. There are no matches in the case documents or the setup guide. The description sheet, which matches the dataset package's apart from the removed section, already prints 19 of them (details below). |
| 4 | No document mentions peer review or auditing other students' work | Pass | A search of every document and text file in `output/` for "peer", "audit" and "review each other" found nothing (file counts in the evidence below). |
| 5 | No document names a specific AI coding agent product or an agent-specific file name | Pass | The same files were searched for 21 product and file names. |
| 6 | Every .docx opens, is editable, has the funding line, and has no comments, tracked changes or hidden text | Pass | All 8 Word files: funding line in the footer; no comments, tracked changes, hidden text or editing protection; blank author. All 8 open in LibreOffice (page counts below). |
| 7 | No document contains an em dash or an en dash | Pass | None in any Word file or text file in `output/`. |
| 8 | Every number in an instructor document traces to the code's output | Pass | Listed below. |
| 9 | The reference code runs from a clean environment with one command | Pass | In a new virtual environment, `pip install -r requirements.txt` then `python run_all.py` ran in under 30 seconds. Its output was byte-identical to the working copy: the workbook, the charts, the key, the orientation figures and all three site data files. |
| 10 | Each reference site works from a subfolder, with no console errors at 375 and 1280 px, working controls, and numbers that match | Pass | 12 of 12 browser runs pass (3 sites, 2 widths, light and dark). 483 displayed values match the reference code, with none differing. Screenshots: `output/report-screenshots/`. |

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
  pass  searched 6 student files for 203 answer-key values
        Case documents and setup guide: 0 matches.
        Description sheet (both copies, as in the dataset package): 19 matches: $342,000, $370,000, $430,000, $571,000, $615,000, $889,000, 1,351, 1,909, 127, 2,775, 2,814, 3,016, 3,021, 3,664, 3.4, 4,616, 5,629, 5,706, 941
        Each of these is a figure the dataset's own description sheet already prints (rows per campus area, city medians that equal single-city campus areas, the median distance and the zero-area count).
Words and characters that must not appear
  pass  no peer review or auditing in 79 documents and text files
  pass  no agent product or agent-specific file name in 79 documents and text files
  pass  no em or en dash in 79 documents and text files
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
pass  v1-old-homes-close-in table and figures against the reference summary: 81 values checked, 0 differ
pass  v2-six-questions tables and text against the answer key: 377 values checked, 0 differ
pass  v3-close-to-campus headline numbers at five settings, recomputed from the dataset: 25 values checked, 0 differ
```

The V3 test saves the three headline numbers at five settings of campus, budget and distance. `check_numbers.py` recomputes them from the full dataset without the site's data file.

**Where each number in the instructor documents comes from:**

- **Variation 2 answer key (Word and Excel):** every figure is written by `answer_key.py`, from the functions in `variation2.py` and `wrong_answers.py`. That includes the figures in the model answers and the chart descriptions. The only numbers not from the data are the four web facts in Question 5 (section 7 below) and the tolerances, which are marking rules.
- **Instructor orientation:** the text is a template, and `orientation.py` fills in each data figure. All 39 figures, as filled in (`results/orientation_figures.json`):

  - `rows`: 35,442
  - `campuses`: 11
  - `cities`: 18
  - `states`: 11
  - `dom_rows`: 28,042
  - `dom_share`: 79.1%
  - `dom_missing_share`: 21%
  - `dom`: 11
  - `dom_mean`: 33.9
  - `dom_blank_zero`: 6
  - `dom_to_close`: 50
  - `dom_area_min`: 7
  - `dom_area_max`: 27
  - `mich_dom`: 7
  - `mich_dom_to_close`: 39
  - `shared_rows`: 66
  - `shared_addresses`: 16
  - `dedup_loss`: 50
  - `after_dedup`: 35,392
  - `street_rows`: 138
  - `psu_rows`: 60
  - `psu_addresses`: 13
  - `other_shared_rows`: 6
  - `other_shared_addresses`: 3
  - `price_under_1000`: 4
  - `price_zero`: 1
  - `price_under_10000`: 40
  - `price_over_5m`: 31
  - `max_price`: $81,510,000
  - `median_price`: $410,000
  - `mean_price`: $509,438
  - `single_family`: 35,263
  - `zero_sqft`: 127
  - `ga_pps`: $196.82
  - `ga_pps_blank_zero`: $209.30
  - `ga_area_missing`: 337
  - `dec_all_years`: 25
  - `dec_window`: 21
  - `built_1900`: 192

  The orientation's other numbers are not data figures: class time (20 minutes), team size (2 to 3), the schedule days, the rubric points, and a suggested Accuracy scale.
- **Post-assignment survey:** no data figures.
- **Reference code README:** 35,442 rows, 34 columns and 82 figures, as `run_all.py` prints them.
- **Reference site READMEs:** each number is the site's own figure, confirmed by the DuckDB query beside it. All ten queries were re-run against the CSV and returned the values shown.
- **Notebook:** its outputs are computed when it runs. The three worked examples are the pilots' numbers recomputed on the corrected data: $248.39 against $207.64 (19.6%; the pilot had 19.5%), 11 days from 28,028 sales (28,029), and 39 against 7 days (unchanged).

## 4. Changes to the student documents

All changes are in `source/case-documents/content.js`, rebuilt with `build.js`. The original is in `inputs/case-documents/source/`. I added no answers, hints or example questions, did not narrow Variation 1, and added nothing to Variation 3.

**Shared sections (all three case documents):**

| # | Where | Change | Reason |
|---|---|---|---|
| 1 | The data | "the CSV file (8.6 MB)" became "(about 9 MB)" | The corrected file is 9,036,239 bytes: 8.6 MiB but 9.0 MB. All three pilots flagged the mixed units, since the setup guide puts the figure beside a limit given in MiB. |
| 2 | The data | Names the sheet's section: five problems "under \"Five things that will bite you\"" | V3 pilot. The setup guide sends students to that heading, but the case document never used it. |
| 3 | The data; Getting started | "35,529 completed home sales" and "the number of rows (35,529)" became 35,442 | The corrected dataset (section 6) |
| 4 | Build and publish requirements | The summary-file rule now says to commit "the data file it reads" too, and that "A script that prepares data files is fine; the site itself must run without a build step." | V1 and V3 asked whether the full CSV must stay once the site reads a summary file. V2 asked how "no build step" fits with a summary script. |
| 5 | What to submit, README | Each checked number needs "a calculation that confirms it and is separate from the site's own code" | V1 was unsure whether "separate" meant a different tool. |
| 6 | What to submit, reflection | Adds "Submit it to your instructor; it does not go in your repository." | All three pilots were unsure, and the repository is public. |

**Setup guide:**

| # | Where | Change | Reason |
|---|---|---|---|
| 7 | Step 7 and the "Speed" tip | "8.6 MB" became "about 9 MB" | As change 1 |
| 8 | Step 5, the project instructions box | One rule per line | V2 pilot: the box broke sentences mid-line, so pasting it gave broken sentences |
| 9 | Step 6 and the "Maps" tip | "35,529 rows" and "all 35,529 points" became 35,442 | As change 3 |

**Variation 2, "Your task":**

| # | Where | Change | Reason |
|---|---|---|---|
| 10 | Question 4 | Adds "Use only homes listed from April 1, 2023 through March 31, 2025, so that each calendar month covers exactly two years. Group them by the month of `list_date`." | Section 7 check (finding 2). December's median is 25 days with all years and 21 in the window. The fastest months become a clean tie (April and May, 6 days) instead of a three-way tie at 7. |
| 11 | Introduction | Adds "Write the answers for a general reader, such as someone thinking about moving to one of these towns." | V2 pilot: the rubric scores fit to an audience, but Variation 2 named none |
| 12 | Definitions | Adds "They take the place of the rules that \"The data\" section asks you to choose." | V2 pilot saw a conflict with "choose a rule for which sales to include" |
| 13 | Valid sale | Adds "Use only valid sales for figures that involve `sale_price` (Questions 1, 3 and 5). The other questions use every sale." | V2 pilot applied the rule to every question, which changed its Question 2 denominators |
| 14 | Small groups | Now "if a median or a share is based on fewer than 20 sales, show \"fewer than 20 sales\" in place of it. Always show counts of sales and addresses." | V2 pilot was unsure whether the rule applied to counts in Question 6 |
| 15 | Question 3 | Adds "Say what you count as falling," | Undefined: common rules give 5, 8 or 10 of 11 areas. The key now gives all three and marks against the student's stated rule. |
| 16 | Question 4 | "Across all areas, pooled together," | V2 pilot was unsure whether to pool areas or take a median of area medians |
| 17 | Question 5 | Adds "(say what you count as far)" and "Cite a source for any explanation." | The threshold was undefined. The pilot explained the gap from general knowledge, without sources. |
| 18 | Question 6 | Adds "across all areas and within each area" | V2 pilot was unsure which comparison was wanted. On the original file, the overall figure hid opposite patterns in Penn State and Virginia. On the corrected file, only Penn State has 20 or more such sales, so most areas must show "fewer than 20 sales". |

The first version of this package also changed problem 2 under "The data" ("Street addresses repeat. Condo and apartment units can share an address..."), because the original sentence was wrong for most repeated addresses. With the data corrected, the original sentence is right again, so it is restored: "Street addresses repeat because condo and apartment units share an address. Never remove duplicates by address."

Student documents cite only figures already in the data description sheet. The added items are definitions (the Question 4 window dates) or a file size ("about 9 MB", which replaced the old "8.6 MB").

## 5. Pilot findings

The pilots ran before the dataset correction, on the original 35,529-row file. Their numbers below are as they computed them.

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

**What they misread:** The Variation 2 pilot applied the valid-sale rule to every question, so its Question 2 counts used 35,525 sales instead of 35,529 (on the original file). Its figures still fell within the key's tolerance, and change 13 removes the ambiguity. No other misreading of the case documents was found.

**What they found wrong in the description sheet:**

- Its SQL examples compute means (`AVG(julianday(contract_date) - julianday(list_date))`, `AVG(sale_price)`), while its warnings, and Variation 2, call for medians. Left unchanged, as the handoff instructs (section 7).
- It says "Full details are in the build notes", but students do not get the build notes. Left unchanged (section 7).
- The Variation 2 pilot independently found the repeated-address double records. Corrected at your request (section 6).

**What could not be tested in the pilots:** none of the pilot sessions had a browser, so they checked their pages with scripted tests and chart images. That is a limit of the pilot environment, not of the case: students will have browsers. The reference sites were tested in a headless browser.

**Agent logs:** every pilot logged real mistakes its agent made and caught, as the case asks. The Variation 2 pilot noted that the requirement could tempt a student to invent one. The orientation suggests checking logs against the commit history.

## 6. The dataset correction

**What was wrong.** The build removes a second record of the same sale only when the two rows share a parcel number. At 87 addresses, the source held one sale under two parcel numbers: two rows with prices within 1% (identical in 85) and sale dates within 5 days. Typically one row came from the listing, with the list and contract dates, and the other from the county, with the full parcel number and the assessed value. In 66 pairs the listing's row had a placeholder for the parcel number: `0` (17), a lot or homesite number such as `109` (37), or `062000000016D1`, a parcel number that 14 new homes share (12). 79 of the 87 were in Charlottesville. The description sheet called all of them condo units.

**What I changed, keeping version 1.0** (in `output/dataset/college-town-dataset/`):

- **The build** (`build/build_dataset.py`). A new step, `drop_double_records()`, runs right after the same-parcel step. An address with exactly two rows that pass the build's own same-sale test (prices within 1%, sale dates within 90 days) keeps one row, chosen by the existing rule: the most complete record, then the later date, then the lower source id. Only two-row addresses qualify, because three pairs of units in larger State College buildings pass the price and date test but are separate units with their own parcel numbers and living areas.
- **The data.** The raw files are not in the package, so `build/drop_double_records.py` applies the same function to the published CSV, rewrites all five formats with the build's own writers, and checks the Parquet and DuckDB files against the new CSV value by value. It removed 87 rows. Run again, it removes nothing. `build/removed_double_records.csv` lists each removed row beside the row kept for the same sale. Writing the corrected CSV again with the build's writers reproduces the CSV, SQLite and Excel files byte for byte.
- **The documents.** The description sheet, the build notes and the README now give the corrected figures; the build notes add the step to section 6, the count chain (35,822 - 38 - 87 - 255 = 35,442) and the known issues. `reference_figures.md`, `reference_figures_by_city.csv` and the city to campus map were regenerated with `build/reference_figures.py`, after checking that the script reproduces the original documents exactly from the original CSV.

**The result.** 35,442 rows. 66 rows at 16 addresses share an address: 60 are condo and apartment units in 13 State College buildings, and the other 6 are pairs of two different sales, about a year or more apart, at three homes built in 2023 or 2024. The description sheet explains both.

**Checked against the source database.** These read-only queries ran through the PlanetScale connector on October 11, 2026:

- **The source has not changed in size.** The extract filter still gives 35,822 rows. The event history still holds 284,955 events across 35,816 properties, as the build notes say.
- **The 87 removed rows are the right records.** Each matches exactly one source record by address, parcel number and price, and that record's latest sale date equals the row's `sale_date`.
- **Why their dates are blank.** For 86 of the 87, the history has no listing, pending or contingent event between the previous sale and this one. In the build's rule, that means "no listing on record" and "no contract status recorded". The 87th (130 Brickleberry Rdg, Athens) has one listing and one contract, with the same dates as the row kept for its sale, and no failed contract. So the exact counts on the corrected file are:

  | Blank | Reason | Before | After |
  |---|---|---:|---:|
  | `list_date` | No listing on record | 5,281 | 5,195 |
  | | Withdrawn before a contract | 857 | 857 |
  | | Lapsed (silent more than a year) | 122 | 122 |
  | `contract_date` | No contract status recorded | 6,411 | 6,325 |
  | | Contract more than a year before closing | 147 | 147 |
  | | Fell through | 50 | 50 |
  | All three | No history at all | 6 | 6 |

  The count of homes whose clock kept running after a failed contract stays at 2,021. The description sheet and the build notes now give these exact figures, in the same table layout as the original sheet. The "Before" column is the first build's own count, from its build notes.
- **The city floor is unaffected.** The extract's 141 repeated addresses cover 316 rows, and none is in one of the 57 places with fewer than 90 sales. So the new step removes nothing from those places, and the floor still removes the same 255 rows.
- **A full rebuild should keep the same row of each pair.** No pair ties on completeness and date, so the tiebreak never applies: the rebuild breaks ties by source id, the script by `listing_id`. Item 1 under "What you need to do next" confirms this end to end.

**Appendix A.** These 20 of the 82 figures changed; the other 62 are the same:

| Figure | Before | After |
|---|---:|---:|
| Rows | 35,529 | 35,442 |
| Rows with a list and a contract date | 28,043 (78.9%) | 28,042 (79.1%) |
| Rows sharing a street address | 240 | 66 |
| Addresses shared by more than one row (was "buildings") | 103 | 16 |
| `home_type` SINGLE_FAMILY | 35,350 | 35,263 |
| UW-Madison: rows; median price | 5,707; $434,020 | 5,706; $434,010 |
| Florida: rows | 5,630 | 5,629 |
| Michigan: rows; median $/sq ft | 3,022; $259.07 | 3,021; $259.11 |
| UNC: rows | 3,018 | 3,016 |
| Virginia: rows; median price; median $/sq ft; median miles | 2,854; $625,000; $272.35; 3.5 | 2,775; $615,000; $270.03; 3.4 |
| Georgia: rows | 2,816 | 2,814 |
| UC Davis: rows; median price; median $/sq ft | 942; $888,500; $492.58 | 941; $889,000; $492.71 |

**What changed in the case package as a result:**

- **Student documents:** the row count (changes 3 and 9), and the original problem 2 sentence restored (section 4).
- **Variation 2, Question 6:** 16 addresses and 66 sales, against 103 and 240. Penn State is now the only area with 20 or more such sales (0.5 miles from campus against 2.2 for other sales), so the answer no longer contrasts Penn State with Virginia. The key's model answer, note and tolerances are rewritten to match. The other five answers keep every ranking and named area; Virginia's figures move the most.
- **Orientation:** the "sixth problem" section on double records is gone, problem 2 now says what the 66 rows are, and one debrief question no longer assumes the sheet is wrong.
- **Reference sites:** the double-record notes are gone from all three, and the V2 site's Question 6 answer is rewritten. Each site's README numbers were rechecked with DuckDB, and each agent log has a new last entry recording the correction and what it changed. Earlier entries are left as they happened.
- **Reference code:** the double-record figures are gone from `orientation.py`, `answer_key.py` and `sites.py`. `v2_data_checks.py` still counts two-row addresses that look like one sale recorded twice, as a check on the data: it finds none.

## 7. Open decisions

| Decision | Default used | Notes |
|---|---|---|
| Case title | "Campus Comps: Building a Data Website with an AI Coding Agent" | Set in `content.js` and `source/word-documents/build.js` |
| Author name | The placeholder "[Author name]" | In every Word document |
| License | CC BY-NC-SA 4.0, stated in each case document | Unchanged |
| "Suggested starting questions" | Removed from the students' copy only | The dataset's own copy keeps it |
| Variation label visible to students | Shown in each case document's subtitle and header | Replace with a neutral code if students should not know the other variations exist |
| **Parcel number of the 87 kept rows** (decided) | Keep each kept row unchanged, the more complete record, as the build already does for same-parcel duplicates. In 66 of them the parcel number is the listing's placeholder (`0`, a lot or homesite number, or a parcel number several new homes share). | You chose this on October 11. The alternative was to take the parcel number and assessed value from the county's record, which would have made the dataset's first merged row. The county's values stay available in `build/removed_double_records.csv`. |
| **Description sheet SQL examples compute means** (new) | Unchanged, as section 5 of the handoff instructs | The sheet is open for the correction anyway, so this could be fixed in 1.0 too. I changed only the repeated-address material. |
| **Question 4 listing window** (new) | Applied in `content.js`, the key and the V2 site | Confirm the wording |
| **Public repository** (new) | Kept public, as you accepted | Students can find the answer key and the reference sites. The orientation tells instructors so. |
| **Fonts in two reference sites** (new) | Copied into each site's `fonts/` folder with their licenses, so no font service is needed | All four fonts are under the SIL Open Font License |

## 8. Web facts

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
