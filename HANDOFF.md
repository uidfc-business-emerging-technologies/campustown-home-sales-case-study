# Handoff: Campus Comps case package (three variations, GitHub Pages)

This handoff is for an AI coding agent working for Park, the case author. Date: 2026-10-10.

This file is `HANDOFF.md` at the root of the project folder. The folder will become a public GitHub repository.

Read the whole document before you change or create anything. It is self-contained, so you do not need any earlier conversation.

---

## 1. What you are building

You are completing a teaching case for the University of Illinois-Deloitte Foundation Center for Business Emerging Technologies (the Center), which posts free teaching materials for faculty.

In the case, students direct an AI coding agent to build a website with visualizations from the College-town home sales dataset. The site uses plain HTML, CSS and JavaScript. Students keep the code in a public GitHub repository and publish the site with GitHub Pages.

The case has three variations, which differ only in how much direction students get. Park wants to compare student outcomes across them.

| Variation | Name | What students get |
|---|---|---|
| 1 | Open Brief | Complete freedom in what they build |
| 2 | Specific Questions | Six questions their site must answer, with fixed definitions |
| 3 | General Instructions | A required site structure and a suggested process, but students choose their own question |

**What already exists:**

- The student-facing case documents for all three variations and a setup guide, written and reviewed (section 5).
- Sample reference sites for Variations 2 and 3, built and tested (section 10).

**What you will do:**

1. Check the Variation 2 questions against the data.
2. Pilot each variation.
3. Revise the student documents only where the checks or the pilot show a problem.
4. Build the reference code, the Variation 2 answer key, one reference website per variation, and the instructor materials.
5. Report back to Park.

## 2. Decisions already made

- **Tools:** students may use any AI coding agent or assistant, and may edit code by hand. The case gives no tool-specific instructions, because tools change quickly. Keep all materials tool-agnostic: no agent product names, and no agent-specific file names. Charting and mapping libraries may be named as examples.
- **Technology:** plain HTML, CSS and JavaScript only, with no frameworks, no build step and no server-side code. Libraries loaded with a script tag are allowed.
- **Hosting:** a public GitHub repository, published with GitHub Pages using "Deploy from a branch" (main branch, root folder).
- **Data:** the College-town home sales dataset, **version 1.0**, used as is, with every column. Do not make a reduced or anonymized edition.
- **Format:** the instructor's choice. Every document must work for individuals or for teams of 2 to 3, over 1 to 2 weeks.
- **No peer review:** students do not review or audit each other's work. Do not add it anywhere.
- **No file naming conventions:** ignore the Center's file naming conventions. Use clear, descriptive file names.
- **Document format:** text documents are editable Word files (.docx).
- **Public repository:** Park will push this whole folder to a public GitHub repository. Nothing in it needs to be hidden. The dataset, the instructor materials and the answer key will all be public. Commit your work as you go, with clear messages, so the history shows each step.

## 3. Open decisions

Use these defaults for now. List each one in your report so Park can confirm or change it.

| Decision | Default |
|---|---|
| Case title | "Campus Comps: Building a Data Website with an AI Coding Agent" (set in `content.js`) |
| Author name | The placeholder "[Author name]" |
| License for the case | CC BY-NC-SA 4.0, stated in each case document |
| "Suggested starting questions" in the data description sheet | Remove that section from the students' copy. If students see those questions, Variation 1 is no longer fully open. The dataset's own copy keeps the section. |
| Variation label visible to students | Each case document shows its variation name in the subtitle and the page header. If Park wants students not to know other variations exist, replace it with a neutral code. |

## 4. Inputs

The `inputs/` folder next to this handoff holds three folders:

- `inputs/college-town-dataset/`: the dataset package, copied from Box (Park/college-town-dataset). It holds `README.md`, `data/`, `docs/` and `build/`.
    - `data/` has the dataset as CSV, Excel, SQLite, DuckDB and Parquet.
    - `docs/` has `data_description_sheet.md`, `dataset_build_notes.md`, `reference_figures.md` (an instructor copy of the figures a correct site should show) and `reference_figures_by_city.csv`.
- `inputs/case-documents/`: the four Word files and `source/` (`content.js` and `build.js`), as described in section 5.
- `inputs/sample-sites/`: the two sample sites described in section 10.

