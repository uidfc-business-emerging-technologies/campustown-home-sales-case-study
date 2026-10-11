# College-town home sales dataset: how it was built

Version 1.0. Built 2026-10-02; sales recorded twice under two parcel numbers removed
2026-10-11, before publication (section 6). Final dataset: **35,442 rows, 34 columns**.

This document records every decision and transformation between the source database and the
published files, so the dataset can be rebuilt, checked or revised later.

## Files

| File | What it is |
|---|---|
| `build/extract_query.sql` | The two queries run against the source database |
| `build/build_dataset.py` | The build: dates, cleaning, deduplication, ids, file writing |
| `build/make_parquet.py` | Converts the published CSV to Parquet and DuckDB using the build's own schema, then checks both value by value |
| `build/drop_double_records.py` | Applies the section 6 two-parcel rule to the published CSV and rewrites all five files, for use without the raw files |
| `build/removed_double_records.csv` | The 87 rows that rule removed, each beside the row kept for the same sale |
| `build/reference_figures.py` | Instructor figures and the city to campus map |
| `build/raw_extract.csv` | Query 1 output, unmodified. **Not for publication**, see section 13 |
| `build/raw_events.csv` | Query 2 output, unmodified. **Not for publication**, see section 13 |
| `data/college_town_home_sales.{csv,sqlite,xlsx,duckdb,parquet}` | The published dataset |

---

## 1. Source

| | |
|---|---|
| Platform | PlanetScale Postgres |
| Organization / database / branch | `subwaymatch` / `hasdata-data-collection` / `main` |
| Table | `public.zillow_properties` |
| Rows in source table | 36,469 |
| Columns in source table | 154, including JSON columns |
| Collected | 2026-03-24 to 2026-03-26, via HasData |
| Coverage | 84 city and state combinations, concentrated in 14 US college towns |

## 2. Row filters

Applied in `extract_query.sql`:

| Filter | Rows removed | Why |
|---|---:|---|
| `status IN ('SOLD','RECENTLY_SOLD')` | 609 | Removes homes currently being marketed (for sale, pending, for rent, foreclosure). Every remaining row is a completed sale, and no currently listed home appears with its address and price. |
| `COALESCE(address_undisclosed, false) = false` | 38 | Rows where the address was deliberately withheld. 40 rows in the table carry the flag; 2 were already removed by the status filter. |

36,469 - 609 - 38 = **35,822 rows extracted**.

## 3. Column selection

The test applied to each column: does this value also appear in a county assessor or recorder
record?

**Kept**: street address, city, state, ZIP, county, county FIPS, parcel number, latitude,
longitude, sale price, home type, beds, baths, living area, lot size, year built, stories,
basement, garage and garage capacity, cooling, heating, fireplace, architectural style, roof
type, annual tax amount, assessed value, high school district. From `price_history`, only each
event's **date and type** (listed, price change, pending, contingent, removed, listed for rent,
sold), which is where the three dates come from.

**Extracted but never used**: `date_posted`. Despite its name it is not the sale date (section
4.1). It stays in the extract so that check can be repeated, and the build drops it on load.

**Deliberately excluded**:

| Columns | Reason |
|---|---|
| `agent_name`, `broker_name`, `buyer_agent_name`, `buyer_broker_name`, `agent_phone_number`, `broker_phone_number`, `agent_emails` | Named individuals and their contact details. Present on about 31,000 of the extracted rows. |
| `zestimate`, `rent_zestimate`, `rent_zestimate_url`, `zestimate_low_percent`, `zestimate_high_percent`, `days_on_zillow` | Proprietary model output and platform-specific metrics, not facts about the property. Days on market is computed from the event dates instead. |
| `property_id` (ZPID), `url`, `image`, `photos`, `static_map_urls`, `nearby`, `raw_json` | Platform identifiers and media. Keeping them would make the file joinable straight back to the source site. |
| `description` | Copyrighted agent-written listing remarks, which also contain names and phone numbers. |
| `schools` | Licensed third-party school ratings. The district name survives in `school_district`. |
| Event prices and price-change rates in `price_history`; all of `tax_history` | Compiled histories, left for a possible second table. |
| The remaining RESO and raw-text columns | Dropped for usability, not risk. |

