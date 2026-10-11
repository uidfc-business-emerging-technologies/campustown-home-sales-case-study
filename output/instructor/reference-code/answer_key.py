"""Build the Variation 2 answer key from the reference figures.

Writes, from one set of computed values:
- the Excel workbook (output/instructor/Variation 2 Answer Key.xlsx)
- one chart per question (output/source/word-documents/charts/)
- the markdown source of the Word answer key, which build.js turns into a .docx
- data/answers.json for the Variation 2 reference site

Every number in these files comes from the functions below. None is typed by hand.
"""

import json
import re
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from openpyxl import Workbook  # noqa: E402
from openpyxl.drawing.image import Image as XLImage  # noqa: E402
from openpyxl.styles import Alignment, Font, PatternFill  # noqa: E402
from openpyxl.utils import get_column_letter  # noqa: E402

import variation2 as v2  # noqa: E402
import wrong_answers  # noqa: E402
from definitions import REPO_ROOT, half_up  # noqa: E402

OUTPUT = REPO_ROOT / "output"
WORKBOOK = OUTPUT / "instructor" / "Variation 2 Answer Key.xlsx"
WORD_SOURCES = OUTPUT / "source" / "word-documents"
MARKDOWN = WORD_SOURCES / "variation2_answer_key.md"
CHARTS = WORD_SOURCES / "charts"
CONTENT_JS = OUTPUT / "source" / "case-documents" / "content.js"
SMALL = "fewer than 20 sales"
FIXED_TIME = datetime(2026, 10, 11)

BLUE, ORANGE, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3df"
SHORT = v2.SHORT_NAMES


# ---- formatting ---------------------------------------------------------------
def trim(x):
    text = f"{x:,.2f}".rstrip("0").rstrip(".")
    return text


FORMATS = {
    # kind: (markdown text, Excel value, Excel number format)
    "text": (lambda v: str(v), lambda v: v, "General"),
    "int": (lambda v: f"{int(v):,}", lambda v: int(v), "#,##0"),
    "money": (lambda v: f"${half_up(v):,}", lambda v: half_up(v), "$#,##0"),
    "money2": (lambda v: f"${half_up(v, 2):,.2f}", lambda v: half_up(v, 2), "$#,##0.00"),
    "days": (lambda v: trim(half_up(v, 1)), lambda v: half_up(v, 1), "General"),
    "pct": (lambda v: f"{half_up(100 * v, 1):.1f}%", lambda v: half_up(v, 3), "0.0%"),
    "ratio": (lambda v: f"{half_up(v, 2):.2f}", lambda v: half_up(v, 2), "0.00"),
    "miles": (lambda v: trim(half_up(v, 2)), lambda v: half_up(v, 2), "General"),
}


def is_missing(v):
    try:
        return v is None or v != v
    except TypeError:
        return False


def fmt(v, kind):
    if isinstance(v, str):
        return v
    if is_missing(v):
        return "none"
    return FORMATS[kind][0](v)


class Table:
    """A table both the workbook and the markdown are written from."""

    def __init__(self, title, columns, rows, note=None):
        self.title, self.columns, self.rows, self.note = title, columns, rows, note

    def markdown(self):
        head = "| " + " | ".join(h for h, _ in self.columns) + " |"
        align = "|" + "|".join("---" if k == "text" else "---:" for _, k in self.columns) + "|"
        body = ["| " + " | ".join(fmt(v, k) for v, (_, k) in zip(r, self.columns)) + " |" for r in self.rows]
        return "\n".join([head, align, *body])


# ---- the questions as the case states them --------------------------------------
def question_texts():
    source = CONTENT_JS.read_text()
    block = source.split('{ t: "h2", text: "Questions" }')[1].split("] },")[0]
    items = re.findall(r'^\s*"(.*)",\s*$', block, re.M)
    return [i.replace('\\"', '"').replace("[[", "`").replace("]]", "`") for i in items]


