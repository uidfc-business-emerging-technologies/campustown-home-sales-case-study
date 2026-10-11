# Close to Campus

A sample site for the Campus Comps case, Variation 3 (General Instructions).

**Question:** On a new faculty budget, where can you buy a home close to campus?
**User:** newly hired faculty deciding where to buy, and how close to campus they can afford to live.

Pick a campus area, a budget and a distance. The site shows:

- **Three headline numbers:** the share of homes sold nearby that fit the budget, their median size, and how fast they went under contract
- **A dot map** of the sales around the campus landmark
- **A bar chart** comparing all 11 campus areas
- **A table** with every figure

**Live site:** https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/ (replace with the address GitHub Pages gives you)

## What's here

| Path | What it is |
|---|---|
| `index.html` | The page |
| `css/style.css` | Styles, with light and dark themes |
| `js/charts.js` | Small SVG chart helpers written for this site (no libraries) |
| `js/app.js` | Filters the sales and draws the numbers, map, chart and table |
| `data/sales.json` | The 12,254 sales the site uses, with only the columns it needs (492 KB) |
| `data/college_town_home_sales.parquet` | The full dataset (version 1.0) |
| `scripts/build_data.py` | Makes `data/sales.json` from the full dataset |

## Preview it on your own computer

```bash
python -m http.server 8000
```

Then open http://localhost:8000/. Opening `index.html` straight from the file won't load the data.

## Rebuild the data

```bash
pip install pandas pyarrow
python scripts/build_data.py
```

## Data notes

- **Sales used:** the 12,254 sales from March 26, 2025 to March 25, 2026, the most recent 12 months in the data. Prices were fairly steady across all three years (quarterly medians between about $380,000 and $435,000), but a buyer cares about current prices.
- **Left out:** 19 sales under $10,000 in those months, which are not ordinary market sales.
- **Budget** is compared with the sale price only. It doesn't include closing costs, taxes or financing.
- **Distance** is straight-line miles to one landmark per campus (`miles_to_campus`), not travel time.
- **Size** is finished living area. Values under 100 sq ft are treated as missing.
- **Days on market** runs from `list_date` to `contract_date`. Sales missing either date are left out of that figure, and the share missing is shown.
- **Home types:** all are included, because `home_type` is unreliable. Condo units that share an address are kept, because they are separate homes.
- **Small groups:** a median based on fewer than 20 sales is not shown.

## How we checked our numbers

These are the default settings: Illinois, a $400,000 budget, within 3 miles. Each number was recomputed with a separate SQL query in DuckDB, run on the Parquet file instead of through the site's JavaScript.

| Number on the site | Check query | Result |
|---|---|---|
| 93% of homes within 3 miles at or under $400,000 (636 of 685) | `SELECT count(*) FILTER (WHERE sale_price <= 400000), count(*) FROM 'data/college_town_home_sales.parquet' WHERE university = 'University of Illinois Urbana-Champaign' AND CAST(sale_date AS DATE) BETWEEN DATE '2025-03-26' AND DATE '2026-03-25' AND sale_price >= 10000 AND miles_to_campus <= 3` | 636, 685 |
| Median size 1,400 sq ft | `SELECT median(living_area_sqft) FROM ... WHERE` (same filters) `AND sale_price <= 400000 AND living_area_sqft >= 100` | 1400 |
| Median 7 days to go under contract | `SELECT median(date_diff('day', CAST(list_date AS DATE), CAST(contract_date AS DATE))) FROM ... WHERE` (same filters) `AND sale_price <= 400000 AND list_date IS NOT NULL AND contract_date IS NOT NULL` | 7 |

## Tools

An AI coding agent wrote the code with direction and review (see `AGENT_LOG.md`). The data file is built with Python and pandas, and the checks above used DuckDB. The site itself is plain HTML, CSS and JavaScript with no libraries, published with GitHub Pages. The map draws each sale from its latitude and longitude, with no map service.

## Data citation

College-town home sales dataset, version 1.0 (2026). University of Illinois-Deloitte Foundation Center for Business Emerging Technologies. Data collected March 2026.