`property_id` is read by the build as the key that joins the two extracts and as a deterministic
tie-break, and is dropped before any file is written. It appears in no published file.

## 4. Dates

### 4.1 Why not `date_posted`

The source has a column called `date_posted` that is easy to mistake for the sale date, and an
early draft of this build did. Checked against each property's recorded history:

| `date_posted` equals | Rows | Share of the 31,373 dated rows |
|---|---:|---:|
| the date the home went on the market (`reso_on_market_date`) | 26,272 | 84% |
| the actual sale date | 390 | 1.2% |

The median gap from listing to sale is 51 days, so most `date_posted` values are about seven
weeks before the sale. The 4,449 extracted rows with no `date_posted` all have a recorded sale,
so a dataset built on that column would show 12.4% of sale dates missing when only 6 rows truly
lack one. One `date_posted` even falls after the collection window; no recorded sale does, the
latest being 2026-03-25.

`price` was checked the same way and is correct: it equals `last_sold_price` on all 35,822
extracted rows and the price of the most recent sold event on every row that has one, with no
disagreements.

### 4.2 Where the dates come from now

`raw_events.csv` holds every property's history as one row per event: 284,955 events across
35,816 properties (6 properties have an empty history). Every event has a date, and every date
agrees with the event's own timestamp.

| Event | Count | Properties |
|---|---:|---:|
| `sold` | 84,391 | 35,816 |
| `listedForSale` | 68,699 | 32,305 |
| `priceChange` | 46,000 | 16,470 |
| `pendingSale` | 39,162 | 26,627 |
| `listingRemoved` | 25,514 | 12,690 |
| `contingent` | 10,921 | 9,478 |
| `listedForRent` | 10,268 | 4,942 |

### 4.3 The rule

Implemented in `derive_dates()` in `build_dataset.py`, with nine worked examples that the build
runs before every build (`--check-rules` runs them alone).

1. **`sale_date`** is the most recent `sold` event. Only events after the sale before it belong
   to this sale.
2. **`contract_date`** is the start of the last unbroken run of `pendingSale`/`contingent`
   events before the sale. It is left blank if it is more than **365 days** before closing (an
   old contract that did not produce this sale), or if the listing was withdrawn more than
   **90 days** before closing (the deal fell through).
3. **`list_date`** is the start of the listing that led to the contract, or to the sale when
   there is no contract. A `listingRemoved` or `listedForRent` event ends a listing. Coming back
   on the market after a failed contract does not, so the clock keeps running from the original
   listing. A silence of more than **365 days** with no recorded event means the listing had
   lapsed; the clock restarts at the next listing if there is one, and is left blank if not.

Days on market is `contract_date - list_date`. Time to close is `sale_date - contract_date`.

### 4.4 Alternatives that were tested and rejected

| Rule | Problem |
|---|---|
| First listing after the previous sale | Reaches back to listings years before the sale: listing-to-sale gaps with a 95th percentile of 1,097 days and a maximum of 18 years |
| Most recent listing before the sale | Restarts the clock when a failed contract puts the home back on the market. That cuts days on market on about 7% of rows, by a median of 30 days, for exactly the homes that had trouble selling |
| First contract after the listing | Picks contracts that fell through years earlier: one 11-year escrow. The last contract before the sale is the one that closed |
| No withdrawal or silence checks | Attaches listings withdrawn long before an off-market sale: a 2011 listing to a 2025 sale |

Withdrawals are not routine closing noise. Of the 940 sale cycles with a `listingRemoved`
between listing and sale, only 17 fall within 3 days of closing, and the median is 152 days
before it.

### 4.5 Evidence the rule reads the history correctly

