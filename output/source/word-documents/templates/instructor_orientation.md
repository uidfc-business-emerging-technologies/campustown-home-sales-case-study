# Instructor Orientation

This orientation is for instructors. It summarizes the case, explains the three variations, and covers running the case, what to expect, the data problems, grading, the debrief and running the variations as a comparison. Every data figure in it comes from the reference code in `instructor/reference-code`.

## The case in brief

AI coding agents can now write most of the code for a data website. That changes the analyst's job. In this case, students decide what to show and who it is for, direct an AI coding agent, and check that every number is right.

Students work with the College-town home sales dataset (version 1.0): {{rows}} completed home sales around {{campuses}} university campuses, in {{cities}} cities across {{states}} states, collected in March 2026. They build a website with visualizations in plain HTML, CSS and JavaScript, keep the code in a public GitHub repository, and publish the site with GitHub Pages.

Students may use any AI coding agent or assistant, and may edit code by hand. The case gives no tool-specific steps, because tools change quickly.

### Learning objectives

By the end of the case, students will be able to:

- Direct an AI coding agent to build a data website from plain HTML, CSS and JavaScript
- Explore an unfamiliar real-world dataset and handle its data quality problems
- Choose and design visualizations that communicate findings to an audience
- Check AI-produced analysis independently
- Publish and update a website with GitHub and GitHub Pages

## The three variations

The three case documents are identical except for the variation label and the "Your task" section. The setup guide, the deliverables, the rubric and the schedule are the same in all three.

| Variation | What students get | What it tests | Choose it when |
|---|---|---|---|
| 1. Open Brief | Complete freedom: topic, audience, design and scope are theirs | Whether students can find a question in unfamiliar data, scope a project and direct an agent with little structure | Students have some data experience, or you want to see initiative and judgment |
| 2. Specific Questions | Six questions, with fixed definitions and an answer key | Precise reading of definitions, accuracy against a known answer, and handling the data problems the questions expose | You want comparable, checkable work, or students are new to data analysis |
| 3. General Instructions | A required structure (a question for a named user, three headline numbers, two charts or maps with a control, data notes) and a suggested process | Framing a question for a real user and building an interactive tool, with scaffolding but no fixed answer | You want guided independence and a product a user could act on |

## Running the case

### Prerequisites

None. Students need no coding experience. Each student needs:

- A free GitHub account
- A web browser
- Access to an AI coding agent or assistant that can read and edit files in a project folder

Check what agent access your institution provides before the case starts.

### Timelines

The case documents give a two-week schedule and tell students to compress it for one week. Give students exact dates.

| Milestone | Two weeks | One week |
|---|---|---|
| Accounts, repository, first page published on GitHub Pages | Days 1 and 2 | Day 1 |
| Check-in: site URL and one paragraph on the plan | Day 7 | Day 3 or 4 |
| Submit | Day 14 | Day 7 |

### Individuals or teams

Every case document works for individuals or for teams of 2 to 3. Teams submit once, from one shared repository, and the README says who did what. Every team member must be able to explain how each number on the site is computed, so ask any member at random during the check-in.

### Class time

- **Kickoff (20 minutes).** Use an agent, live, to publish a one-chart page. Create a public repository, turn on GitHub Pages, ask the agent for a page that loads the CSV and shows the number of rows ({{rows}}), then one chart. Push, and open the github.io address. Then check one number a second way, such as the row count in a spreadsheet. Rehearse once beforehand: the first publish takes a few minutes.
- **Mid-point check-in.** Open each site's URL and read the plan paragraph. Catch problems early: a site that does not load, a number that looks wrong, or a plan too large for the time left.
- **Optional showcase.** Students show their sites for two minutes each. In Variation 1 and 3 sections, the range of topics is the point. In Variation 2 sections, compare how sites presented the same answers.

## What to expect

Before release, each variation was piloted. A fresh AI agent was given only that variation's student files (the case document, the setup guide, the students' copy of the data description sheet and the data) and the instruction "You are a student. Complete this assignment." Each pilot worked in a local git repository and previewed its site with a local web server instead of publishing. Each produced a working site with a README, an agent log and a reflection in one working session.

