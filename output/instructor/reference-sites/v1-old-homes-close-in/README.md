# Old Homes, Close In

A site for the Campus Comps case, Variation 1 (Open Brief).

**What it's for:** a short data story for anyone curious about college towns, and especially for someone house-hunting near a campus. It shows how the age of the homes that sold changes with distance from campus, and what a home's age means for its price per square foot. A campus picker shows the same figures for any one of the 11 campus areas.

**Live site:** https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/ (replace with the address GitHub Pages gives you)

## What's here

| Path | What it is |
|---|---|
| `index.html` | The page |
| `css/style.css` | Styles, with light and dark themes. The page uses the reader's system fonts. |
| `js/charts.js` | Small SVG chart helpers written for this site (no libraries) |
| `js/app.js` | Reads the data file and draws the findings, numbers, charts and table |
| `data/age.json` | Every figure on the site, made by the script below (about 18 KB) |
| `data/college_town_home_sales.csv` | The full dataset (version 1.0), which the script reads |
| `docs/data_description_sheet.md` | The dataset's description sheet |
| `scripts/build_data.py` | Computes `data/age.json` from the full dataset |

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

- **Rows used:** all 35,442 sales. Nothing is removed as a duplicate, because condo units share street addresses.
- **Year built** is as reported. One sale has no year built and is left out of the year figures. 192 homes are recorded as built in exactly 1900 and 119 in 1901, against about 25 a year from 1902 to 1909, so many of these are probably a default for "very old, year unknown". They stay in, because they are old homes either way, and the site says so beside the decade chart.
- **Distance** is `miles_to_campus`, the straight-line distance to a campus landmark. Bands: under 1 mile, 1 to under 2, 2 to under 5, 5 to under 10, and 10 or more.
- **Price per square foot** is sale price divided by living area, for each sale of $1,000 or more with at least 100 sq ft of living area (34,934 sales). We take the median of those values, never a median price divided by a median area.
- **New home:** built in the year it sold or the year before, or sold before it was finished (46 homes have a year built later than their sale year). Shares use the 35,435 sales with both a year built and a sale date.
- **Sold without a listing:** the sale has no `list_date`.
- **Medians, not means,** and a median from fewer than 20 sales is not shown.
- **Not used:** `home_type`, which the description sheet says is unreliable.

## How we checked our numbers

Each number below was recomputed with a separate SQL query in DuckDB, run directly on the CSV file instead of through `scripts/build_data.py`.

| Number on the site | Check query | Result |
|---|---|---|
| Median year built within 1 mile of campus, all areas: 1939 | `SELECT median(year_built) FROM 'data/college_town_home_sales.csv' WHERE miles_to_campus < 1 AND year_built IS NOT NULL` | 1939 |
| Homes built in the 1930s, median price per sq ft: $272 | `SELECT median(sale_price / living_area_sqft) FROM 'data/college_town_home_sales.csv' WHERE sale_price >= 1000 AND living_area_sqft >= 100 AND year_built BETWEEN 1930 AND 1939` | 272.30 |
| New homes: 8.0% of sales | `SELECT count(*) FILTER (WHERE year(sale_date) - year_built <= 1), count(*) FROM 'data/college_town_home_sales.csv' WHERE year_built IS NOT NULL AND sale_date IS NOT NULL` | 2,833 of 35,435 (8.0%) |

## Tools

An AI coding agent wrote the code with my direction and review (see `AGENT_LOG.md`). The data file is built with Python and pandas, and the checks above used DuckDB. The site is plain HTML, CSS and JavaScript with no libraries, published with GitHub Pages. I tested it in a headless browser at phone and desktop widths, in light and dark mode.

## Who did what

Individual project.

## Data citation

College-town home sales dataset, version 1.0 (2026). University of Illinois-Deloitte Foundation Center for Business Emerging Technologies. Data collected March 2026.
