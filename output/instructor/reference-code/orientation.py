"""Fill the data figures into the instructor orientation.

The orientation's text lives in output/source/word-documents/templates/
instructor_orientation.md, with each data figure written as {{name}}. This module
computes every one of those figures and writes the finished markdown, which
build.js turns into the Word document. No figure in the orientation is typed by hand.
"""

import re

import variation2 as v2
import wrong_answers
from answer_key import fmt
from definitions import ADDRESS_KEY, REPO_ROOT, half_up

TEMPLATE = REPO_ROOT / "output" / "source" / "word-documents" / "templates" / "instructor_orientation.md"
OUTPUT = REPO_ROOT / "output" / "source" / "word-documents" / "instructor_orientation.md"


def figures(df):
    f = {}
    n = len(df)
    both = df["days_on_market"].notna()
    to_close = (df["sale_date"] - df["list_date"]).dt.days
    f["rows"] = f"{n:,}"
    f["campuses"] = str(df["university"].nunique())
    f["cities"] = str(df[["city", "state"]].drop_duplicates().shape[0])
    f["states"] = str(df["state"].nunique())
    f["dom_rows"] = f"{int(both.sum()):,}"
    f["dom_share"] = f"{half_up(100 * both.mean(), 1)}%"
    f["dom_missing_share"] = f"{half_up(100 * (1 - both.mean()))}%"
    f["dom"] = fmt(df["days_on_market"].median(), "days")
    f["dom_mean"] = fmt(df["days_on_market"].astype(float).mean(), "days")
    f["dom_blank_zero"] = fmt(df["days_on_market"].astype(float).fillna(0).median(), "days")
    f["dom_to_close"] = fmt(to_close.median(), "days")

    q2 = v2.q2_speed(df)
    f["dom_area_min"] = fmt(q2["median days on market"].min(), "days")
    f["dom_area_max"] = fmt(q2["median days on market"].max(), "days")
    wrong_q2 = wrong_answers.q2(df)["Median days on market"]
    mich = "University of Michigan"
    f["mich_dom"] = fmt(wrong_q2.loc[mich, "correct: list_date to contract_date"], "days")
    f["mich_dom_to_close"] = fmt(wrong_q2.loc[mich, "measured to sale_date"], "days")

    shared = df[df["shared_address"]]
    f["shared_rows"] = f"{len(shared):,}"
    f["shared_addresses"] = f"{shared[ADDRESS_KEY].drop_duplicates().shape[0]:,}"
    f["dedup_loss"] = f"{len(shared) - shared[ADDRESS_KEY].drop_duplicates().shape[0]:,}"
    f["after_dedup"] = f"{n - (len(shared) - shared[ADDRESS_KEY].drop_duplicates().shape[0]):,}"
    street = df.groupby("address_street")["listing_id"].transform("size") > 1
    f["street_rows"] = f"{int(street.sum()):,}"

    in_psu = shared["university"] == "The Pennsylvania State University"
    f["psu_rows"] = str(int(in_psu.sum()))
    f["psu_addresses"] = str(shared[in_psu][ADDRESS_KEY].drop_duplicates().shape[0])
    f["other_shared_rows"] = str(int((~in_psu).sum()))
    f["other_shared_addresses"] = str(shared[~in_psu][ADDRESS_KEY].drop_duplicates().shape[0])

    price = df["sale_price"]
    f["price_under_1000"] = str(int((price < 1000).sum()))
    f["price_zero"] = str(int((price == 0).sum()))
    f["price_under_10000"] = str(int((price < 10_000).sum()))
    f["price_over_5m"] = str(int((price > 5_000_000).sum()))
    f["max_price"] = fmt(price.max(), "money")
    f["median_price"] = fmt(df["price"].median(), "money")
    f["mean_price"] = fmt(df["price"].astype(float).mean(), "money")

    types = df["home_type"].value_counts()
    f["single_family"] = f"{int(types['SINGLE_FAMILY']):,}"
    f["zero_sqft"] = str(int((df["living_area_sqft"] == 0).sum()))
    wrong_q1 = wrong_answers.q1(df)["Median price per sq ft"]
    ga = "University of Georgia"
    f["ga_pps"] = fmt(wrong_q1.loc[ga, "correct: median of per-sale values"], "money2")
    f["ga_pps_blank_zero"] = fmt(wrong_q1.loc[ga, "no area floor, blank or 0 sq ft divided as 0"], "money2")
    f["ga_area_missing"] = f"{int((df[df['university'] == ga]['living_area_sqft'].isna()).sum()):,}"

    q4_all = v2.q4_timing(df, window=False)["median days on market"]
    q4_win = v2.q4_timing(df, window=True)["median days on market"]
    f["dec_all_years"] = fmt(q4_all["December"], "days")
    f["dec_window"] = fmt(q4_win["December"], "days")
    f["built_1900"] = str(int((df["year_built"] == 1900).sum()))
    return f


def write(df):
    values = figures(df)
    text = TEMPLATE.read_text()
    missing = sorted(set(re.findall(r"\{\{(\w+)\}\}", text)) - set(values))
    if missing:
        raise KeyError(f"The orientation template uses figures that are not computed: {missing}")
    OUTPUT.write_text(re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], text))
    return OUTPUT, values