# ---- per-question content -----------------------------------------------------
def q1(df):
    t = v2.q1_price_levels(df)
    sizes = df[df["price_per_sqft"].notna()].groupby("university")["living_area_sqft"].median()
    top, bottom = t.index[0], t.index[-1]
    moved = t[t["rank by price"] != t["rank by price per sq ft"]]
    figures = Table("Price levels by campus area", [
        ("Campus area", "text"), ("Valid sales", "int"), ("Median sale price", "money"), ("Rank", "int"),
        ("Sales with price per sq ft", "int"), ("Median price per sq ft", "money2"), ("Rank", "int"),
    ], [[u, r["valid sales"], r["median sale price"], r["rank by price"], r["sales with price per sq ft"],
         r["median price per sq ft"], r["rank by price per sq ft"]] for u, r in t.iterrows()])

    swap = " and ".join(SHORT[u] for u in moved.index)
    a, b = moved.index[0], moved.index[1]
    hi_price, lo_price = (a, b) if t.loc[a, "median sale price"] > t.loc[b, "median sale price"] else (b, a)
    answer = [
        f"{SHORT[top]} is highest on both measures, with a median sale price of {fmt(t.loc[top, 'median sale price'], 'money')} "
        f"and {fmt(t.loc[top, 'median price per sq ft'], 'money2')} per square foot. {SHORT[bottom]} is lowest on both, at "
        f"{fmt(t.loc[bottom, 'median sale price'], 'money')} and {fmt(t.loc[bottom, 'median price per sq ft'], 'money2')}.",
        f"The ranking barely changes. Only {swap} trade places, at {int(t.loc[hi_price, 'rank by price'])} and "
        f"{int(t.loc[lo_price, 'rank by price'])}. {SHORT[hi_price]} homes sell for more "
        f"({fmt(t.loc[hi_price, 'median sale price'], 'money')} against {fmt(t.loc[lo_price, 'median sale price'], 'money')}), "
        f"but they are larger (median {fmt(sizes[hi_price], 'int')} sq ft against {fmt(sizes[lo_price], 'int')}), "
        f"so they cost less per square foot. Price per square foot adjusts for size; median price does not.",
    ]
    wa = wrong_answers.q1(df)
    wrong = [
        ("Mean instead of median", f"Means are pulled up by a few very expensive sales, up to "
         f"{fmt(df['sale_price'].max(), 'money')}.",
         area_table(wa["Median sale price"], "money")),
        ("Ratio of medians, mean of ratios, or blank areas divided", "Price per square foot is a median of "
         "per-sale values. Dividing the median price by the median area, averaging, or letting a blank or 0 sq ft "
         "area divide (JavaScript returns Infinity) each gives a different figure.",
         area_table(wa["Median price per sq ft"], "money2")),
    ]
    tolerance = [
        "Median sale price: within $1,000 of the key. Rounding to the nearest thousand is fine.",
        "Median price per sq ft: within $1.00.",
        f"Ranking: the site must name {SHORT[top]} highest and {SHORT[bottom]} lowest on both measures, and notice that "
        f"{swap} swap. Any reason based on home size earns full credit.",
    ]
    chart = chart_q1(t, f"Two bar charts, one per measure, ordered by median sale price. {SHORT[top]} is highest and "
                     f"{SHORT[bottom]} lowest on both; only {swap} change places.")
    site = [{"campus": SHORT[u], "valid_sales": int(r["valid sales"]), "median_price": half_up(r["median sale price"]),
             "pps_sales": int(r["sales with price per sq ft"]), "median_pps": half_up(r["median price per sq ft"], 2),
             "median_sqft": half_up(sizes[u]), "rank_price": int(r["rank by price"]),
             "rank_pps": int(r["rank by price per sq ft"])} for u, r in t.iterrows()]
    return dict(figures=[figures], chart=chart, answer=answer, wrong=wrong, tolerance=tolerance, site=site)


def q2(df):
    t = v2.q2_speed(df)
    fastest = t["median days on market"].min()
    tied = [SHORT[u] for u in t.index[t["median days on market"] == fastest]]
    slow = t.sort_values("median days on market", ascending=False).head(3)
    share = t["share missing days on market"]
    figures = Table("Days on market by campus area", [
        ("Campus area", "text"), ("Sales", "int"), ("Sales with days on market", "int"),
        ("Median days on market", "days"), ("Share with no days on market", "pct"),
    ], [[u, r["sales"], r["sales with days on market"], r["median days on market"], r["share missing days on market"]]
        for u, r in t.iterrows()])
    answer = [
        f"{count_word(len(tied))} areas tie as the fastest, at a median of {fmt(fastest, 'days')} days: {join(sorted(tied))}. "
        f"The slowest are " + join([f"{SHORT[u]} ({fmt(r['median days on market'], 'days')})" for u, r in slow.iterrows()]) + ".",
        f"Between {fmt(share.min(), 'pct')} ({SHORT[share.idxmin()]}) and {fmt(share.max(), 'pct')} "
        f"({SHORT[share.idxmax()]}) of sales have no days on market. Those sales are mostly off-market and new "
        f"construction sales, so they are not a random sample. The medians describe only homes that were listed, "
        f"and areas with a large missing share, such as {SHORT[share.idxmax()]} and "
        f"{SHORT[share.drop(share.idxmax()).idxmax()]}, are the least comparable.",
    ]
    wa = wrong_answers.q2(df)
    wrong = [
        ("Measured to sale_date, blanks as zero, or a mean", "Days on market ends at `contract_date`. Using "
         "`sale_date` adds the time to close. Treating a blank date as 0 makes unlisted homes look instant. A mean "
         "is pulled up by homes that took over a year.", area_table(wa["Median days on market"], "days")),
        ("Missing share counts only list_date", "A sale needs both dates. Counting only a missing `list_date` "
         "misses sales with a list date but no contract date.", area_table(wa["Share missing days on market"], "pct")),
    ]
    tolerance = [
        "Median days on market: within 0.5 days. For Iowa, 23.5 and 24 are both correct.",
        "Share with no days on market: within 0.5 percentage points.",
        "The comment on the missing share should say the missing sales are not random, or that the comparison covers "
        "listed homes only.",
    ]
    chart = chart_q2(t)
    site = [{"campus": SHORT[u], "rows": int(r["sales"]), "dom_sales": int(r["sales with days on market"]),
             "median_dom": float(half_up(r["median days on market"], 1)),
             "missing_share": half_up(r["share missing days on market"], 4)} for u, r in t.iterrows()]
    return dict(figures=[figures], chart=chart, answer=answer, wrong=wrong, tolerance=tolerance, site=site)


