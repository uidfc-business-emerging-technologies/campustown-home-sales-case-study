# College Towns in Six Questions

A site for the Campus Comps case, Variation 2 (Specific Questions). It answers the case's six questions about 35,529 home sales around 11 university campuses, each with the figures, a chart and a plain-language answer, for anyone thinking about moving to one of these towns.

**Live site:** https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/ (replace with the address GitHub Pages gives you)

## What's here

| Path | What it is |
|---|---|
| `index.html` | The page |
| `css/style.css` | Styles, with light and dark themes |
| `fonts/` | The two fonts the page uses, saved here so no font service is needed (SIL Open Font License, see the `OFL` files) |
| `js/charts.js` | Small SVG chart helpers written for this site (no libraries) |
| `js/app.js` | Loads the data, fills in every number in the answers, and draws every chart and table |
| `data/answers.json` | Every figure on the site, made by the script below |
| `data/college_town_home_sales.csv` | The full dataset (version 1.0), which the script reads |
| `docs/data_description_sheet.md` | The dataset's description sheet |
| `scripts/build_data.py` | Computes `data/answers.json` from the full dataset |

## Preview it on your own computer

The page loads its data with `fetch`, so it needs a local web server. Opening `index.html` straight from the file won't load the data.

```bash
python -m http.server 8000
```

Then open http://localhost:8000/.

## Rebuild the data

```bash
pip install pandas
python scripts/build_data.py
```

## Data notes

- **Campus area:** the `university` column (11 areas).
- **Valid sale:** a sale price of $1,000 or more (35,525 of 35,529 sales). Questions 1, 3 and 5 use valid sales; the other questions use every sale, as the case says.
- **Price per square foot:** computed for each valid sale with at least 100 sq ft of living area, then the median of those values.
- **Days on market:** `contract_date` minus `list_date`, only for sales with both dates (28,043). Blanks are never treated as zero.
- **Distance bands:** under 1 mile, 1 to under 2, 2 to under 5, 5 to under 10, and 10 or more, from `miles_to_campus`.
- **Falls with distance (Question 3):** "at every step" means each band with 20 or more sales is cheaper than the one before; "overall" means the farthest such band is cheaper than the nearest and no step rises by more than 5%. An area that meets neither does not fall.
- **Listing window (Question 4):** homes listed from April 1, 2023 through March 31, 2025, all campus areas pooled, grouped by the month of `list_date`.
- **Far from 1 (Question 5):** a median ratio below 0.5.
- **Small groups:** a median or share based on fewer than 20 sales shows "fewer than 20 sales". Counts are always shown.
- **Medians, not means.** Prices run up to $81.5 million, which would distort a mean.
- **Repeated addresses** are never removed. In State College they are separate condo units with their own parcel numbers. Around Virginia, most look like one sale recorded twice (the same price and usually the same closing date, with one row from the listing and one from the county record); the site says so in Question 6 but counts every sale, as the question defines.
- `home_type` is not used, because it is unreliable.

## How we checked our numbers

Each of these was recomputed with a separate SQL query in DuckDB, run directly on the CSV file instead of through `build_data.py`:

| Number on the site | Check query | Result |
|---|---|---|
| Illinois median sale price, $245,000 (Question 1) | `SELECT median(sale_price) FROM 'data/college_town_home_sales.csv' WHERE university = 'University of Illinois Urbana-Champaign' AND sale_price >= 1000` | 245000 |
| Georgia median days on market, 27 (Question 2) | `SELECT median(date_diff('day', list_date, contract_date)) FROM 'data/college_town_home_sales.csv' WHERE university = 'University of Georgia' AND list_date IS NOT NULL AND contract_date IS NOT NULL` | 27 |
| April listings, median 6 days on market (Question 4) | `SELECT median(date_diff('day', list_date, contract_date)), count(*) FROM 'data/college_town_home_sales.csv' WHERE contract_date IS NOT NULL AND list_date BETWEEN DATE '2023-04-01' AND DATE '2025-03-31' AND month(list_date) = 4` | 6, from 2,041 listings |
| 103 addresses with more than one sale, covering 240 sales (Question 6) | `SELECT count(*), sum(n) FROM (SELECT count(*) AS n FROM 'data/college_town_home_sales.csv' GROUP BY address_street, city, state, zipcode HAVING count(*) > 1)` | 103, 240 |

The campus-level medians for price, price per square foot and days on market also match the instructor reference figures that come with the dataset. Those figures round Iowa's 23.5 days up to 24.

## Tools

An AI coding agent wrote the code with direction and review (see `AGENT_LOG.md`). The summary file is built with Python and pandas, and the checks above used DuckDB. The site itself is plain HTML, CSS and JavaScript with no libraries, published with GitHub Pages.

## Sources cited on the site (Question 5)

Checked October 11, 2026.

- [Pennsylvania tax assessment appeals and common level ratios](https://www.babstcalland.com/news-article/pennsylvania-tax-assessment-appeals-and-common-level-ratios-four-observations/) (Babst Calland, 2023)
- [2025 Common Level Ratio Real Estate Valuation Factors](https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/taxtypes/rtt/documents/clr_factor_current.pdf) (Pennsylvania Department of Revenue, July 2026)
- [Guide to Basic Assessing](https://www.michigan.gov/-/media/Project/Websites/treasury/Assessors/Guide_to_Basic_Assessing_116.pdf) (Michigan State Tax Commission)
- [Assessors' Handbook Section 401, Change in Ownership](https://www.boe.ca.gov/proptaxes/pdf/ah401.pdf) (California State Board of Equalization)

## Who did what

Individual project.

## Data citation

College-town home sales dataset, version 1.0 (2026). University of Illinois-Deloitte Foundation Center for Business Emerging Technologies. Data collected March 2026.