| Check | Result |
|---|---|
| Time to close, contract to sale | Median 31 days, quartiles 24 and 42: a normal escrow |
| Ordering | `list_date` <= `contract_date` <= `sale_date` on every row |
| Long escrows that survive the cap | 263 rows close 6 to 12 months after contract; 89% are homes built that year or the year before, where buyers sign before construction ends (6% across all other sales) |
| Sale dates and prices against the database | An independent SQL computation of every property's latest sale date and price produces the same checksum as the build, over all 35,816 properties |
| Read-through | Histories inspected by hand for every outcome: both dates, list only, contract only, withdrawn, lapsed, stale contract, fell through, zero days on market, back on market |

### 4.6 What the rule decided, on the published rows

| | Rows |
|---|---:|
| Both `list_date` and `contract_date` (days on market computable) | 28,042 |
| `list_date` only | 1,220 |
| `contract_date` only | 872 |
| Neither | 5,308 |
| Clock kept running after a failed contract | 2,020 or 2,021, see below |
| Listed and under contract the same day | 384 |
| Under contract on the closing day | 68 |

Blank dates, as the build counted them on its 35,529 rows before the section 6 two-parcel step:
`list_date` 6,266, of which no listing on record 5,281, withdrawn before a contract 857, lapsed
122 and no history 6; `contract_date` 6,614, of which no contract status recorded 6,411, contract
over a year before closing 147, fell through 50 and no history 6.

That step removed 87 rows. 86 had neither date, so the published file has 6,180 blank list dates
and 6,528 blank contract dates. Which reason each of the 86 had is not recorded in the published
files, so the split above can be off by up to 86 in any one reason; the remaining row had the same
list and contract dates as the row kept for its sale (130 Brickleberry Rdg, Athens), which is why
the clock-kept-running count is one of two values. A rebuild from the raw files prints the exact
split (section 14).

Days on market: median 11, quartiles 4 and 41, 90th percentile 95, maximum 677 days; 67 rows over
a year, all listings with recorded activity throughout.

## 5. Cleaning

Applied in `build_dataset.py`, in this order.

**5.1 Whitespace.** Every text column trimmed; internal whitespace collapsed in the key fields
used for matching.

**5.2 Placeholder values treated as missing.** 4 `parcel_number` values (`NA`, `NONE`,
`unknown`, `.`), 2 `roof_type` values (`None`, `Unknown`), and 9 `school_district` values (`NA`).
Left as text, these would survive into the CSV, where pandas reads a literal `NA` back as missing
anyway, so the file would disagree with itself depending on the reader.

**5.3 City spelling normalized (22 rows).** `URBANA` beside `Urbana`, `Ann arbor` beside `Ann
Arbor`, `Iowa city` beside `Iowa City`, and similar in Athens, Chapel Hill, Charlottesville,
Middleton and West Lafayette. Each spelling group collapses to its most common form, with ties
going to the alphabetically first spelling so the result never depends on row order. This is
the only value in the dataset that was rewritten. `--keep-city-variants` turns it off.

**5.4 Strict typing.** Every numeric column must parse; the build stops rather than silently
turning a malformed value into a blank. None did: no value in the extract was lost to type
conversion, and the flag columns contain only `true`, `false` and blanks.

## 6. Deduplication

A street address is not a unique key: 141 addresses appear on more than one row in the extract,
covering 316 rows. Every one of those rows has a parcel number, and the parcel number, the price
and the date separate three situations. `drop_duplicate_properties()` handles the first and calls
`drop_double_records()` for the second.

**Same address, same parcel: one property listed twice (38 pairs).** The source holds the
property under two platform ids. In 37 pairs it is the same sale recorded twice, with prices
within 1% and sale dates within 90 days, often with one copy missing its living area. The build
keeps the most complete copy, then the later date, then the lower source id. One pair is a
genuine resale (4236 Barbaro Ave, Iowa City: $570,000 in March 2024, then $590,000 in August
2024), and the build keeps the later sale. **Removed: 38 rows.**

That leaves 240 rows at 103 addresses where the parcel numbers differ.