def q3(df):
    counts, medians, shown = v2.q3_distance(df)
    order = list(SHORT)
    pattern = v2.q3_pattern(shown)
    columns = [("Campus area", "text")] + [(b, "money2") for b in v2.BAND_LABELS]

    def cell(u, b):
        n = counts.loc[u, b]
        if n == 0:
            return "no sales"
        return SMALL if n < v2.MIN_GROUP else medians.loc[u, b]

    figures = [
        Table("Median price per sq ft by distance band", columns, [[u] + [cell(u, b) for b in v2.BAND_LABELS] for u in order]),
        Table("Sales in each cell", [("Campus area", "text")] + [(b, "int") for b in v2.BAND_LABELS],
              [[u] + [counts.loc[u, b] for b in v2.BAND_LABELS] for u in order]),
        Table("Pattern by area", [("Campus area", "text"), ("Pattern", "text"), ("Highest band", "text"),
                                  ("Largest rise between neighboring bands", "pct")],
              [[u, r["pattern"], r["highest band"], max(r["largest rise between neighboring bands"], 0)]
               for u, r in pattern.loc[order].iterrows()],
              note="A rise of 0.0% means price per square foot never rises from one band to the next."),
    ]
    every = [SHORT[u] for u in pattern.index[pattern["pattern"] == "falls at every step"]]
    overall = [SHORT[u] for u in pattern.index[pattern["pattern"] == "falls overall"]]
    nofall = pattern[pattern["pattern"] == "does not fall"]
    falls = len(every) + len(overall)
    worst = nofall["largest rise between neighboring bands"].idxmax()
    answer = [
        f"Yes, in most areas. Price per square foot is highest within 1 mile of campus in "
        f"{int((pattern['highest band'] == v2.BAND_LABELS[0]).sum())} of 11 areas, and it falls with distance in {falls}: "
        f"at every step in {join(sorted(every))}, and overall, with no rise between neighboring bands above "
        f"{fmt(v2.MAX_RISE, 'pct')}, in {join(sorted(overall))}.",
        f"It does not fall in {join(sorted(SHORT[u] for u in nofall.index))}. {SHORT[worst]} is the clearest exception: "
        f"its highest band is {pattern.loc[worst, 'highest band'].lower()} "
        f"({fmt(shown.loc[worst, pattern.loc[worst, 'highest band']], 'money2')}, against "
        f"{fmt(shown.loc[worst, v2.BAND_LABELS[0]], 'money2')} under 1 mile).",
        f"{count_word(int((counts < v2.MIN_GROUP).sum().sum()))} of the {counts.size} cells have fewer than 20 sales, all "
        f"in the outer bands, and show \"fewer than 20 sales\" or no sales.",
    ]
    wa = wrong_answers.q3(df)
    pooled = wa["All areas pooled, by band"]
    small = wa["Small cells shown instead of suppressed"]
    wrong = [
        ("All areas pooled into one line", "Pooling mixes areas with different price levels. The outer bands are "
         "dominated by a few areas, so the pooled line rises again even though most areas fall.",
         Table("All areas pooled", [("Band", "text"), ("Sales", "int"), ("Median price per sq ft", "money2")],
               [[b, r["sales"], r["median price per sq ft"]] for b, r in pooled.iterrows()])),
        ("Small cells shown", "These medians rest on fewer than 20 sales and must be replaced by \"fewer than 20 sales\".",
         Table("Cells that must not show a figure", [("Campus area", "text"), ("Band", "text"), ("Sales", "int"),
                                                     ("Median shown in error", "money2")],
               [[u, b, r["sales"], r["median that should not be shown"]] for (u, b), r in small.iterrows()])),
    ]
    tolerance = [
        "Each reportable cell: within $1.00.",
        "Every cell with 1 to 19 sales shows \"fewer than 20 sales\". A cell with no sales may show that, a dash or "
        "\"no sales\".",
        f"The answer says yes for most areas and names {SHORT[worst]}. Naming "
        f"{join(sorted(SHORT[u] for u in nofall.index if u != worst))} as well is correct. Naming an area that falls at "
        f"every step ({join(sorted(every))}) is wrong.",
    ]
    chart = chart_q3(shown, pattern, "Eleven small line charts of median price per square foot across the distance "
                     f"bands. The line falls in most areas; it does not fall in {join(sorted(SHORT[u] for u in nofall.index))}, "
                     "drawn in orange.")
    site = {"bands": v2.BAND_LABELS, "rows": [{"campus": SHORT[u], "pattern": pattern.loc[u, "pattern"], "cells": [
        {"n": int(counts.loc[u, b]), "median_pps": None if counts.loc[u, b] < v2.MIN_GROUP else half_up(medians.loc[u, b], 2)}
        for b in v2.BAND_LABELS]} for u in order]}
    return dict(figures=figures, chart=chart, answer=answer, wrong=wrong, tolerance=tolerance, site=site)


def q4(df):
    t = v2.q4_timing(df, window=True)
    med = t["median days on market"]
    fastest = med[med == med.min()].index.tolist()
    slowest = med.idxmax()
    second = med.drop(slowest).idxmax()
    figures = Table(f"Days on market by month listed, {WINDOW_TEXT}",
                    [("Month listed", "text"), ("Listings with days on market", "int"), ("Median days on market", "days")],
                    [[m, r["listings with days on market"], r["median days on market"]] for m, r in t.iterrows()])
    answer = [
        f"Homes listed in {join(fastest)} go under contract fastest, at a median of {fmt(med.min(), 'days')} days. "
        f"{slowest} listings are slowest ({fmt(med.max(), 'days')} days), followed by {second} ({fmt(med[second], 'days')}).",
        "Spring listings sell fastest and late-year listings slowest, the usual pattern of a spring buying season.",
    ]
    wa = wrong_answers.q4(df)["Median days on market by month listed"]
    wrong = [
        ("No window, wrong month or wrong end date", "Listings outside the window are incomplete. Grouping by the "
         "month of `sale_date` describes when homes closed, not when they were listed. Measuring to `sale_date` adds "
         "the time to close. Treating blank dates as 0 pulls every month down.",
         Table("Median days on market by month under each mistake", [("Month", "text")] +
               [(c, "days") for c in wa.columns], [[m] + list(r.values) for m, r in wa.iterrows()])),
    ]
    tolerance = [
        "Each month: within 0.5 days.",
        f"Fastest: {join(fastest)}. Slowest: {slowest}. Naming {second} as the second slowest is good but not required.",
    ]
    chart = chart_q4(t, fastest, slowest)
    site = {"window": list(v2.LISTING_WINDOW), "months": [{"month": i + 1, "name": m, "n": int(r["listings with days on market"]),
            "median_dom": float(half_up(r["median days on market"], 1))} for i, (m, r) in enumerate(t.iterrows())]}
    return dict(figures=[figures], chart=chart, answer=answer, wrong=wrong, tolerance=tolerance, site=site)


