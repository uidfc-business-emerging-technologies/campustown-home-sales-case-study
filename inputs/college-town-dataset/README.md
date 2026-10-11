# College-town home sales

Completed home sales around 11 US university campuses, reduced to the property attributes that
also appear in county assessor and recorder records, with the dates each home was listed, went
under contract and closed. Built as the dataset for a coding-agent case where learners publish a
data-driven site.

**Version 1.0. 35,529 rows, 34 columns, 11 campuses, 18 cities in 11 states. Collected March 2026.**

```
college-town-dataset/
  README.md                          this file
  data/
    college_town_home_sales.csv      8.6 MB
    college_town_home_sales.sqlite   14.6 MB   table: home_sales
    college_town_home_sales.xlsx     5.9 MB    sheets: home_sales, columns
    college_town_home_sales.duckdb             table: home_sales
    college_town_home_sales.parquet
  docs/
    data_description_sheet.md        for learners: hand this out with the data
    dataset_build_notes.md           every decision between source and release
    reference_figures.md             instructor copy: what a correct site should show
    reference_figures_by_city.csv    the same figures, machine readable
    city_campus_map.md               which cities fall under which campus
    city_campus_map.csv              the same, machine readable
  build/
    extract_query.sql                the two queries run against the source database
    build_dataset.py                 dates, cleaning, deduplication, ids, file writing
    make_parquet.py                  CSV to Parquet and DuckDB, checked value by value
    reference_figures.py             instructor figures and the campus map
```

The build inputs, `raw_extract.csv` and `raw_events.csv`, contain the source platform's
property ids and are not distributed.

## Formats

Values are identical in every format. In SQLite and DuckDB the table is `home_sales` and the
primary key is `listing_id`.

| Format | Use it for | Note |
|---|---|---|
| SQLite | Real SQL with no server, and a Python site that reads it | Read-only on serverless hosts. Dates are `YYYY-MM-DD` text |
| CSV | pandas, R, anything | Read ZIP and parcel columns as text |
| Excel | Looking at the data by hand | Leading zeros preserved, dates are real dates |
| DuckDB | Fast local analytics | Real DATE columns |
| Parquet | Columnar workflows | Real date columns |

To regenerate the DuckDB and Parquet files from the CSV:

```bash
pip install duckdb pyarrow
python build/make_parquet.py
```

It reads the CSV in `data/`, writes both files beside it, and checks every value against the CSV
before finishing. Rebuilding everything from the raw inputs is deterministic: same input, same
rows, same `listing_id` values.

## Start here

```sql
SELECT city, state, COUNT(*) AS sales, ROUND(AVG(sale_price)) AS avg_price
FROM home_sales
WHERE sale_price >= 1000
GROUP BY city, state
ORDER BY sales DESC;
```

```python
df = pd.read_csv(
    "data/college_town_home_sales.csv",
    dtype={"zipcode": str, "county_fips": str, "parcel_number": str},
    parse_dates=["list_date", "contract_date", "sale_date"],
)
df["days_on_market"] = (df["contract_date"] - df["list_date"]).dt.days
```

Every row also carries `university` (one of 11) and `miles_to_campus`, both assigned from the
property's coordinates rather than its city label, so campus groups stay clean even where the
city field is wrong.

## Before you aggregate anything

Three characteristics of this data are real and deliberate:

1. **Days on market is `contract_date - list_date`, and needs both.** 78.9% of rows have both.
   The blanks are not random: 38% of Pittsboro sales have no list date, against 5% of
   Lafayette's. `sale_date - list_date` adds about a month of closing time and is not days on
   market.
2. **240 rows share a street address** because they are separate apartments in 103 buildings and
   the source recorded no unit number. Deduplicating by address deletes real homes. Use
   `listing_id` as the key and `parcel_number` to tell units apart.
3. **Prices run from $0 to $81.5 million.** Decide on a rule, state it, apply it consistently.

`docs/data_description_sheet.md` explains each one, along with two more.

## Provenance and limits

Collected in March 2026 from public property listings. Agent and broker names, phone numbers and
emails, listing photos and descriptions, valuation estimates and all platform identifiers were
removed before release. Rows for homes currently being marketed and rows with withheld addresses
were removed, so every row is a completed sale.

Values are as reported by the collection source, not verified against county records.

## Citation

> College-town home sales dataset, version 1.0 (2026). University of Illinois-Deloitte
> Foundation Center for Business Emerging Technologies. Data collected March 2026.