**Same address, two parcel numbers, one sale (87 pairs).** At 87 of those addresses there are
exactly two rows, and they pass the same test as the pairs above: prices within 1% (identical in
85 pairs) and sale dates within 90 days (all within 5 days). They are one sale that the source
holds twice. Typically one record is the listing's, with the list and contract dates, and the
other is the county's, with the assessed value (86 of the 87 removed rows have one, against 7 of
the rows kept) but no listing dates. In 66 pairs the listing's record has a placeholder where the
county's has the full parcel number: `0` (17), a lot or homesite number such as `109` or
`Homesite 19` (37), or `062000000016D1`, a parcel number that 14 new homes on two Charlottesville
streets share (12). In the other 21 pairs the two parcel numbers differ in format (`61A42C` and
`061A00000042C0`, `244C5 A003` and `244C5A003`) or in a few digits. 79 of the 87 are in
Charlottesville. The build keeps the more complete record, then the later date, then the lower
source id, as for same-parcel pairs. That keeps the listing's record in 84 pairs; in one pair both
records carry the same dates, and in two neither does. **Removed: 87 rows.**
`build/removed_double_records.csv` lists each removed row beside the row kept for the same sale,
so the county's parcel number and assessed value can be recovered where the kept row lacks them.

Only addresses with exactly two rows qualify. In larger buildings, units of similar size can sell
for the same price within weeks of each other: three pairs in State College buildings pass the
price and date test (two at 456 E Beaver Ave, one at 200 Highland Ave), but each unit has its own
unit parcel and a different living area, so they are kept.

This step was added on 2026-10-11, before publication. The first build kept all 103 addresses as
units in one building; checking that claim showed that 87 of them held one sale twice, 79 of them
in Charlottesville. The raw files were not at hand, so the published files were corrected with
`build/drop_double_records.py`, which applies the same function to the published CSV. No pair
ties on completeness and date, so the source-id tiebreak a full rebuild uses and the `listing_id`
tiebreak the script uses are never reached, and both keep the same rows.

**Same address, different parcels, different sales: kept (66 rows at 16 addresses).** 60 rows are
separate condo and apartment units in 13 State College buildings, with no unit number in the
source. 456 E Beaver Ave is ten separate units, each with its own parcel number. The other six
rows are three pairs, in Chapel Hill, Charlottesville and Gainesville, each a home built in 2023 or
2024 with two different sales about a year or more apart, at different prices, under two parcel
numbers. The source does not show whether a pair is one home sold twice or two homes given one
address. All 66 rows are kept.

35,822 - 38 - 87 = **35,697 rows** after deduplication.

Two pairs disagree on location as well as detail: the two copies of 3249 Cliffstone Blvd are 3.6
miles apart, and those of 4017 Marie Curie Ct 8.1 miles apart, both in Charlottesville. The
build keeps the more complete copy and does not try to tell which location is right.

Rules that need matching living areas, or a date on every copy, miss most of these pairs: an
early draft that used them caught 8 of the 38 and counted the other 30 as condo units.

## 7. City floor

The collection reached into towns surrounding each campus, leaving a long tail: 57 places with
between 1 and 39 sales each, together 255 rows. They were too thin to analyse and carried most of
the dataset's bad city labels, including "Denver, PA" for a property in North Carolina and
"Blackshear" for one inside Athens. Cities with fewer than 90 sales were dropped
(`--min-city-rows`, 0 keeps every city). That leaves 18 cities, the smallest Pittsboro NC with 92.
All 103 two-parcel addresses are in the 18 cities that remain (the first build's output
held all 240 of their rows), so the two-parcel step removes nothing from a dropped place and the
floor still removes 255 rows.

35,697 - 255 = **35,442 rows**.

## 8. Derived columns

**`university` and `miles_to_campus`.** Each row is assigned the nearest of the 11 campuses by
great-circle distance from its own coordinates to one landmark per campus. Coordinates were
checked against the sources below on 2026-10-02. Where no landmark-level source was reachable,
the university's reference point is used; those sit within 0.1 mile of the historic core, which
is the rounding precision of `miles_to_campus`.