def q5(df):
    t = v2.q5_assessment(df)
    ratio = t["median assessed / sale price"]
    far = ratio[ratio.map(lambda r: half_up(r, 2)) < 0.5]
    rest = ratio.drop(far.index)
    figures = Table("Median assessed value / sale price", [
        ("Campus area", "text"), ("State", "text"), ("Sales used", "int"), ("Median ratio", "ratio"),
    ], [[u, r["state"], r["sales used"], r["median assessed / sale price"]] for u, r in t.iterrows()])
    psu, mich = "The Pennsylvania State University", "University of Michigan"
    davis = "University of California, Davis"
    illinois = "University of Illinois Urbana-Champaign"
    answer = [
        f"Two areas are far from 1: {SHORT[psu]} ({fmt(ratio[psu], 'ratio')}) and {SHORT[mich]} "
        f"({fmt(ratio[mich], 'ratio')}). The other {len(rest)} areas run from {fmt(rest.min(), 'ratio')} to "
        f"{fmt(rest.max(), 'ratio')}, with {SHORT[davis]} at {fmt(ratio[davis], 'ratio')}.",
        "**Penn State (Pennsylvania).** Pennsylvania counties assess against a \"base year\" and reassess at irregular "
        "intervals (Babst Calland, 2023). The state measures how far assessments have drifted with a common level "
        "ratio for each county. For Centre County, the July 2026 factor is 6.10, and the factor is the reciprocal of "
        "the ratio, so assessments sit at about one sixth of market value (Pennsylvania Department of Revenue). "
        f"That matches the data's {fmt(ratio[psu], 'ratio')}.",
        "**Michigan.** Michigan's constitution caps assessed value at 50 percent of true cash value. Taxable value can "
        "rise each year only by inflation or 5 percent, whichever is less, until the home sells (Michigan State Tax "
        "Commission). Assessments at half of value would give about 0.5. The data's "
        f"{fmt(ratio[mich], 'ratio')} is lower still, which fits a field holding the capped taxable value, or "
        "assessments that lag rising prices. The dataset does not say which.",
        "**For contrast, UC Davis (California).** California reassesses a home at its purchase price when it changes "
        "hands, and the value can then rise by at most 2 percent a year (California State Board of Equalization). "
        f"A recent sale resets the assessment to about the sale price, so the median ratio is {fmt(ratio[davis], 'ratio')}.",
        f"Do not read a state's statutory assessment level into this column. Illinois, for example, sits at "
        f"{fmt(ratio[illinois], 'ratio')} here. The values are as the collection source reported them.",
        "Sources, checked October 11, 2026:",
    ]
    sources = [
        "[Pennsylvania tax assessment appeals and common level ratios](https://www.babstcalland.com/news-article/pennsylvania-tax-assessment-appeals-and-common-level-ratios-four-observations/) (Babst Calland, October 6, 2023)",
        "[2025 Common Level Ratio Real Estate Valuation Factors](https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/taxtypes/rtt/documents/clr_factor_current.pdf) (Pennsylvania Department of Revenue, July 2026)",
        "[Guide to Basic Assessing](https://www.michigan.gov/-/media/Project/Websites/treasury/Assessors/Guide_to_Basic_Assessing_116.pdf) (Michigan State Tax Commission, May 2018)",
        "[Assessors' Handbook Section 401, Change in Ownership](https://www.boe.ca.gov/proptaxes/pdf/ah401.pdf) (California State Board of Equalization, reprinted January 2015)",
    ]
    wa = wrong_answers.q5(df)["Median assessed value / sale price"]
    wrong = [
        ("Mean, ratio of medians, inverted ratio, or invalid sales kept", "The ratio is computed per sale, then the "
         "median is taken. Including sales under $1,000 divides by tiny prices and wrecks a mean.",
         area_table(wa, "ratio")),
    ]
    tolerance = [
        "Each median ratio: within 0.01.",
        f"Names {SHORT[psu]} and {SHORT[mich]} as far from 1. Naming {SHORT[davis]} as far from 1 is wrong.",
        "The explanation must rest on how each state assesses property, with a source. A claim that homes there "
        "sell far above their value earns no credit.",
    ]
    chart = chart_q5(t, far.index, "Bar chart of the median assessment ratio by campus area. " + join(
        [f"{SHORT[u]} ({fmt(ratio[u], 'ratio')})" for u in far.index]) + f" are far below 1; the rest are between "
        f"{fmt(rest.min(), 'ratio')} and {fmt(rest.max(), 'ratio')}.")
    site = [{"campus": SHORT[u], "state": r["state"], "n": int(r["sales used"]),
             "median_ratio": half_up(r["median assessed / sale price"], 3)} for u, r in t.iterrows()]
    return dict(figures=[figures], chart=chart, answer=answer, sources=sources, wrong=wrong, tolerance=tolerance, site=site)


