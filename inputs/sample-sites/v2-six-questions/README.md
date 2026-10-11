# College Towns in Six Questions

A sample site for the Campus Comps case, Variation 2 (Specific Questions). It answers the case's six questions about 35,529 home sales around 11 university campuses, each with the figures, a chart and a plain-language answer.

**Live site:** https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/ (replace with the address GitHub Pages gives you)

## What's here

| Path | What it is |
|---|---|
| `index.html` | The page |
| `css/style.css` | Styles, with light and dark themes |
| `js/charts.js` | Small SVG chart helpers written for this site (no libraries) |
| `js/app.js` | Loads the data and draws every chart and table |
| `data/answers.json` | Every figure on the site, made by the script below |
| `data/college_town_home_sales.parquet` | The full dataset (version 1.0) |
| `scripts/build_data.py` | Computes `data/answers.json` from the full dataset |

## Preview it on your own computer

The page loads its data with `fetch`, so it needs a local web server. Opening `index.html` straight from the file won't load the data.

```bash
python -m http.server 8000
```

Then open http://localhost:8000/.

## Rebuild the data

```bash
pip install pandas pyarrow
python scripts/build_data.py
```

## Data notes

- **Campus area:** the `university` column (11 areas).
- **Valid sale:** a sale price of $1,000 or more (35,525 of 35,529 sales).
- **Price per square foot:** computed for each valid sale with at least 100 sq ft of living area, then the median of those values.
- **Days on market:** `contract_date` minus `list_date`, only for sales with both dates (28,043). Blanks are never treated as zero.
- **Distance bands:** under 1 mile, 1 to under 2, 2 to under 5, 5 to under 10, and 10 or more, from `miles_to_campus`.
- **Small groups:** fewer than 20 sales shows "Fewer than 20 sales" instead of a figure.
- **Medians, not means.** Prices run up to $81.5 million, which would distort a mean.
- **Repeated addresses** are separate condo or apartment units, so none are removed as duplicates.
- `home_type` is not used, because it is unreliable.

## How we checked our numbers

Each of these was recomputed with a separate SQL query in DuckDB, run directly on the Parquet file instead of through `build_data.py`:

| Number on the site | Check query | Result |
|---|---|---|
| Illinois median sale price, $245,000 (Question 1) | `SELECT median(sale_price) FROM 'data/college_town_home_sales.parquet' WHERE university = 'University of Illinois Urbana-Champaign' AND sale_price >= 1000` | 245000 |
| Georgia median days on market, 27 (Question 2) | `SELECT median(date_diff('day', CAST(list_date AS DATE), CAST(contract_date AS DATE))) FROM 'data/college_town_home_sales.parquet' WHERE university = 'University of Georgia' AND list_date IS NOT NULL AND contract_date IS NOT NULL` | 27 |
| 103 addresses with more than one sale, covering 240 sales (Question 6) | `SELECT count(*), sum(n) FROM (SELECT address_street, city, state, zipcode, count(*) AS n FROM 'data/college_town_home_sales.parquet' GROUP BY ALL HAVING count(*) > 1)` | 103, 240 |

The campus-level medians for price, price per square foot and days on market also match the instructor reference figures that come with the dataset. Those figures round 23.5 days up to 24.

## Tools

An AI coding agent wrote the code with direction and review (see `AGENT_LOG.md`). The summary file is built with Python and pandas, and the checks above used DuckDB. The site itself is plain HTML, CSS and JavaScript with no libraries, published with GitHub Pages.

## Sources cited on the site (Question 5)

- [Pennsylvania tax assessment appeals and common level ratios](https://www.babstcalland.com/news-article/pennsylvania-tax-assessment-appeals-and-common-level-ratios-four-observations/) (Babst Calland)
- [Proposal A brochure](https://lakecountymi.gov/wp-content/uploads/2024/12/2019LC-PropABrochure.pdf) (Lake County, Michigan)
- [Change in ownership questions](https://www.boe.ca.gov/proptaxes/pdf/cioquestions.pdf) (California State Board of Equalization)

## Data citation

College-town home sales dataset, version 1.0 (2026). University of Illinois-Deloitte Foundation Center for Business Emerging Technologies. Data collected March 2026.