### What the pilots had to guess

The case documents were revised to remove the guesses that came from unclear wording:

- **Where the reflection goes.** All three pilots asked. The documents now say to submit it to you, not to put it in the repository.
- **Whether the full CSV must stay in the repository** once the site reads only a smaller summary file. The documents now say to commit the script and the data file it reads.
- **What counts as a separate check** of a number. The documents now say the calculation must be separate from the site's own code.
- **Variation 2 definitions:** which questions use valid sales only, whether the small-group rule applies to counts, what counts as price per square foot "falling" with distance, what "far from 1" means, and whether to compare within each area or across all areas. Each is now stated, without giving away an answer.

Some choices are left to students on purpose, and pilots hesitated over them too: which prices to keep, the smallest believable living area, what "near campus" means, and which time window to use. Expect these questions. The answer is the same each time: choose a rule, state it in the data notes, and apply it everywhere.

### Setup problems to expect

The setup guide's "Common problems" table covers the usual ones. Expect these:

- **Paths.** A path that starts with `/`, or a file name whose capitalization differs, works on a student's computer but not on GitHub Pages.
- **Opening the page from the file.** Data will not load from a page opened as `file://`. Students need a local web server.
- **Pages not turned on,** or the wrong branch or folder selected.
- **An old copy in the browser** after a push. A reload without the cache fixes it.
- **The project instructions file.** Its name depends on the agent. Students should check their agent's documentation; the setup guide gives the text to put in it.

When a student is stuck, ask for the exact error from the browser's Console tab. Most problems are visible there.

### How pilots handled the data, and what students may do differently

None of the pilots fell into the five data problems below. Each pilot read the data description sheet before writing any analysis code, as the case tells students to do. Students who skip that step, or who never give the sheet to their agent, are the ones most likely to fall into them. In the kickoff, show the sheet and say plainly that the agent must read it first.

### Agent logs

The case asks for at least one time the agent got something wrong. Every pilot found real mistakes to log, so students should too. Still, a student could invent one. Ask for prompts pasted verbatim, and compare the log's dates and claims with the repository's commit history.

## The five data problems, and a sixth

The data description sheet explains five problems under "Five things that will bite you." The dataset keeps them on purpose. Here is how each one shows up in student work, and how to spot it quickly. The reference figures that come with the dataset, and the answer key, give the correct values.

### 1. Days on market

Days on market runs from `list_date` to `contract_date`, and needs both dates. {{dom_rows}} sales ({{dom_share}}) have both. The median is {{dom}} days, and the median for each campus area runs from {{dom_area_min}} to {{dom_area_max}} days.

- **Measured to `sale_date`:** the overall median becomes {{dom_to_close}} days, because it adds the time to close. Around Michigan, {{mich_dom_to_close}} days instead of {{mich_dom}}.
- **Blank dates treated as zero:** the overall median falls to {{dom_blank_zero}} days, and many homes appear to sell instantly.
- **A mean instead of a median:** {{dom_mean}} days, pulled up by homes that took over a year.
- **Spot it:** is the overall median close to {{dom}} days? Is it about a month too long, or close to zero for many homes?

The missing dates are not random: off-market and new construction sales are the ones without a list date. A strong site says that its days-on-market figures describe listed homes only.

### 2. Repeated street addresses

{{shared_rows}} sales share a street address with another sale, at {{shared_addresses}} addresses. The sheet says they are condo and apartment units with no unit number.

- **Deduplicated by address:** the row count drops by {{dedup_loss}}, from {{rows}} to {{after_dedup}}, and the condo units in State College disappear.
- **Grouped by street name alone,** without city, state and ZIP code: {{street_rows}} rows look repeated instead of {{shared_rows}}, because the same street name appears in different towns.
- **Spot it:** does the site's row count, or a city's total, fall short of the description sheet's?

### 3. Impossible prices

Prices run from $0 to {{max_price}}. {{price_under_1000}} sales are under $1,000, including {{price_zero}} at $0; {{price_under_10000}} are under $10,000; {{price_over_5m}} are over $5,000,000.

