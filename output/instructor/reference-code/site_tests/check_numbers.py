"""Check that the numbers each reference site shows match the reference code.

    python check_numbers.py <text-folder>

Reads what check_sites.js saved from each page (every table cell, every filled-in
figure and the headline numbers) and compares it with figures computed here from
the full dataset:

- Variation 2: every table cell against the answer key, within the rounding the
  page displays, and every number in the answers' text against the key's values.
- Variation 1: every table cell and figure against the reference summary.
- Variation 3: the headline numbers at five settings, recomputed from the dataset.
"""

import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import answer_key  # noqa: E402
import sites  # noqa: E402
import variation2 as v2  # noqa: E402
from definitions import add_derived, half_up, load  # noqa: E402

FULL = {short: full for full, short in v2.SHORT_NAMES.items()}
SMALL, NONE = "Fewer than 20 sales", "No sales"


def number(text):
    t = text.replace("$", "").replace(",", "").replace("%", "").replace(" days", "").replace(" day", "").strip()
    return float(t)


class Checker:
    def __init__(self, name):
        self.name, self.checked, self.failures = name, 0, []

    def close(self, where, shown, expected, tol):
        self.checked += 1
        try:
            ok = abs(number(shown) - float(expected)) <= tol + 1e-9
        except ValueError:
            ok = False
        if not ok:
            self.failures.append(f"{where}: page shows {shown!r}, expected {expected}")

    def same(self, where, shown, expected):
        self.checked += 1
        if shown != expected:
            self.failures.append(f"{where}: page shows {shown!r}, expected {expected!r}")

    def report(self):
        status = "pass" if not self.failures else "FAIL"
        print(f"{status}  {self.name}: {self.checked} values checked, {len(self.failures)} differ")
        for f in self.failures[:20]:
            print("      " + f)
        return not self.failures


def area_of(label):
    return FULL[label.split(" (")[0]]


def table(dump, section):
    return [t["rows"] for t in dump["tables"] if t["section"] == section][0]