def q6(df):
    by_area, total = v2.q6_buildings(df)
    miles = ["median miles, sales at those addresses", "median miles, all other sales"]

    def shown(r):
        return r[miles[0]] if r["sales at those addresses"] >= v2.MIN_GROUP else (
            SMALL if r["sales at those addresses"] > 0 else "no sales")

    figures = Table("Addresses with more than one sale", [
        ("Campus area", "text"), ("Addresses", "int"), ("Sales at those addresses", "int"),
        ("Median miles, those sales", "miles"), ("Median miles, all other sales", "miles"),
    ], [[u, r["addresses with more than one sale"], r["sales at those addresses"], shown(r), r[miles[1]]]
        for u, r in by_area.iterrows()] +
        [["All campus areas", total["addresses with more than one sale"], total["sales at those addresses"],
          total[miles[0]], total[miles[1]]]])
    big = by_area[by_area["sales at those addresses"] >= v2.MIN_GROUP]
    none = [SHORT[u] for u in by_area.index[by_area["sales at those addresses"] == 0]]
    va, psu = "University of Virginia", "The Pennsylvania State University"
    groups = v2.shared_address_groups(df)
    doubles = groups[groups["likely one sale recorded twice"]]
    va_doubles = doubles[doubles["university"] == va]
    recent = int(df["sale_date"].min().year)
    split = int(((doubles["rows with a list or contract date"] == 1) & (doubles["rows with an assessed value"] == 1)).sum())
    answer = [
        f"In all, {total['addresses with more than one sale']} addresses have more than one sale, covering "
        f"{total['sales at those addresses']} sales. They are concentrated in two areas: {SHORT[va]} "
        f"({by_area.loc[va, 'addresses with more than one sale']} addresses, {by_area.loc[va, 'sales at those addresses']} sales) "
        f"and {SHORT[psu]} ({by_area.loc[psu, 'addresses with more than one sale']} addresses, "
        f"{by_area.loc[psu, 'sales at those addresses']} sales). {join(none)} have none, and every other area has "
        f"{by_area.drop([va, psu])['addresses with more than one sale'].max()} or fewer such addresses.",
        f"Across all areas, those sales sit a median {fmt(total[miles[0]], 'miles')} miles from campus, against "
        f"{fmt(total[miles[1]], 'miles')} for all other sales. That overall figure mixes two opposite patterns. Around "
        f"{SHORT[psu]}, the repeated addresses are close to campus ({fmt(big.loc[psu, miles[0]], 'miles')} miles against "
        f"{fmt(big.loc[psu, miles[1]], 'miles')}). Around {SHORT[va]}, they are farther out ({fmt(big.loc[va, miles[0]], 'miles')} "
        f"against {fmt(big.loc[va, miles[1]], 'miles')}). The other areas have fewer than 20 such sales.",
    ]
    instructor_note = (
        f"**Instructor note: what the repeated addresses are.** The description sheet calls all {total['sales at those addresses']} "
        f"rows separate condo or apartment units. That holds in State College. But {len(doubles)} of the "
        f"{total['addresses with more than one sale']} addresses ({doubles['sales'].sum()} rows) meet the build notes' own test "
        f"for one sale recorded twice: two rows, prices within 1% and sale dates within 90 days. Of these, {len(va_doubles)} "
        f"are in {SHORT[va]}, and {int((va_doubles['newest year built'] >= recent).sum())} of those are homes built in "
        f"{recent} or later. In {split} of the {len(doubles)} pairs, one row carries the listing dates and the other "
        f"carries the county's parcel number and assessed value, so the build's parcel check missed them. Their coordinates "
        f"differ too, which is why {SHORT[va]}'s repeated-address sales look far from campus. Do not mark down a student who "
        f"spots this and explains it. The figures above follow the question's definition, which counts every row."
    )
    wa = wrong_answers.q6(df)
    totals = wa["Totals under each method"]
    wrong = [
        ("Grouped by street name only, or duplicates removed first", "Grouping by street name alone merges same-named "
         "streets in different towns. Removing duplicate addresses first leaves nothing to count. Counting only the "
         "extra sales (sales minus addresses) understates the total.",
         Table("Totals under each method", [("Method", "text"), ("Addresses", "int"), ("Sales", "int"),
                                            ("Median miles of those sales", "miles")],
               [[m, r["addresses"], r["sales"], r["median miles to campus of those sales"]] for m, r in totals.iterrows()] +
               [["extra sales only", total["addresses with more than one sale"],
                 total["sales at those addresses"] - total["addresses with more than one sale"], total[miles[0]]]])),
    ]
    tolerance = [
        f"Counts: exact. {total['addresses with more than one sale']} addresses and {total['sales at those addresses']} "
        "sales in total, and each area's counts as in the table. For areas with fewer than 20 such sales, showing the "
        "count or \"fewer than 20 sales\" are both correct.",
        "Median miles: within 0.05 miles. In areas with fewer than 20 such sales, the median must show "
        "\"fewer than 20 sales\".",
        "Full credit needs the overall comparison and the observation that it differs by area.",
    ]
    shown_areas = by_area[by_area["sales at those addresses"] >= v2.MIN_GROUP]
    chart = chart_q6(by_area, "Bar chart of sales at repeated addresses by campus area. " + join(
        [f"{SHORT[u]} ({r['sales at those addresses']})" for u, r in shown_areas.iterrows()]) + " hold almost all of them.")
    site = {"rows": [{"campus": SHORT[u], "addresses": int(r["addresses with more than one sale"]),
                      "sales": int(r["sales at those addresses"]),
                      "median_miles_multi": None if r["sales at those addresses"] < v2.MIN_GROUP else half_up(r[miles[0]], 2),
                      "median_miles_other": half_up(r[miles[1]], 2)} for u, r in by_area.iterrows()],
            "total": {"addresses": int(total["addresses with more than one sale"]), "sales": int(total["sales at those addresses"]),
                      "median_miles_multi": half_up(total[miles[0]], 2), "median_miles_other": half_up(total[miles[1]], 2)}}
    return dict(figures=[figures], chart=chart, answer=answer, note=instructor_note, wrong=wrong, tolerance=tolerance, site=site)