When you load the inputs, run these checks. **If any check fails, stop and report. Do not edit the data.**

1. `data/college_town_home_sales.csv` has 35,529 rows and 34 columns, and `listing_id` is unique.
2. Your code reproduces every figure in Appendix A.
3. Never copy a raw build input (`raw_extract.csv` or `raw_events.csv`) into any output. They are not in the package, and must stay out.

## 5. The student documents (already written)

| File | Contents |
|---|---|
| Case Document - Variation 1 (Open Brief).docx | Shared sections + Variation 1 task |
| Case Document - Variation 2 (Specific Questions).docx | Shared sections + Variation 2 task: definitions and six questions |
| Case Document - Variation 3 (General Instructions).docx | Shared sections + Variation 3 task: required structure and suggested process |
| Setup Guide - GitHub Pages.docx | Shared by all variations: from an empty GitHub account to a live site, plus tips that work with any agent |

All four are generated from `source/content.js` by `source/build.js`. Run `node build.js <output-folder>`, with the `docx` npm package installed.

**Edit `content.js` and rebuild. Do not edit the Word files by hand.**

The three case documents share every section except "Your task" and the variation label. The shared sections are:

- Overview
- Learning objectives
- The data
- Build and publish requirements
- Working with your AI coding agent
- What to submit
- How you will be graded
- Suggested schedule
- Getting started
- Citation and license

Keep it that way. A change to a shared section must go into all three documents, and that happens automatically because the text lives once in `content.js`.

**What students submit** (in every variation):

- The repository URL
- The github.io site URL
- A README.md with data notes and "How we checked our numbers"
- An AGENT_LOG.md
- A reflection of 400 to 600 words

The grading rubric (100 points: Accuracy 25, Data handling 15, Communication 20, Visualization 20, Engineering and publishing 10, Agent process and reflection 10) is identical in all three documents.

**What you may change:**

- Fix anything that is wrong, unclear or unworkable, based on your data checks (section 7) or the pilot (section 8). Record every change in your report, with the reason.
- Do not add answers, hints or example questions to any student document.
- Do not narrow Variation 1 or add example questions to Variation 3.

Also make the students' copy of the data description sheet. Remove "Suggested starting questions" (see section 3), and change nothing else. Produce it in two forms:

- **Markdown,** named `data_description_sheet.md`. The setup guide tells students to put this file in their repository's `docs/` folder.
- **Word,** for reading.

## 6. Deliverables

Write everything under `output/`, with clear file names. Keep student files and instructor files in separate folders, so an instructor can tell at a glance what to hand out. The repository is public, so the instructor files will be public too. Park has accepted that.

**For students:**

- The three case documents and the setup guide, revised if needed and rebuilt
- The students' copy of the data description sheet (markdown and Word)
- The dataset files, unchanged

**For instructors only:**

- Instructor orientation (section 9.1)
- Variation 2 answer key, as a Word document and a matching Excel workbook (section 9.2)
- Reference code (section 9.3)
- Reference sites, one per variation, each ready to publish with GitHub Pages (section 10)
- Post-assignment survey (Appendix B)

**For Park:**

- The updated `content.js`, plus the markdown source and build script for every new Word document
- `REPORT.md` (section 14)

## 7. Variation 2: checks to run

The Variation 2 definitions match the rules in `docs/reference_figures.md`:

- **Valid sale:** a price of $1,000 or more
- **Price per square foot:** computed for each sale with a living area of at least 100 square feet, then take the median
- **Days on market:** `contract_date` minus `list_date`
- **Medians,** not means

So the Question 1 and Question 2 medians by campus area should match Appendix A.

Before you build the answer key, check each question:

- **Every question has a clear answer that is not trivial.**
- **Question 3 (campus area by distance band)** will have small cells. The case already says to show "fewer than 20 sales" in place of the figure for any group under 20 sales. Confirm that the question still produces a meaningful pattern. If it doesn't, propose a fix.
- **Question 4:** sale dates run from 2023-03-27 to 2026-03-25, and listing dates start earlier. Check that every calendar month has enough listings. If the oldest listing years distort the result, propose restricting the question to a stated window.
- **Question 5:** the medians run from 0.18 (Penn State) and 0.33 (Michigan) to 1.00 (UC Davis), with the other eight areas between 0.78 and 1.00.
    - Do not assume a state's statutory assessment level shows up in this data. Illinois assesses most property at one third of market value, yet the Illinois ratio here is 0.82.
    - The Variation 2 sample site explains Pennsylvania (base-year assessments), Michigan (assessed value at about half of market value, with taxable value capped until a sale) and California (reassessment at market value on a change of ownership), with sources. Verify these, and put the explanation and the sources in the answer key only.
    - The student document asks the question and gives no hint.
- **Question 6** should reproduce the description sheet's figures: 240 sales at 103 addresses in total.

If a question needs to change, change it in `content.js`, rebuild, and explain the change in your report.

## 8. Pilot test

Pilot each variation before you finalize anything:

1. Start a fresh agent session for each variation. Give it only that variation's student files (the case document, the setup guide, the students' copy of the description sheet and the data) and this instruction: "You are a student. Complete this assignment."
2. Have it work in a local git repository, and preview the site with a local web server instead of publishing.
3. Record:
    - What the agent had to guess
    - What it misread
    - How many steps it took
    - Which of the five data problems it fell into
4. Revise the student documents to remove ambiguity, without handing over answers.
5. Summarize the findings in your report and in the orientation's "What to expect" section.

You may start a reference site from a pilot build, but the finished reference site must meet every requirement in section 10.

## 9. Instructor materials

### 9.1 Instructor orientation

Include:

- **Case summary and learning objectives**, matching the case documents.
- **The three variations:** what differs, what each is meant to test, and when an instructor might choose each one.
- **Running the case:**
    - One-week and two-week timelines
    - Individuals or teams
    - Prerequisites (none, and no coding experience is needed)
    - Suggested class time: a 20-minute kickoff in which the instructor uses an agent to publish a one-chart page to GitHub Pages, a mid-point check-in, and an optional showcase
- **What to expect:** the setup problems and misreadings found in the pilot, and how to help students past them.
- **The five data problems:** how each one shows up in student work, and how to spot it quickly. Use the "Four things to check" list in `reference_figures.md` as a starting point.
- **Grading:** how to apply the rubric. For Accuracy:
    - **Variations 1 and 3:** the grader picks three headline numbers and recomputes them with the reference code, under the student's stated definitions.
    - **Variation 2:** the grader compares the site with the answer key, using the key's tolerances.
- **Debrief discussion questions.**
- **Running the variations as a comparison:**
    - Hold constant: the dataset, the deliverables, the time allowed, the rubric, the setup guide and the allowed tools.
    - Assignment: random assignment within a section is strongest. Assigning by section or semester is easier, but it mixes the variation with differences in instructor, timing and cohort. Say so plainly.
    - What to measure: rubric scores by criterion; accuracy of headline numbers; which data problems were handled; number of distinct visualizations; self-reported hours; survey responses (Appendix B); and the length of the agent log.
    - Blind grading where possible. Variation 2 sites are recognizable, so note that limit.
    - Research use: if results will be collected for research or publication, consult the campus IRB before the assignment runs.
- **Reference sites:** what each one demonstrates and how to open it.

### 9.2 Variation 2 answer key

Produce a Word document and a matching Excel workbook. For each question, give:

- The figures, as tables
- The chart
- A model answer in plain words
- Common wrong answers and what causes them, with the actual wrong figures computed by your code. Examples: days on market measured to `sale_date`, blanks treated as zero, means instead of medians, deduplication by address, or a median price divided by a median area.
- The tolerance for marking an answer correct

Every number comes from the reference code. Type none by hand.

### 9.3 Reference code

- Python 3.11 or later, using pandas or DuckDB, with pinned versions in `requirements.txt`. It must run offline and give the same output every time.
- One command does all of the following:
    - Reproduces Appendix A and stops if any figure differs
    - Computes every Variation 2 figure and the common wrong-answer figures
    - Writes the answer key workbook
    - Writes the summary files the reference sites read
- Include a short notebook for instructors that recomputes a student's headline number under the student's own stated definitions, with three worked examples.

## 10. Reference sites

Two sample sites already exist, in `inputs/sample-sites/`:

| Folder | Variation | What it does |
|---|---|---|
| `v2-six-questions/` | 2 | Answers all six questions. Its figures come from `scripts/build_data.py`, which uses the case's definitions. |
| `v3-close-to-campus/` | 3 | One question for one user (new faculty): a budget and distance tool, with a dot map, a campus comparison and a table. |

Each site includes a README with SQL cross-checks and an honest AGENT_LOG. Both pass these checks: 375 px and 1280 px wide, light and dark, served from a subfolder, no console errors. Review them against section 7 and the rubric, then:

- Build `answers.json` and the answer key from your own reference code, and confirm the two agree.
- Build the missing Variation 1 site.

Build one site per variation. Each is a plausible strong student submission that meets every requirement of its variation and would earn full marks on the rubric:

- **Variation 1:** a free-form site on a topic you choose.
- **Variation 2:** answers all six questions.
- **Variation 3:** one question for one user, following the required structure.

Keep each site at a level a strong student could reach in two weeks with an agent. It should not look like a professional product.

Requirements:

- **Plain HTML, CSS and JavaScript,** exactly as the case requires.
    - Charting libraries are allowed. Save a copy in the site folder rather than loading it from a CDN, so the site still works if a CDN changes.
    - The site reads summary files produced by the reference code, so its numbers always match the answer key.
- **Ready for GitHub Pages:**
    - `index.html` at the root
    - Relative paths only
    - No file or folder name starting with an underscore
    - File names in a consistent case
    - It must work when served from a subfolder, as a project site is (`https://user.github.io/repo-name/`)
- **Aggregates only:** show no individual street addresses.
- **Accessibility:** give each chart a text alternative (a one-sentence summary or a small data table), keep color contrast readable, and make controls usable with a keyboard.
- **Model student files:** each site folder includes its own README.md and AGENT_LOG.md, written as models of what students submit.
- **Testing:**
    - Serve each site from a subfolder with a local web server, and test it with a headless browser at 375 px and 1280 px wide.
    - It must have no console errors, every control must work, and the numbers shown must match the answer key.
    - Save the screenshots for the report.
- **Ready to publish:** Park will publish the sites with GitHub Pages from the public repository. Make sure each one works from its own subfolder.

## 11. Writing and formatting rules

- Write in plain US English, in short sentences and the active voice. Address students as "you."
- Use no em dashes or en dashes anywhere, including bullet glyphs. Use commas, colons, parentheses or hyphens instead, and use straight quotes.
- Write the Center's name exactly: "University of Illinois-Deloitte Foundation Center for Business Emerging Technologies." Write "University of Illinois Urbana-Champaign," with no "at."
- Every Word document carries the funding line in its footer: "Funded by the University of Illinois-Deloitte Foundation Center for Business Emerging Technologies."
- Use this dataset citation exactly:

  > College-town home sales dataset, version 1.0 (2026). University of Illinois-Deloitte Foundation Center for Business Emerging Technologies. Data collected March 2026.

- Keep all materials tool-agnostic (section 2).
- Every .docx must be editable and clean: no comments, no tracked changes and no hidden text. Leave the author property blank.
- Student documents cite only figures that already appear in the data description sheet.

## 12. Working method

Work in this order:

1. Load and verify the inputs (section 4).
2. Write the reference code, and reproduce Appendix A.
3. Run the Variation 2 checks (section 7).
4. Make the students' copy of the description sheet.
5. Pilot each variation (section 8), then revise `content.js` and rebuild.
6. Build the reference sites.
7. Write the instructor materials.
8. Run the acceptance checks (section 13).
9. Write REPORT.md.

Stop and ask Park, rather than guessing, if:

- An input fails a check
- A Variation 2 question cannot be answered sensibly
- Any step would require changing the dataset
- You would need to publish or upload anything outside this repository

Do not upload anything to Box, the Center website or any other host. Park pushes the repository to GitHub.

## 13. Acceptance checks