| University | Landmark | Coordinates | Source | Rows |
|---|---|---|---|---:|
| University of Wisconsin-Madison | Bascom Hill | 43.0753, -89.4041 | latitude.to | 5,706 |
| University of Florida | Century Tower | 29.648834, -82.34329 | Wikipedia | 5,629 |
| Purdue University | Engineering Fountain | 40.42864, -86.91378 | Wikipedia | 4,616 |
| University of Illinois Urbana-Champaign | Foellinger Auditorium, Main Quad | 40.1059, -88.2272 | Wikipedia | 3,664 |
| University of Michigan | The Diag | 42.2767, -83.7387 | latitude.to | 3,021 |
| The University of North Carolina at Chapel Hill | Old Well | 35.912056, -79.051250 | Wikipedia | 3,016 |
| University of Georgia | North Campus (university reference point) | 33.9558, -83.3745 | latitude.to | 2,814 |
| University of Virginia | Central Grounds (university reference point) | 38.0350, -78.5050 | latitude.to | 2,775 |
| The University of Iowa | Old Capitol | 41.661333, -91.535639 | Wikipedia | 1,909 |
| The Pennsylvania State University | Old Main (university reference point) | 40.7960, -77.8627 | latitude.to | 1,351 |
| University of California, Davis | Shields Library, on the Quad | 38.53972, -121.74917 | Wikipedia | 941 |

Every row falls within 15.1 miles of its campus, with a median of
3.4. Distance is straight-line, rounded to 0.1 mile. Assignment uses coordinates rather than the
city label because a few source rows carry a city or ZIP from elsewhere entirely.

**`listing_id`.** A deterministic 12-character hex id, the first 48 bits of a SHA-256 hash of:

```
normalized_street | normalized_city | normalized_state | zip5 | sale_date | sale_price | parcel_number
```

Normalization is uppercase, trimmed, internal whitespace collapsed. A missing sale date, price or
parcel number contributes an empty string. At 35,442 rows, 48 bits gives roughly a
2-in-a-million chance of any collision; the build asserts uniqueness and stops rather than
shipping a colliding key. The id is stable across rebuilds but tied to the recipe, and it is not
an anonymizer: anyone with the address and sale price can recompute it, which is acceptable
because the address is in the file.

## 9. Output formats

All formats carry identical values. Type handling differs where the format demands it:

| | CSV | SQLite | Excel | DuckDB | Parquet |
|---|---|---|---|---|---|
| `list_date`, `contract_date`, `sale_date` | ISO text | TEXT | real date | DATE | date32 |
| integers and flags (`has_*`) | digits, 0 / 1 | INTEGER | numbers | BIGINT | int64 |
| `zipcode`, `county_fips`, `parcel_number` | text, leading zeros kept | TEXT | text cells | VARCHAR | string |
| missing values | empty | NULL | empty cell | NULL | null |

Flags are 0/1 because SQLite has no boolean type, and 0/1 behaves identically in pandas, SQL and
JavaScript. Dates are ISO text inside the build; every writer that produces a typed date column
converts them explicitly, so no format ends up with a string or timestamp column by accident.

The SQLite and DuckDB files contain exactly one table, `home_sales`, primary key `listing_id`,
with the same seven indexes: `(city, state)`, `university`, `zipcode`, `sale_date`,
`sale_price`, `parcel_number` and `(address_street, city, state)`. `make_parquet.py` imports the
schema and the writers from `build_dataset.py`, so files it makes are identical in structure to
a full rebuild's.

The Excel file has a `home_sales` sheet with a frozen header row and autofilter, plus a
`columns` sheet listing every column with its type, fill rate and a note. Its internal
timestamps are pinned to 2026-03-26 so that rebuilds are byte-identical.

## 10. Verification performed