def check_v2(dump, df):
    c = Checker("v2-six-questions tables and text against the answer key")
    q1 = v2.q1_price_levels(df)
    for row in table(dump, "q1")[1:]:
        u = area_of(row[0])
        c.close(f"Q1 {u} valid sales", row[1], q1.loc[u, "valid sales"], 0)
        c.close(f"Q1 {u} median price", row[2], q1.loc[u, "median sale price"], 0.5)
        c.close(f"Q1 {u} rank by price", row[3], q1.loc[u, "rank by price"], 0)
        c.close(f"Q1 {u} sales with price per sq ft", row[4], q1.loc[u, "sales with price per sq ft"], 0)
        c.close(f"Q1 {u} median price per sq ft", row[5], q1.loc[u, "median price per sq ft"], 0.005)
        c.close(f"Q1 {u} rank by price per sq ft", row[6], q1.loc[u, "rank by price per sq ft"], 0)

    q2 = v2.q2_speed(df)
    for row in table(dump, "q2")[1:]:
        u = area_of(row[0])
        c.close(f"Q2 {u} sales", row[1], q2.loc[u, "sales"], 0)
        c.close(f"Q2 {u} sales with days on market", row[2], q2.loc[u, "sales with days on market"], 0)
        c.close(f"Q2 {u} median days", row[3], q2.loc[u, "median days on market"], 0.05)
        c.close(f"Q2 {u} share missing", row[4], 100 * q2.loc[u, "share missing days on market"], 0.05)

    counts, medians, _ = v2.q3_distance(df)
    pattern = v2.q3_pattern(medians.where(counts >= v2.MIN_GROUP))
    for row in table(dump, "q3")[1:]:
        u = FULL[row[0]]
        for b, cell in zip(v2.BAND_LABELS, row[1:6]):
            n = counts.loc[u, b]
            if n == 0:
                c.same(f"Q3 {u} {b}", cell, NONE)
            elif n < v2.MIN_GROUP:
                c.same(f"Q3 {u} {b}", cell, SMALL)
            else:
                c.close(f"Q3 {u} {b}", cell, medians.loc[u, b], 0.5)
        c.same(f"Q3 {u} pattern", row[6].lower(), pattern.loc[u, "pattern"])

    q4 = v2.q4_timing(df, window=True)
    for row in table(dump, "q4")[1:]:
        c.close(f"Q4 {row[0]} listings", row[1], q4.loc[row[0], "listings with days on market"], 0)
        c.close(f"Q4 {row[0]} median days", row[2], q4.loc[row[0], "median days on market"], 0.05)

    q5 = v2.q5_assessment(df)
    for row in table(dump, "q5")[1:]:
        u = area_of(row[0])
        c.same(f"Q5 {u} state", row[1], q5.loc[u, "state"])
        c.close(f"Q5 {u} sales used", row[2], q5.loc[u, "sales used"], 0)
        c.close(f"Q5 {u} ratio", row[3], q5.loc[u, "median assessed / sale price"], 0.0005)

    q6, total = v2.q6_buildings(df)
    rows = table(dump, "q6")
    for row in rows[1:-1]:
        u = area_of(row[0])
        r = q6.loc[u]
        c.close(f"Q6 {u} addresses", row[1], r["addresses with more than one sale"], 0)
        c.close(f"Q6 {u} sales", row[2], r["sales at those addresses"], 0)
        if r["sales at those addresses"] == 0:
            c.same(f"Q6 {u} median miles", row[3], NONE)
        elif r["sales at those addresses"] < v2.MIN_GROUP:
            c.same(f"Q6 {u} median miles", row[3], SMALL)
        else:
            c.close(f"Q6 {u} median miles", row[3], r["median miles, sales at those addresses"], 0.05)
        c.close(f"Q6 {u} median miles, others", row[4], r["median miles, all other sales"], 0.05)
    foot = rows[-1]
    c.close("Q6 total addresses", foot[1], total["addresses with more than one sale"], 0)
    c.close("Q6 total sales", foot[2], total["sales at those addresses"], 0)
    c.close("Q6 total median miles", foot[3], total["median miles, sales at those addresses"], 0.05)
    c.close("Q6 total median miles, others", foot[4], total["median miles, all other sales"], 0.05)

    # Numbers in the answers' text: each must be one of the key's values in a form the page uses.
    allowed = allowed_values(df)
    dates = {"firstSale": long_date(df["sale_date"].min()), "lastSale": long_date(df["sale_date"].max()),
             "q4.window": "homes listed from " + long_date(pd.Timestamp(v2.LISTING_WINDOW[0])) + " through "
             + long_date(pd.Timestamp(v2.LISTING_WINDOW[1]))}
    for key, text in dump["facts"]:
        if key in dates:
            c.same(f"text {key}", text, dates[key])
    for key, text in [f for f in dump["facts"] if f[0] not in dates] + [("figure", s) for s in dump["stats"]]:
        for token in re.findall(r"\$?\d[\d,]*\.?\d*%?", text):
            c.checked += 1
            if token.strip(".") not in allowed:
                c.failures.append(f"text {key}: {token!r} is not a value in the answer key")
    return c.report()


def long_date(ts):
    return f"{ts:%B} {ts.day}, {ts.year}"


def allowed_values(df):
    """Every answer-key value, formatted every way the V2 page formats numbers."""
    key, answers = answer_key.build(df), answer_key.site_answers(answer_key.build(df), df)
    values = set()

    def walk(x):
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, (int, float)) and not isinstance(x, bool):
            values.add(float(x))

    walk(answers)
    out = {"1", "11", "20", "5", "5%", "2"}
    for v in values:
        out |= {f"{half_up(v):,}", f"${half_up(v):,}", f"${v:,.2f}", f"{v:.2f}", f"{v:.1f}", f"{v:.3f}",
                f"{half_up(100 * v)}%", f"{100 * v:.1f}%", f"{v:g}", f"${v / 1e6:.1f}"}
    return out