WORDS = ["No", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten"]


def long_date(iso):
    d = datetime.strptime(iso, "%Y-%m-%d")
    return f"{d:%B} {d.day}, {d.year}"


WINDOW_TEXT = f"homes listed {long_date(v2.LISTING_WINDOW[0])} to {long_date(v2.LISTING_WINDOW[1])}"


def count_word(n):
    """A count at the start of a sentence: a word up to ten, otherwise the figure."""
    return WORDS[n] if n < len(WORDS) else f"{n:,}"


def join(items):
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def area_table(frame, kind):
    return Table("", [("Campus area", "text")] + [(c, kind) for c in frame.columns],
                 [[u] + list(r.values) for u, r in frame.iterrows()])


# ---- charts ---------------------------------------------------------------------
def style(ax, xlabel=None, ylabel=None):
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    for side in ["left", "bottom"]:
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    if xlabel:
        ax.set_xlabel(xlabel, color=INK, fontsize=9)
    if ylabel:
        ax.set_ylabel(ylabel, color=INK, fontsize=9)


def save(fig, name, alt):
    CHARTS.mkdir(parents=True, exist_ok=True)
    path = CHARTS / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white", metadata={"Software": None})
    plt.close(fig)
    return {"path": path, "alt": alt}


def hbar(ax, labels, values, colors, fmt_value, invert=True):
    y = range(len(labels))
    ax.barh(list(y), values, color=colors, height=0.6)
    ax.set_yticks(list(y), labels, color=INK, fontsize=9)
    if invert:  # first label on top; with a shared y axis, invert only once
        ax.invert_yaxis()
    for i, v in enumerate(values):
        ax.text(v, i, " " + fmt_value(v), va="center", fontsize=8, color=INK)


def chart_q1(t, alt):
    fig, axes = plt.subplots(1, 2, figsize=(9, 4), sharey=True)
    labels = [SHORT[u] for u in t.index]
    hbar(axes[0], labels, list(t["median sale price"] / 1000), [BLUE] * len(t), lambda v: f"${v:,.0f}K")
    hbar(axes[1], labels, list(t["median price per sq ft"]), [BLUE] * len(t), lambda v: f"${v:,.0f}", invert=False)
    style(axes[0], "Median sale price (thousands of dollars)")
    style(axes[1], "Median price per square foot (dollars)")
    for ax in axes:
        ax.margins(x=0.18)
    fig.suptitle("Question 1. Median sale price and price per square foot, by campus area", fontsize=10, color=INK, x=0.02, ha="left")
    return save(fig, "q1", alt)


def chart_q2(t):
    fig, axes = plt.subplots(1, 2, figsize=(9, 4), sharey=True)
    labels = [SHORT[u] for u in t.index]
    hbar(axes[0], labels, list(t["median days on market"]), [BLUE] * len(t), lambda v: trim(v))
    hbar(axes[1], labels, list(100 * t["share missing days on market"]), [BLUE] * len(t), lambda v: f"{v:.1f}%",
         invert=False)
    style(axes[0], "Median days on market")
    style(axes[1], "Share of sales with no days on market (%)")
    for ax in axes:
        ax.margins(x=0.18)
    fig.suptitle("Question 2. Days on market and the share missing, by campus area", fontsize=10, color=INK, x=0.02, ha="left")
    return save(fig, "q2", "Two bar charts ordered from fastest to slowest median days on market, with the share of "
                "sales that have no days on market beside each area.")


def chart_q3(shown, pattern, alt):
    order = list(SHORT)
    fig, axes = plt.subplots(3, 4, figsize=(10, 7))
    short_bands = ["<1", "1-2", "2-5", "5-10", "10+"]
    for ax, u in zip(axes.flat, order):
        values = shown.loc[u].astype(float)
        color = ORANGE if pattern.loc[u, "pattern"] == "does not fall" else BLUE
        x = [i for i, v in enumerate(values) if v == v]
        ax.plot(x, [values.iloc[i] for i in x], color=color, linewidth=2, marker="o", markersize=5)
        ax.set_xticks(range(5), short_bands, fontsize=8)
        ax.set_title(SHORT[u], fontsize=9, color=INK, loc="left")
        style(ax)
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        ax.grid(axis="x", visible=False)
        ax.tick_params(labelsize=8)
    axes.flat[-1].axis("off")
    axes.flat[-1].text(0, 0.6, "Miles from campus on each x axis.\nDollars per sq ft on each y axis;\nscales differ by area.\n\n"
                       "Orange: price per sq ft does\nnot fall with distance.\nMissing points: fewer than 20 sales.",
                       fontsize=8, color=MUTED, va="top")
    fig.suptitle("Question 3. Median price per square foot by distance band, one panel per campus area",
                 fontsize=10, color=INK, x=0.02, ha="left")
    fig.tight_layout()
    return save(fig, "q3", alt)


def chart_q4(t, fastest, slowest):
    fig, ax = plt.subplots(figsize=(9, 3.6))
    med = t["median days on market"]
    colors = [ORANGE if m in fastest or m == slowest else BLUE for m in t.index]
    ax.bar([m[:3] for m in t.index], list(med), color=colors, width=0.6)
    for i, v in enumerate(med):
        ax.text(i, v, trim(v), ha="center", va="bottom", fontsize=8, color=INK)
    style(ax, "Month listed", "Median days on market")
    ax.grid(axis="x", visible=False)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.tick_params(axis="x", colors=INK)
    fig.suptitle(f"Question 4. Median days on market by month listed, {WINDOW_TEXT}; fastest and slowest in orange",
                 fontsize=10, color=INK, x=0.02, ha="left")
    return save(fig, "q4", f"Bar chart of median days on market by month listed. {join(fastest)} are fastest and "
                f"{slowest} is slowest.")


def chart_q5(t, far, alt):
    fig, ax = plt.subplots(figsize=(8, 4))
    labels = [SHORT[u] for u in t.index]
    values = list(t["median assessed / sale price"])
    hbar(ax, labels, values, [ORANGE if u in far else BLUE for u in t.index], lambda v: f"{v:.2f}")
    ax.axvline(1, color=MUTED, linewidth=1, linestyle="--")
    ax.text(1, len(labels) - 0.4, " ratio of 1", color=MUTED, fontsize=8, va="bottom")
    style(ax, "Median ratio of assessed value to sale price")
    ax.margins(x=0.15)
    fig.suptitle("Question 5. Median assessed value / sale price; areas far from 1 in orange",
                 fontsize=10, color=INK, x=0.02, ha="left")
    return save(fig, "q5", alt)


def chart_q6(by_area, alt):
    t = by_area[by_area["sales at those addresses"] > 0]
    fig, ax = plt.subplots(figsize=(8, 3.2))
    hbar(ax, [SHORT[u] for u in t.index], list(t["sales at those addresses"]), [BLUE] * len(t), lambda v: f"{int(v)}")
    style(ax, "Sales at addresses with more than one sale")
    ax.margins(x=0.12)
    fig.suptitle("Question 6. Sales at repeated addresses, by campus area (areas with none left out)",
                 fontsize=10, color=INK, x=0.02, ha="left")
    return save(fig, "q6", alt)


# ---- writers --------------------------------------------------------------------
TOLERANCE_INTRO = (
    "Mark an answer correct when it is within the tolerance stated for its question. The tolerances allow for "
    "rounding but not for a different definition: each common wrong answer below falls outside them."
)


def build(df):
    texts = question_texts()
    builders = [q1, q2, q3, q4, q5, q6]
    titles = ["Price levels", "Speed", "Distance", "Timing", "Assessment", "Buildings"]
    return [dict(number=i + 1, title=titles[i], text=texts[i], **fn(df)) for i, fn in enumerate(builders)]


def write_markdown(key):
    lines = [
        "# Variation 2 Answer Key",
        "",
        "This key gives the answer to each of the six Variation 2 questions, as computed by the reference code. "
        "For each question it shows the figures, a chart, a model answer, the common wrong answers with the figures "
        "they produce, and the tolerance for marking. The workbook `Variation 2 Answer Key.xlsx` holds the same "
        "figures.",
        "",
        "The case's definitions apply throughout: a valid sale is $1,000 or more; price per square foot is computed "
        "per valid sale with at least 100 sq ft, then the median is taken; days on market runs from `list_date` to "
        "`contract_date`; groups under 20 sales show \"fewer than 20 sales\"; medians, not means.",
        "",
        TOLERANCE_INTRO,
        "",
        "To regenerate every number here, run `python run_all.py` in `instructor/reference-code`.",
    ]
    for q in key:
        lines += ["", "<!-- pagebreak -->", "", f"## Question {q['number']}. {q['title']}", "", f"> {strip_bold_title(q['text'])}", ""]
        lines += ["### Figures", ""]
        for table in q["figures"]:
            if table.title:
                lines += [f"**{table.title}**", ""]
            lines += [table.markdown(), ""]
            if table.note:
                lines += [table.note, ""]
        rel = q["chart"]["path"].relative_to(WORD_SOURCES)
        lines += ["### Chart", "", f"![{q['chart']['alt']}]({rel.as_posix()})", ""]
        lines += ["### Model answer", ""]
        for para in q["answer"]:
            lines += [para, ""]
        for source in q.get("sources", []):
            lines += [f"- {source}"]
        if q.get("sources"):
            lines += [""]
        if q.get("note"):
            lines += [q["note"], ""]
        lines += ["### Common wrong answers", ""]
        for label, cause, table in q["wrong"]:
            lines += [f"**{label}.** {cause}", "", table.markdown(), ""]
        lines += ["### Tolerance", ""]
        lines += [f"- {t}" for t in q["tolerance"]]
    MARKDOWN.parent.mkdir(parents=True, exist_ok=True)
    MARKDOWN.write_text("\n".join(lines) + "\n")


def strip_bold_title(text):
    return re.sub(r"^\*\*[^*]+\*\*\s*", "", text)


def write_workbook(key):
    wb = Workbook()
    bold = Font(bold=True)
    head_fill = PatternFill("solid", fgColor="EEF2F7")
    wrap = Alignment(wrap_text=True, vertical="top")

    ws = wb.active
    ws.title = "Read me"
    readme = [
        ("Variation 2 Answer Key", bold),
        ("Campus Comps: Building a Data Website with an AI Coding Agent", None),
        ("", None),
        ("One sheet per question, with the figures, the chart, the model answer, the common wrong answers and the "
         "tolerance. The Word answer key holds the same figures.", None),
        ("Definitions: a valid sale is $1,000 or more; price per square foot is computed per valid sale with at least "
         "100 sq ft, then the median is taken; days on market runs from list_date to contract_date; groups under 20 "
         "sales show \"fewer than 20 sales\"; medians, not means.", None),
        (TOLERANCE_INTRO, None),
        ("Every figure was computed by the reference code (instructor/reference-code/run_all.py).", None),
        ("", None),
        ("College-town home sales dataset, version 1.0 (2026). University of Illinois-Deloitte Foundation Center for "
         "Business Emerging Technologies. Data collected March 2026.", None),
        ("Funded by the University of Illinois-Deloitte Foundation Center for Business Emerging Technologies.", None),
    ]
    for i, (text, font) in enumerate(readme, start=1):
        c = ws.cell(row=i, column=1, value=text)
        c.alignment = wrap
        if font:
            c.font = font
    ws.column_dimensions["A"].width = 110

    for q in key:
        ws = wb.create_sheet(f"Q{q['number']} {q['title']}")
        row = 1
        ws.cell(row=row, column=1, value=f"Question {q['number']}. {q['title']}").font = Font(bold=True, size=13)
        row += 1
        ws.cell(row=row, column=1, value=plain(strip_bold_title(q["text"]))).alignment = wrap
        row += 2

        def put_table(table, row):
            if table.title:
                ws.cell(row=row, column=1, value=table.title).font = bold
                row += 1
            for c, (h, _) in enumerate(table.columns, start=1):
                cell = ws.cell(row=row, column=c, value=h)
                cell.font, cell.fill, cell.alignment = bold, head_fill, wrap
            row += 1
            for r in table.rows:
                for c, (v, (_, kind)) in enumerate(zip(r, table.columns), start=1):
                    if isinstance(v, str) or is_missing(v):
                        ws.cell(row=row, column=c, value=v if isinstance(v, str) else "none")
                    else:
                        cell = ws.cell(row=row, column=c, value=FORMATS[kind][1](v))
                        cell.number_format = FORMATS[kind][2]
                row += 1
            if table.note:
                ws.cell(row=row, column=1, value=table.note)
                row += 1
            return row + 1

        ws.cell(row=row, column=1, value="Figures").font = Font(bold=True, size=12)
        row += 1
        for table in q["figures"]:
            row = put_table(table, row)
        ws.cell(row=row, column=1, value="Model answer").font = Font(bold=True, size=12)
        row += 1
        for para in q["answer"] + q.get("sources", []) + ([q["note"]] if q.get("note") else []):
            ws.cell(row=row, column=1, value=plain(para)).alignment = Alignment(wrap_text=False)
            row += 1
        row += 1
        ws.cell(row=row, column=1, value="Common wrong answers").font = Font(bold=True, size=12)
        row += 1
        for label, cause, table in q["wrong"]:
            ws.cell(row=row, column=1, value=f"{label}. {plain(cause)}").font = bold
            row += 1
            row = put_table(table, row)
        ws.cell(row=row, column=1, value="Tolerance").font = Font(bold=True, size=12)
        row += 1
        for t in q["tolerance"]:
            ws.cell(row=row, column=1, value=plain(t))
            row += 1
        widths = [46] + [20] * 8
        for c, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(c)].width = w
        img = XLImage(str(q["chart"]["path"]))
        scale = 620 / img.width
        img.width, img.height = int(img.width * scale), int(img.height * scale)
        ws.add_image(img, "J2")

    wb.properties.creator = ""
    wb.properties.lastModifiedBy = ""
    wb.properties.created = FIXED_TIME
    wb.properties.modified = FIXED_TIME
    WORKBOOK.parent.mkdir(parents=True, exist_ok=True)
    wb.save(WORKBOOK)


def plain(text):
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    return text.replace("**", "").replace("`", "")


def site_answers(key, df):
    by = {q["number"]: q["site"] for q in key}
    return {
        "source": "College-town home sales dataset, version 1.0",
        "rows": len(df),
        "rules": {"min_price": 1000, "min_sqft": 100, "min_group": v2.MIN_GROUP},
        "counts": {
            "valid_sales": int(df["valid_price"].sum()),
            "pps_sales": int(df["price_per_sqft"].notna().sum()),
            "dom_sales": int(df["days_on_market"].notna().sum()),
            "assessed_sales": int((df["valid_price"] & (df["tax_assessed_value"] > 0)).sum()),
        },
        "sale_dates": [df["sale_date"].min().strftime("%Y-%m-%d"), df["sale_date"].max().strftime("%Y-%m-%d")],
        "q1": by[1], "q2": by[2], "q3": by[3], "q4": by[4], "q5": by[5], "q6": by[6],
    }


def write_all(df, site_paths=()):
    key = build(df)
    write_markdown(key)
    write_workbook(key)
    answers = site_answers(key, df)
    for path in site_paths:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(answers, indent=1) + "\n")
    return key, answers
