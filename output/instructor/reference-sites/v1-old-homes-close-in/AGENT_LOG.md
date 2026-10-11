# Agent log

This log records how this site was actually built with an AI coding agent, as a model of the log the case asks students to keep.

## 2026-10-11: Find a topic in the data

- **Asked:** "Read the data description sheet, then profile the data. I want a topic that isn't just prices or days on market. Show me a few patterns by distance from campus."
- **Agent produced:** several candidates. The clearest was the age of the housing: the median home sold within a mile of campus was built in 1939, against 2002 at 5 to 10 miles out. Price per square foot by decade built also had a shape worth showing: highest for 1920s and 1930s homes, lowest for the 1960s and 1970s, and rising again for new homes.
- **Decided:** a short data story, "Old Homes, Close In", with the findings at the top and a campus picker so readers can check their own town.

## 2026-10-11: Odd values in year_built

- **Asked:** "Before we use `year_built`, show me how many homes there are for each year from 1900 to 1910, and anything else odd in the column."
- **Agent produced:** 192 homes recorded as built in exactly 1900 and 119 in 1901, against about 25 a year from 1902 to 1909. One sale has no year built, and 46 homes have a year built later than the year they sold.
- **Decided:**
    - The 1900 and 1901 spikes look like a default for "very old, year unknown". We keep them, since they are old homes either way, and say so beside the decade chart.
    - A home built after its sale year was sold before it was finished, so it counts as a new home.
    - The sale with no year built is left out of the year figures.

## 2026-10-11: Prepare the data

- **Asked:** "Write `scripts/build_data.py` to compute every figure the page needs into `data/age.json`: median year built by distance band, median price per square foot by decade built, and the share of new homes, for all areas and for each campus area. Use the case's distance bands, the $1,000 price floor and the 100 sq ft floor for price per square foot, and hide any median based on fewer than 20 sales."
- **Agent produced:** the script and a JSON file of about 18 KB, so the page never loads the full CSV.
- **Checked:** the file against a second calculation written separately. Every value matched.

## 2026-10-11: Virginia's new homes are counted twice (caught by checking a surprising number)

- **Caught:** Virginia's share of new homes, 21.7%, was twice that of most areas. We asked the agent to look at Virginia's new homes that share a street address.
- **Found:** 78 pairs of new-home sales at one address have prices within 1% and sale dates within 90 days, the test the dataset's build notes use for one sale recorded twice. In most pairs, one row has the listing dates and the other has the county's parcel number and assessed value.
- **Decided:** keep every row, because the case says never to remove a sale just because its address repeats, but show Virginia's share both ways: 21.7% as recorded, and 19.5% with one copy of each pair. Virginia is still the highest.

## 2026-10-11: Build the page

- **Asked:** "Build the page in plain HTML, CSS and JavaScript, with no libraries:
    - Three findings in words at the top
    - A campus picker that drives three headline numbers and the first two charts
    - Year built by distance band, price per square foot by decade, new homes by campus area
    - A table of all areas, and data notes"
- **Agent produced:** the page. Years are shown as dots on a scale that starts near 1900, because a bar for a year would have to start at zero. Dollars are shown as bars from zero.
- **Caught:** the agent's first draft of the findings said the near-campus pattern "holds in every campus area". Nobody had checked that. We asked it to compute the claim instead. The sentence now fills in the count from the data: in 11 of the 11 areas, the homes within a mile of campus are the oldest of any distance band.

## 2026-10-11: Test on a phone and in dark mode

- **Asked:** "Test at 375 and 1280 pixels wide, in light and dark mode, served from a subfolder. Use every option in the picker, pick an area from the bar chart with the keyboard, and report console errors."
- **Found and fixed:**
    - On a phone, the page scrolled sideways by 47 pixels. The campus picker had sized itself to its longest name, "The University of North Carolina at Chapel Hill". It now fits the screen.
    - The decade chart labeled both 1900 and 2000 as "'00". The first decade of each century now shows the full year.
- **Result:** no console errors and no sideways scrolling, and every picker option changes the numbers.

## 2026-10-11: Check three numbers a second way

- **Asked:** "Recompute three headline numbers with SQL in DuckDB, straight from the CSV, without using `build_data.py`."
- **Result:** 1939, $272 and 8.2% all match. See the README.
