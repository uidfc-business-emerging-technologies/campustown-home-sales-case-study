# Reference figures (instructor copy)

Dataset: 35,442 rows, 18 cities in 11 states, 11 campuses.

These are the numbers a correct site should show. They are not the only defensible answers:
a learner who states a different rule and applies it consistently is right too. What
matters is that the figure on the site matches the rule the learner says they used.

**Rules used here**

- Price figures exclude sales under $1,000. There are 4 such rows, including sales of $0. Row counts include them.
- Price per square foot excludes living areas under 100 sq ft, is computed row by row, and then a median is taken. Dividing a median price by a median area gives a different, wrong answer.
- Median, not mean, for prices. The highest sale in the dataset is $81,510,000.
- Days on market is `contract_date - list_date`, computed only on rows that have both (28,042 rows). Using `sale_date - list_date` instead adds the time to close, which has a median of 31 days.

## By city

| City | Rows | Median price | Mean price | Median $/sqft | Median sqft | Median year built | Median days on market | Rows sharing an address |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Gainesville, FL | 5,477 | $350,000 | $403,359 | $203.44 | 1,734 | 1987 | 25 | 2 |
| Madison, WI | 5,061 | $421,000 | $477,144 | $248.07 | 1,737 | 1965 | 7 | 0 |
| Lafayette, IN | 3,057 | $260,000 | $282,797 | $163.01 | 1,649 | 1979 | 9 | 0 |
| Ann Arbor, MI | 3,021 | $571,000 | $657,210 | $259.11 | 2,222 | 1966 | 7 | 0 |
| Athens, GA | 2,814 | $370,000 | $491,552 | $196.82 | 1,862 | 1992 | 27 | 0 |
| Charlottesville, VA | 2,775 | $615,000 | $795,448 | $270.03 | 2,388 | 1990 | 7 | 2 |
| Chapel Hill, NC | 2,716 | $735,000 | $837,117 | $276.87 | 2,679 | 1997 | 10 | 2 |
| Champaign, IL | 2,286 | $240,000 | $277,276 | $149.68 | 1,644 | 1968 | 7 | 0 |
| Iowa City, IA | 1,909 | $342,000 | $389,734 | $175.91 | 2,034 | 1976 | 24 | 0 |
| West Lafayette, IN | 1,559 | $379,900 | $416,652 | $178.28 | 2,194 | 2002 | 11 | 0 |
| State College, PA | 1,351 | $430,000 | $473,855 | $207.42 | 2,123 | 1982 | 8 | 60 |
| Urbana, IL | 1,131 | $229,900 | $246,549 | $144.35 | 1,550 | 1966 | 8 | 0 |
| Davis, CA | 941 | $889,000 | $976,896 | $492.71 | 1,842 | 1978 | 11 | 0 |
| Middleton, WI | 645 | $611,000 | $709,295 | $256.26 | 2,497 | 2000 | 8 | 0 |
| Savoy, IL | 247 | $402,700 | $420,053 | $186.74 | 2,151 | 2010 | 10 | 0 |
| Carrboro, NC | 208 | $601,250 | $612,495 | $315.38 | 1,780 | 1984 | 7 | 0 |
| Newberry, FL | 152 | $439,995 | $497,060 | $184.70 | 2,662 | 2023 | 87 | 0 |
| Pittsboro, NC | 92 | $876,986 | $954,457 | $301.87 | 2,970 | 2015 | 38 | 0 |

## By campus

Campus is assigned from each property's coordinates, not its city label. Rows are all rows;
prices follow the rules above.

| University | Rows | Median price | Median $/sqft | Median days on market | Median miles to campus |
|---|---:|---:|---:|---:|---:|
| University of Wisconsin-Madison | 5,706 | $434,010 | $249.16 | 7 | 4.8 |
| University of Florida | 5,629 | $355,000 | $203.24 | 25 | 4.4 |
| Purdue University | 4,616 | $299,900 | $168.24 | 10 | 3.8 |
| University of Illinois Urbana-Champaign | 3,664 | $245,000 | $150.30 | 7 | 2.8 |
| University of Michigan | 3,021 | $571,000 | $259.11 | 7 | 2.7 |
| The University of North Carolina at Chapel Hill | 3,016 | $725,000 | $280.25 | 10 | 3.8 |
| University of Georgia | 2,814 | $370,000 | $196.82 | 27 | 3.7 |
| University of Virginia | 2,775 | $615,000 | $270.03 | 7 | 3.4 |
| The University of Iowa | 1,909 | $342,000 | $175.91 | 24 | 2.2 |
| The Pennsylvania State University | 1,351 | $430,000 | $207.42 | 8 | 2.1 |
| University of California, Davis | 941 | $889,000 | $492.71 | 11 | 2.0 |

## Whole dataset

| Figure | Value |
|---|---:|
| Rows | 35,442 |
| Columns | 34 |
| Cities / states / counties | 18 / 11 / 20 |
| Median sale price | $410,000 |
| Sale dates | 2023-03-27 to 2026-03-25 |
| Rows with a sale date | 35,436 |
| Rows with a list date | 29,262 (82.6%) |
| Rows with a contract date | 28,914 (81.6%) |
| Rows with both (days on market computable) | 28,042 (79.1%) |
| Median days on market | 11 |
| Median contract to close | 31 days |
| Median list to close | 50 days |
| Rows sharing a street address | 66 |
| Largest building | 10 sales at one address |

## Four things to check on a learner's site

1. **Does the city total match?** If it is short by a few rows, they probably deduplicated by address and deleted condo units.
2. **Does the median look like the table above?** One far too high usually means a mean was computed instead, or the $0 sales were left in a min/max display.
3. **Does price per square foot look plausible?** A figure in the thousands means the zero-square-foot rows were divided by.
4. **Is days on market about a month too long?** Then they subtracted `list_date` from `sale_date`, which includes the time to close. If it is close to zero for many homes, they may have treated blanks as zero.