- [ ] Your code reproduces every figure in Appendix A exactly.
- [ ] The three case documents differ only in the variation label and "Your task." Show the text diff in your report.
- [ ] No student file contains answers. Search the student files for every answer-key value.
- [ ] No document mentions peer review or auditing other students' work.
- [ ] No document names a specific AI coding agent product or an agent-specific file name.
- [ ] Every .docx opens, is editable, has the funding line, and has no comments, tracked changes or hidden text.
- [ ] No document contains an em dash (U+2014) or an en dash (U+2013).
- [ ] Every number in an instructor document traces to your code's output. List them in the report.
- [ ] The reference code runs from a clean environment with one command.
- [ ] Each reference site works from a subfolder, with no console errors at 375 px and 1280 px wide; its controls work, and its numbers match the answer key.

## 14. Report to Park (REPORT.md)

Include:

1. **Summary:** what was built, and what Park must do next (for example, add the author name, confirm the license, or publish the reference sites)
2. **Contents:** the `output/` tree, with one line per file
3. **Verification:** each acceptance check, marked pass or fail, with evidence
4. **Changes to the student documents,** each with its reason
5. **Pilot findings,** by variation
6. **Open decisions:** each one, with the default used
7. **Web facts:** each fact checked on the web, with the source and the date checked

---

## Appendix A: Dataset facts to reproduce

These figures come from `data_description_sheet.md` and `reference_figures.md`, version 1.0. If your figure differs from one of these, stop and report. Do not change the data or the documents to make them match.

**Whole dataset:**

| Figure | Value |
|---|---:|
| Rows / columns | 35,529 / 34 |
| Cities / states / counties | 18 / 11 / 20 |
| Campus areas | 11 |
| Median sale price | $410,000 |
| Sale dates | 2023-03-27 to 2026-03-25 |
| Rows with both a list date and a contract date | 28,043 (78.9%) |
| Median days on market | 11 |
| Rows sharing a street address with another row | 240, in 103 buildings |
| `living_area_sqft` equal to 0 | 127 rows |
| `home_type` values | 35,350 `SINGLE_FAMILY`; 177 `HOME_TYPE_UNKNOWN`; 2 `CONDO` |
| Prices | 40 under $10,000 (4 under $1,000, one of them $0); 31 over $5,000,000, up to $81,510,000 |
| `miles_to_campus` | 0.2 to 15.1, median 3.4 |

**By campus area.** Prices use sales of $1,000 or more. Price per square foot uses living areas of at least 100 square feet, computed per sale, then the median is taken. Days on market is `contract_date - list_date`, on rows with both dates.

| University | Rows | Median price | Median $/sq ft | Median days on market | Median miles to campus |
|---|---:|---:|---:|---:|---:|
| University of Wisconsin-Madison | 5,707 | $434,020 | $249.16 | 7 | 4.8 |
| University of Florida | 5,630 | $355,000 | $203.24 | 25 | 4.4 |
| Purdue University | 4,616 | $299,900 | $168.24 | 10 | 3.8 |
| University of Illinois Urbana-Champaign | 3,664 | $245,000 | $150.30 | 7 | 2.8 |
| University of Michigan | 3,022 | $571,000 | $259.07 | 7 | 2.7 |
| The University of North Carolina at Chapel Hill | 3,018 | $725,000 | $280.25 | 10 | 3.8 |
| University of Virginia | 2,854 | $625,000 | $272.35 | 7 | 3.5 |
| University of Georgia | 2,816 | $370,000 | $196.82 | 27 | 3.7 |
| The University of Iowa | 1,909 | $342,000 | $175.91 | 24 | 2.2 |
| The Pennsylvania State University | 1,351 | $430,000 | $207.42 | 8 | 2.1 |
| University of California, Davis | 942 | $888,500 | $492.58 | 11 | 2.0 |

## Appendix B: Post-assignment survey (identical in all variations)

Draft items. Refine the wording, but keep the survey identical across variations and anonymous by default.

Rate each statement on a 5-point scale from strongly disagree to strongly agree:

1. I understood what I was supposed to produce.
2. I had enough freedom to make the site my own.
3. I had enough direction to know where to start.
4. I am confident the numbers on my site are correct.
5. I learned how to direct an AI coding agent.
6. I learned something about analyzing real-world data.
7. I would use an AI coding agent for a data project again.

Then ask:

- About how many hours did you spend? (a number)
- What coding experience did you have before this assignment? (none, one course, more than one course)
- Which AI tools did you use?
- What would have helped you most? (open-ended)