- **A mean instead of a median:** the mean price is {{mean_price}}, against a median of {{median_price}}.
- **No stated rule:** a minimum or maximum shown on the site is $0 or {{max_price}}.
- **Spot it:** a median far above the reference figures usually means a mean. Any rule is acceptable if the site states it and applies it consistently.

### 4. The home_type column

{{single_family}} of the {{rows}} rows say `SINGLE_FAMILY`, including the condo units in State College. Any chart split by `home_type` is meaningless. Spot it by searching the site and its code for `home_type`.

### 5. Values that are impossible on their face

{{zero_sqft}} homes have 0 square feet of living area, and some have none recorded.

- **Divided anyway:** price per square foot comes out in the thousands, or as "Infinity". In JavaScript, a blank living area also divides to Infinity. Around Georgia, where {{ga_area_missing}} sales have no living area, the median becomes {{ga_pps_blank_zero}} instead of {{ga_pps}}.
- **Spot it:** any price per square foot in the thousands, or the word Infinity on the page.

### 6. Repeated addresses that are one sale recorded twice (not in the student documents)

The description sheet says all {{shared_rows}} repeated-address sales are separate units. That is true in State College, where {{psu_addresses}} buildings hold separate units with their own parcel numbers. But {{double_addresses}} of the {{shared_addresses}} addresses ({{double_rows}} rows) meet the dataset build notes' own test for one sale recorded twice: two rows, prices within 1% and sale dates within 90 days. {{double_va}} of them are around Virginia, mostly new homes. In most pairs, one row carries the listing dates and the other carries the county's parcel number and assessed value, so the build's parcel check missed them. Only {{real_addresses}} addresses ({{real_rows}} rows) look like real multi-unit buildings.

The effect on most figures is small. With one copy of each pair removed, Virginia's median sale price would be {{va_price_one_copy}} instead of {{va_price}}. The effect is larger where the pairs dominate a figure: Variation 2's Question 6, and any share of new homes around Virginia.

The case documents still tell students never to remove a sale just because its address repeats, which remains right for State College. Do not mark down a student who keeps every row. Give credit under Data handling to a student who spots the double records, explains them, and either keeps them with a note or removes one copy with a stated rule. One Variation 2 pilot found them on its own.

## Grading

The rubric has 100 points and is identical in all three variations.

| Criterion | Points | What to look for |
|---|---:|---|
| Accuracy | 25 | Numbers on the site can be reproduced from the data under the definitions the site states, or, in Variation 2, the case's definitions |
| Data handling | 15 | The data problems that affect the site's numbers are handled correctly and explained in the data notes |
| Communication | 20 | A visitor understands the site's purpose within 10 seconds, findings are stated in words, and the content suits its audience |
| Visualization | 20 | Chart types fit the data; axes and units are labeled; charts work on a phone; controls work |
| Engineering and publishing | 10 | The site loads at its github.io address; the repository is tidy; the README is complete; no secrets anywhere |
| Agent process and reflection | 10 | The agent log shows the student directing and checking the agent, and the reflection is specific |

### Accuracy

**Variations 1 and 3.** Pick three headline numbers from the site. For each one, read the student's stated definitions in the data notes or README, then recompute the number with the notebook `instructor/reference-code/recompute_student_number.ipynb`. Its three worked examples show how. If the notebook reproduces the number, it is accurate, even when the definition is weak: judge the definition under Data handling. If it does not reproduce, look for an unstated rule before marking it wrong. A reasonable scale: 25 points if all three reproduce, 17 for two, 8 for one.

**Variation 2.** Compare the site with the answer key (`Variation 2 Answer Key.docx`, with the same figures in the `.xlsx` workbook). The key gives a tolerance for each question that allows for rounding but not for a different definition. Its "Common wrong answers" tables show the exact figure each common mistake produces, so you can name the mistake from the number alone.

### Quick checks for any site

