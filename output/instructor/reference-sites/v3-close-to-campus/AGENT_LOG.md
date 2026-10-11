# Agent log

This log records how this site was actually built with an AI coding agent, as a model of the log the case asks students to keep.

## 2026-10-09: Choose the question and the user

- **Asked:** "Profile the data with the description sheet in mind. Suggest a question that matters to a specific user and that the data can answer clearly."
- **Chosen:** newly hired faculty deciding where to buy. Their question: "On a new faculty budget, where can you buy a home close to campus?" It uses the columns the data is strongest on (price, distance to campus, size, dates) and avoids `home_type`.
- **Decided:** use only the most recent 12 months of sales, because a buyer cares about current prices. We checked first that this doesn't hide a big shift: quarterly median prices stayed between about $380,000 and $435,000 across all three years. With 12 months, every campus area still has 315 or more sales within 3 miles.

## 2026-10-09: Prepare the data

- **Asked:** "Write `scripts/build_data.py` to keep the sales from those 12 months, leave out sales under $10,000, and save only the columns the site needs to `data/sales.json`."
- **Agent produced:** the script and a 492 KB JSON file with 12,254 sales.
- **Checked:** 12,273 sales fall in the window, and 19 are under $10,000 (12,273 - 19 = 12,254).

## 2026-10-09: Build the page

- **Asked:** "Build it in plain HTML, CSS and JavaScript:
    - The question and user at the top
    - A campus picker, a budget slider and distance buttons
    - Three headline numbers
    - A map of the sales around the campus landmark, without a map service
    - A bar chart comparing all campuses
    - A table and data notes"
- **Agent produced:** the page. The map places each sale from its latitude and longitude around the landmark, with a ring at the chosen distance.
- **Checked:** what happens with very few sales. At UC Davis with a $400,000 budget, only 8 of 315 homes within 3 miles fit, so the size and speed figures correctly show "Too few sales" instead of a misleading median. Penn State at $150,000 within 10 miles (5 homes) does the same.

## 2026-10-09: A data note that was wrong

- **Caught:** the data notes said one of the excluded sales sold for $0. We checked the 12-month window, and the $0 sale is from earlier in the data; the lowest price in the window is $100. We fixed the note. Lesson: a fact from the description sheet about the whole dataset isn't automatically true of a subset.

## 2026-10-09: Test on a phone and in dark mode

- **Asked:** "Test at 375 and 1280 pixels wide, in light and dark mode, served from a subfolder. Click a bar, change every control, hover the map, and report console errors."
- **Found and fixed:** the "Who it's for" label wrapped onto two lines beside the text on desktop. It is now a normal sentence.
- **Result:** no console errors and no sideways scrolling. Clicking a bar switches the campus, and the map tooltip shows price, size, bedrooms and distance.

## 2026-10-09: Check three numbers a second way

- **Asked:** "Recompute the three default headline numbers with SQL in DuckDB, without using the site's JavaScript."
- **Result:** 636 of 685 (93%), 1,400 sq ft and 7 days all match. See the README.

## 2026-10-11: Follow the setup guide's layout

- **Asked:** "Keep the data the way the setup guide says: the CSV in `data/` and the description sheet in `docs/`. Make `scripts/build_data.py` read the CSV, with ZIP, FIPS and parcel numbers as text."
- **Agent produced:** the updated script. It also sorts the sales by campus, distance and `listing_id`, so the file comes out the same every time.
- **Checked:** the rebuilt `data/sales.json` has the same 12,254 sales, and the three default headline numbers are unchanged.

## 2026-10-11: Numbers typed into the page

- **Caught:** the introduction and the data notes had numbers typed in by hand: 12,254 sales, 19 left out, a lowest price of $100, and quarterly medians of "about $380,000 and $435,000". They would go stale the moment the data changed.
- **Asked:** "Compute every number the notes quote in the script, and fill them in from `data/sales.json`."
- **Result:** no number in `index.html` is typed by hand now. The quarterly range is exact: $379,900 to $435,000 across the 11 full calendar quarters.

## 2026-10-11: Repeated addresses that look like one sale recorded twice

- **Asked:** "Our notes say condo units that share an address are separate homes. Check that in our 12 months."
- **Agent produced:** a count of pairs at one address with prices within 1% and sale dates within 90 days, the test the dataset's build notes use for one sale recorded twice. There are 24 such pairs, and 22 are new homes around Virginia. In 22 of the 24, one row has the listing dates and the other has the county's parcel number and assessed value.
- **Decided:** they are under 0.4% of the sales we use and barely move any figure, so we keep them. But we no longer claim every repeated address is a separate home; the data notes now say what we found.

## 2026-10-11: Fonts, and a final test

- **Found:** the page loaded its two fonts from a font service, so it depended on another site staying up. We saved the fonts, with their licenses, in `fonts/`.
- **Asked:** "Test again at 375 and 1280 pixels, light and dark, served from a subfolder. Try five combinations of campus, budget and distance, and compare the three headline numbers with a separate calculation from the full dataset."
- **Result:** no console errors, no sideways scrolling, every control works, and all five settings match.