def check_v1(dump, df):
    c = Checker("v1-old-homes-close-in table and figures against the reference summary")
    s = sites.v1_summary(df)
    rows = table(dump, "")[1:] if any(t["section"] == "" for t in dump["tables"]) else dump["tables"][0]["rows"][1:]
    names = {u: short for u, short in v2.SHORT_NAMES.items()}
    for row in rows:
        area = "All campus areas" if row[0] == "All campus areas" else names[row[0]]
        a = s["areas"][area]
        c.close(f"{area} sales", row[1], a["rows"], 0)
        c.close(f"{area} median year", row[2], a["median_year"], 0)
        for col, band in [(3, 0), (4, 3)]:
            b = a["by_band"][band]
            if b["median_year"] is None:
                c.same(f"{area} band {band}", row[col], "Too few" if b["n"] else NONE)
            else:
                c.close(f"{area} band {band}", row[col], b["median_year"], 0)
        c.close(f"{area} new share", row[5], 100 * a["new_share"], 0.05)
        if a["new_no_list_share"] is None:
            c.same(f"{area} new without listing", row[6], "Too few")
        else:
            c.close(f"{area} new without listing", row[6], 100 * a["new_no_list_share"], 0.5)
    facts = dict(dump["facts"])
    all_ = s["areas"]["All campus areas"]
    c.close("near year", facts["nearYear"], all_["by_band"][0]["median_year"], 0)
    c.close("far year", facts["farYear"], all_["by_band"][3]["median_year"], 0)
    shown = [d for d in all_["by_decade"] if d["median_pps"] is not None]
    hi = max(shown, key=lambda d: d["median_pps"])
    lo = min(shown, key=lambda d: d["median_pps"])
    c.same("peak decade", facts["peakDecade"], f"{hi['decade']}s")
    c.close("peak price per sq ft", facts["peakPps"], hi["median_pps"], 0.5)
    c.same("low decade", facts["lowDecade"], f"{lo['decade']}s")
    c.close("low price per sq ft", facts["lowPps"], lo["median_pps"], 0.5)
    c.close("new share", facts["newShare"], 100 * all_["new_share"], 0.05)
    c.close("new without listing", facts["newNoList"], 100 * s["listing"]["new_no_list_share"], 0.5)
    c.close("older without listing", facts["oldNoList"], 100 * s["listing"]["older_no_list_share"], 0.5)
    c.close("Virginia pairs", facts["vaPairs"], s["virginia_double_records"]["new_pairs"], 0)
    c.close("Virginia one copy", facts["vaOneCopy"], 100 * s["virginia_double_records"]["new_share_one_copy"], 0.05)
    return c.report()


def check_v3(settings, df):
    """Recompute the V3 headline numbers from the full dataset, without the site's data file."""
    c = Checker("v3-close-to-campus headline numbers at five settings, recomputed from the dataset")
    first, last = sites.v3_window(df)
    recent = df[(df["sale_date"] >= first) & (df["sale_date"] <= last) & (df["sale_price"] >= sites.V3_MIN_PRICE)]
    for s in settings:
        u = FULL[s["campus"]]
        near = recent[(recent["university"] == u) & (recent["miles_to_campus"] <= s["dist"])]
        inb = near[near["sale_price"] <= s["budget"]]
        where = f"{s['campus']} ${s['budget']:,} {s['dist']} mi"
        c.same(f"{where} share", s["share"], f"{half_up(100 * len(inb) / len(near))}%")
        c.same(f"{where} counts", s["counts"].split(" homes")[0], f"{len(inb):,} of the {len(near):,}")
        sq = inb["living_area_sqft"].where(inb["living_area_sqft"] >= 100).dropna()
        c.same(f"{where} size", s["sqft"], f"{half_up(sq.median()):,} sq ft" if len(sq) >= 20 else "Too few sales")
        dom = inb["days_on_market"].dropna()
        c.same(f"{where} days", s["dom"], f"{float(dom.median()):g} days" if len(dom) >= 20 else "Too few sales")
        c.same(f"{where} budget", s["budgetShown"], f"${s['budget']:,}")
    return c.report()


def main():
    folder = Path(sys.argv[1])
    df = add_derived(load())
    ok = [
        check_v1(json.loads((folder / "v1-old-homes-close-in.json").read_text()), df),
        check_v2(json.loads((folder / "v2-six-questions.json").read_text()), df),
        check_v3(json.loads((folder / "v3-settings.json").read_text()), df),
    ]
    sys.exit(0 if all(ok) else 1)


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    main()