1. **Does the row count or a city's total match the description sheet?** If it is short, the student probably removed sales by address.
2. **Does a median look like the reference figures?** One far too high usually means a mean.
3. **Is price per square foot plausible?** Thousands, or Infinity, means a zero or blank living area was divided.
4. **Is days on market about a month too long?** Then it was measured to `sale_date`. Near zero for many homes means blanks were treated as zero.

## Debrief discussion questions

1. Which decisions did you make, and which did the agent make? Which should it have left to you?
2. Where did the agent's output look right but turn out to be wrong? What made you check?
3. What rule did you choose for implausible prices, and how much did it change your numbers? Is there one right rule?
4. Who is missing from "days on market"? How should a site talk about a figure that covers only some of the sales?
5. The description sheet says repeated addresses are condo units. Did you check? When should you trust a dataset's documentation, and how would you find out it is wrong?
6. How would a visitor know whether to trust your site's numbers? What did you show them?
7. If you started again with the same agent, what would you tell it first?

If you ran more than one variation, add: did more freedom or more direction lead to better work, and better learning? Why?

## Running the variations as a comparison

The three variations differ only in how much direction students get, so they can be compared.

**Hold constant:** the dataset, the deliverables, the time allowed, the rubric, the setup guide and the tools students may use. Give every group the same kickoff.

**Assignment.** Random assignment of students (or teams) to variations within a section is the strongest design: each variation then gets the same instructor, the same timing and the same mix of students. Assigning by section or by semester is easier to run, but it mixes the effect of the variation with differences in instructor, timing and cohort, and no analysis can separate them afterward. Say so plainly when you report results.

**What to measure:**

- Rubric scores, by criterion
- Accuracy of headline numbers (in Variations 1 and 3, the share of the three checked numbers that reproduce)
- Which data problems each site handled, and which it fell into
- Number of distinct visualizations
- Self-reported hours
- Post-assignment survey responses
- Length of the agent log

**Blind grading.** Remove names and variation labels before grading where you can. Variation 2 sites answer the same six questions, so graders will recognize them; note that limit when you compare scores.

**The survey.** The post-assignment survey is identical in every variation and anonymous by default. To group responses by variation without asking students, give each variation its own copy of the survey link.

**Research use.** If you will collect results for research or publication, consult your campus Institutional Review Board before the assignment runs.

## Reference sites

Each reference site is a plausible strong student submission that meets every requirement of its variation and would earn full marks. Each folder includes a model README and agent log. Each site reads a summary file written by the reference code, and its own build script produces the same file.

| Folder | Variation | What it demonstrates |
|---|---|---|
| `v1-old-homes-close-in` | 1. Open Brief | A free-form data story: housing age by distance from campus and price per square foot by decade built. It shows findings stated in words, a campus picker driving every chart, a dot plot for years, and data notes that handle the {{built_1900}} homes recorded as built in exactly 1900 and Virginia's double records. |
| `v2-six-questions` | 2. Specific Questions | All six answers, each with figures, a chart and plain words. Every number on the page is filled in from the data file. It applies the small-group rule, states its rules for "falls" and "far from 1", and cites sources for Question 5. |
| `v3-close-to-campus` | 3. General Instructions | One question for one user (new faculty on a budget): a campus picker, budget slider and distance buttons drive three headline numbers, a dot map, a campus comparison and a table. |

**To open a site** on your own computer, start a web server in the `instructor/reference-sites` folder:

```
python -m http.server 8000
```

Then open, for example, http://localhost:8000/v1-old-homes-close-in/. Once the repository is published with GitHub Pages, each site is also at `https://OWNER.github.io/REPOSITORY/output/instructor/reference-sites/FOLDER/`.

The repository is public, so students can find these sites and the answer key. Decide whether that matters for your course before you assign it.

## What is in the package

| Folder | For | Contents |
|---|---|---|
| `students/` | Students | The three case documents, the setup guide, the data description sheet (Word and markdown) and the dataset in five formats |
| `instructor/` | Instructors | This orientation, the Variation 2 answer key (Word and Excel), the post-assignment survey, the reference code and the reference sites |
| `source/` | Case author | The source and build scripts for every Word document |

Give each student only their variation's case document, plus the setup guide, the description sheet and the data.