| Check | Result |
|---|---|
| Event extract against the database | md5 of the full 284,955-row history matches the database's own computation |
| Sale dates and prices against the database | Checksum over all 35,816 properties matches an independent SQL computation |
| Date rule | Nine worked examples pass on every build; zero ordering violations; median time to close 31 days |
| Determinism | Two consecutive builds produce byte-identical CSV, SQLite and Excel files. Writing the corrected CSV again with the build's writers reproduces the published CSV, SQLite and Excel files byte for byte |
| `listing_id` | 35,442 unique, all matching `[0-9a-f]{12}` |
| SQLite storage classes | Integers stored as INTEGER (an early build stored numpy integers as BLOBs, which broke every aggregate), reals as REAL, dates and text as TEXT |
| Excel readback | Header matches the CSV; all three date columns are real dates |
| Deduplication | 456 E Beaver Ave keeps all ten units; every repeated address now has distinct parcel numbers; Barbaro Ave keeps the later sale; no address with exactly two rows holds one sale twice, and `drop_double_records.py` run on the published CSV removes nothing |
| Parquet and DuckDB | `make_parquet.py` reads both back and compares every value, every type, the primary key and the indexes with the CSV, and refuses a CSV whose columns do not match the build |

## 11. Known issues, deliberately left in the data

These are real characteristics of the source, kept because noticing them is part of the teaching
value. The data description sheet explains them for learners.

- **Days on market is computable on 79.1% of rows, and the blanks are not random.** 38% of
  Pittsboro sales have no list date, against 5% of Lafayette's; new construction and off-market
  sales are over-represented among them.
- **Implausible prices.** 40 rows below $10,000 (4 below $1,000, including one at $0) and 31
  above $5,000,000, up to $81,510,000.
- **`home_type` is unreliable.** 35,263 rows say `SINGLE_FAMILY`, including the State College
  condo units; 177 say `HOME_TYPE_UNKNOWN`; 2 say `CONDO`.
- **Repeated addresses with no unit number**: 66 rows at 16 addresses, 60 of them units in 13
  State College buildings (section 6).
- **Placeholder parcel numbers.** `parcel_number` is `0` on 67 rows, and on some rows it is a lot
  or homesite number rather than the county's parcel number (section 6).
- **`school_district`** is populated on 47.9% of rows and not standardized.
- **`architectural_style` and `roof_type` are free text**, 62.0% and 60.2% populated.
- **`tax_assessed_value` is an assessment, not a sale price**, and the two differ widely.
- **Impossible values**: `living_area_sqft` is 0 on 127 rows; lot sizes reach 1,435,737,600 sq
  ft, with 274 lots over 10 acres; one home reports 60 bathrooms; one annual tax bill is exactly
  $1,000,000,000.
- **6 rows have no dates at all**, because the source holds no history for them.

## 12. Parquet and DuckDB

`build_dataset.py` writes both when `pyarrow` and `duckdb` are installed. Where they are not, run
this on any machine that has them:

```bash
pip install pyarrow duckdb
python build/make_parquet.py
```

It converts the published CSV rather than rebuilding, so the values cannot drift, and it exits
with an error if any value, type, key or index differs from the CSV.

## 13. Note on the raw files

`raw_extract.csv` and `raw_events.csv` are the unmodified query results. Both contain
`property_id`, the source platform's identifier, which is excluded from every published file.
Keep them as build artifacts and do not include them in a public release.

## 14. Reproducing this build

```bash
# 1. Run both queries in build/extract_query.sql against the source database and export each
#    as CSV with a header row, to build/raw_extract.csv and build/raw_events.csv.
#    (psql:  \copy (<query>) TO 'raw_extract.csv' CSV HEADER)

# 2. Build, from the package root
pip install pandas openpyxl duckdb pyarrow
python build/build_dataset.py
python build/reference_figures.py
```

The build prints a row count after every step and the reasons behind every blank date, so any
change in the source shows up as a changed count rather than a silent difference.

Without the raw files, the section 6 two-parcel step can be applied to a published CSV that
lacks it, which is how the current files were made:

```bash
pip install pandas openpyxl pyarrow duckdb
python build/drop_double_records.py
python build/reference_figures.py
```

It rewrites all five files in `data/`, checks the Parquet and DuckDB files against the new CSV
value by value, and on files that already have the step it removes nothing.
