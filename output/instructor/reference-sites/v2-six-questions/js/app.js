/* Builds the answers, charts and tables from data/answers.json (made by scripts/build_data.py).
   No number on the page is typed by hand: every one is filled in from that file. */
(function () {
  "use strict";
  var C = window.Charts;

  var money = function (v) { return "$" + Math.round(v).toLocaleString("en-US"); };
  var money2 = function (v) { return "$" + v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); };
  var int = function (v) { return Math.round(v).toLocaleString("en-US"); };
  var pct = function (v) { return Math.round(v * 100) + "%"; };
  var pct1 = function (v) { return (v * 100).toFixed(1) + "%"; };
  var num = function (v) { return v % 1 ? String(Math.round(v * 10) / 10) : String(v); };
  var days = function (v) { return num(v) + (v === 1 ? " day" : " days"); };
  var mi = function (v) { return v.toFixed(1); };
  var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  var SMALL = "Fewer than 20 sales";

  function list(names) {
    return names.length < 2 ? names.join("") : names.slice(0, -1).join(", ") + " and " + names[names.length - 1];
  }
  function longDate(iso) {
    var p = iso.split("-").map(Number);
    return new Date(Date.UTC(p[0], p[1] - 1, p[2])).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric", timeZone: "UTC" });
  }
  function byId(id) { return document.getElementById(id); }

  // Build a table with text nodes only. cols: [{head, get}]
  function table(container, cols, rows, foot) {
    container.textContent = "";
    var t = document.createElement("table");
    var thead = t.createTHead().insertRow();
    cols.forEach(function (c) { var th = document.createElement("th"); th.scope = "col"; th.textContent = c.head; thead.appendChild(th); });
    var tb = t.createTBody();
    rows.forEach(function (r) {
      var tr = tb.insertRow();
      cols.forEach(function (c, i) {
        var td = i === 0 ? document.createElement("th") : document.createElement("td");
        if (i === 0) { td.scope = "row"; td.style.fontWeight = "500"; }
        td.textContent = c.get(r);
        tr.appendChild(td);
      });
    });
    if (foot) {
      var tf = t.createTFoot().insertRow();
      foot.forEach(function (v) { var td = document.createElement("td"); td.textContent = v; tf.appendChild(td); });
    }
    container.appendChild(t);
  }

  // Every sentence's numbers and names, worked out from the data.
  function facts(d) {
    var f = {}, i;
    f.rows = int(d.rows);
    f.firstSale = longDate(d.sale_dates[0]);
    f.lastSale = longDate(d.sale_dates[1]);
    f.valid = int(d.counts.valid_sales);
    f.invalid = int(d.counts.invalid_sales);
    f.zero = d.counts.zero_price_sales === 1 ? "one" : int(d.counts.zero_price_sales);
    f.pps = int(d.counts.pps_sales);
    f.dom = int(d.counts.dom_sales);
    f.assessed = int(d.counts.assessed_sales);
    f.maxPrice = "$" + (d.counts.max_price / 1e6).toFixed(1) + " million";

    // Question 1
    var q1 = d.q1, top = q1[0], bottom = q1[q1.length - 1];
    var moved = q1.filter(function (r) { return r.rank_price !== r.rank_pps; });
    f["q1.top"] = top.campus; f["q1.topPrice"] = money(top.median_price); f["q1.topPps"] = money(top.median_pps);
    f["q1.bottom"] = bottom.campus; f["q1.bottomPrice"] = money(bottom.median_price); f["q1.bottomPps"] = money(bottom.median_pps);
    f["q1.swap"] = list(moved.map(function (r) { return r.campus; }));
    f["q1.swapCount"] = moved.length === 2 ? "1 swap" : moved.length + " areas move";
    var hi = moved[0], lo = moved[moved.length - 1];
    f["q1.hiName"] = hi.campus; f["q1.loName"] = lo.campus;
    f["q1.hiPrice"] = money(hi.median_price); f["q1.loPrice"] = money(lo.median_price);
    f["q1.hiSqft"] = int(hi.median_sqft); f["q1.loSqft"] = int(lo.median_sqft);

    // Question 2 (sorted fastest first)
    var q2 = d.q2, fastest = q2[0].median_dom;
    var fast = q2.filter(function (r) { return r.median_dom === fastest; }).map(function (r) { return r.campus; }).sort();
    var slow = q2.slice(-3).reverse();
    f["q2.fastest"] = days(fastest); f["q2.fastestNames"] = list(fast);
    f["q2.slowest"] = list(slow.map(function (r, k) { return r.campus + " (" + (k === 0 ? days(r.median_dom) : num(r.median_dom)) + ")"; }));
    f["q2.slowestName"] = slow[0].campus; f["q2.slowestValue"] = days(slow[0].median_dom);
    var miss = q2.slice().sort(function (a, b) { return b.missing_share - a.missing_share; });
    f["q2.missMax"] = pct(miss[0].missing_share); f["q2.missMaxName"] = miss[0].campus;
    f["q2.miss2"] = pct(miss[1].missing_share); f["q2.miss2Name"] = miss[1].campus;
    f["q2.missMin"] = pct(miss[miss.length - 1].missing_share);

    // Question 3
    var rows = d.q3.rows, names = function (p) { return rows.filter(function (r) { return r.pattern === p; }).map(function (r) { return r.campus; }).sort(); };
    var nofall = rows.filter(function (r) { return r.pattern === "does not fall"; });
    var worst = null, worstRise = -1;
    nofall.forEach(function (r) {
      var v = r.cells.map(function (c) { return c.median_pps; }).filter(function (x) { return x != null; });
      for (i = 1; i < v.length; i++) if (v[i] / v[i - 1] - 1 > worstRise) { worstRise = v[i] / v[i - 1] - 1; worst = r; }
    });
    f["q3.every"] = list(names("falls at every step"));
    f["q3.overall"] = list(names("falls overall"));
    f["q3.nofall"] = list(names("does not fall"));
    f["q3.fallCount"] = String(rows.length - nofall.length);
    f["q3.nearCount"] = String(rows.filter(function (r) { return r.highest_band === d.q3.bands[0]; }).length);
    f["q3.maxRise"] = Math.round(d.q3.max_rise * 100) + "%";
    f["q3.worst"] = worst.campus;
    f["q3.worstBand"] = worst.highest_band.toLowerCase();
    f["q3.worstValue"] = money(worst.cells[d.q3.bands.indexOf(worst.highest_band)].median_pps);
    f["q3.worstNear"] = money(worst.cells[0].median_pps);

    // Question 4
    var months = d.q4.months, minM = Math.min.apply(null, months.map(function (m) { return m.median_dom; }));
    var bySlow = months.slice().sort(function (a, b) { return b.median_dom - a.median_dom; });
    f["q4.fastest"] = days(minM);
    f["q4.fastestNames"] = list(months.filter(function (m) { return m.median_dom === minM; }).map(function (m) { return m.name; }));
    f["q4.slowestName"] = bySlow[0].name; f["q4.slowest"] = days(bySlow[0].median_dom);
    f["q4.secondName"] = bySlow[1].name; f["q4.second"] = days(bySlow[1].median_dom);
    f["q4.window"] = "homes listed from " + longDate(d.q4.window[0]) + " through " + longDate(d.q4.window[1]);

    // Question 5 (sorted lowest ratio first)
    var q5 = d.q5, far = q5.filter(function (r) { return r.median_ratio < 0.5; }), rest = q5.filter(function (r) { return r.median_ratio >= 0.5; });
    var find = function (name) { return q5.filter(function (r) { return r.campus === name; })[0]; };
    f["q5.far"] = list(far.map(function (r) { return r.campus + " (" + r.median_ratio.toFixed(2) + ")"; }));
    f["q5.restCount"] = String(rest.length);
    f["q5.restMin"] = pct(rest[0].median_ratio); f["q5.restMax"] = pct(rest[rest.length - 1].median_ratio);
    f["q5.restMinRatio"] = rest[0].median_ratio.toFixed(2);
    f["q5.far0"] = far[0].median_ratio.toFixed(2); f["q5.far0Name"] = far[0].campus;
    f["q5.far1"] = far[1].median_ratio.toFixed(2); f["q5.far1Name"] = far[1].campus;
    f["q5.davisName"] = "UC Davis"; f["q5.davis"] = find("UC Davis").median_ratio.toFixed(2);
    f["q5.illinois"] = find("Illinois").median_ratio.toFixed(2);

    // Question 6 (rows sorted by sales, most first)
    var q6 = d.q6, big = q6.rows.filter(function (r) { return r.sales >= d.rules.min_group; })[0];
    f["q6.addresses"] = int(q6.total.addresses); f["q6.sales"] = int(q6.total.sales);
    f["q6.big0"] = big.campus + " (" + big.addresses + " addresses, " + big.sales + " sales)";
    f["q6.big0Sales"] = int(big.sales); f["q6.big0Name"] = big.campus;
    f["q6.multi"] = mi(q6.total.median_miles_multi); f["q6.other"] = mi(q6.total.median_miles_other);
    f["q6.nearMulti"] = mi(big.median_miles_multi); f["q6.nearOther"] = mi(big.median_miles_other);
    f["q6.few"] = list(q6.rows.filter(function (r) { return r.sales > 0 && r.sales < d.rules.min_group; }).map(function (r) { return r.campus; }).sort());
    f["q6.none"] = list(q6.rows.filter(function (r) { return r.sales === 0; }).map(function (r) { return r.campus; }).sort());
    return f;
  }

  function fill(f) {
    document.querySelectorAll("[data-fact]").forEach(function (el) {
      var v = f[el.getAttribute("data-fact")];
      if (v === undefined) throw new Error("No value for " + el.getAttribute("data-fact"));
      el.textContent = v;
    });
  }

  function render(d) {
    var f = facts(d);
    fill(f);
    var full = {};
    d.campuses.forEach(function (c) { full[c.short] = c; });
    var areaName = function (r) { return r.campus + " (" + full[r.campus].towns + ", " + full[r.campus].state + ")"; };

    // Question 1: rank slope chart
    var changed = function (r) { return r.rank_price !== r.rank_pps; };
    C.slope(byId("q1-chart"), {
      aria: "Slope chart comparing each campus area's rank by median sale price with its rank by median price per square foot. Only " + f["q1.swap"] + " change rank.",
      ltitle: "Median sale price", rtitle: "Median price per sq ft",
      rows: d.q1.map(function (r) {
        return { label: r.campus, l: r.rank_price, r: r.rank_pps, ldisp: money(r.median_price), rdisp: money(r.median_pps), cls: changed(r) ? "hl" : "" };
      })
    });
    table(byId("q1-table"), [
      { head: "Campus area", get: areaName },
      { head: "Valid sales", get: function (r) { return int(r.valid_sales); } },
      { head: "Median sale price", get: function (r) { return money(r.median_price); } },
      { head: "Rank", get: function (r) { return r.rank_price; } },
      { head: "Sales with 100+ sq ft", get: function (r) { return int(r.pps_sales); } },
      { head: "Median $ per sq ft", get: function (r) { return money2(r.median_pps); } },
      { head: "Rank", get: function (r) { return r.rank_pps; } },
      { head: "Median sq ft", get: function (r) { return int(r.median_sqft); } }
    ], d.q1);

    // Question 2: two aligned bar charts, fastest first
    var q2 = d.q2;
    var maxShare = Math.max.apply(null, q2.map(function (r) { return r.missing_share; }));
    C.hbar(byId("q2-chart-a"), {
      aria: "Bar chart of median days on market by campus area, from " + days(q2[0].median_dom) + " to " + days(q2[q2.length - 1].median_dom) + ".",
      rows: q2.map(function (r) {
        return { label: r.campus, value: r.median_dom, display: days(r.median_dom),
          tip: [[r.campus], [days(r.median_dom), "median"], [int(r.dom_sales), "sales with both dates"]] };
      })
    });
    C.hbar(byId("q2-chart-b"), {
      aria: "Bar chart of the share of sales with no days on market, by campus area, from " + f["q2.missMin"] + " to " + f["q2.missMax"] + ".",
      max: Math.ceil(maxShare * 10) / 10,
      rows: q2.map(function (r) {
        return { label: r.campus, value: r.missing_share, display: pct(r.missing_share), cls: "dim",
          tip: [[r.campus], [pct(r.missing_share), "with no days on market"], [int(r.rows - r.dom_sales) + " of " + int(r.rows), "sales"]] };
      })
    });
    table(byId("q2-table"), [
      { head: "Campus area", get: areaName },
      { head: "All sales", get: function (r) { return int(r.rows); } },
      { head: "Sales with both dates", get: function (r) { return int(r.dom_sales); } },
      { head: "Median days on market", get: function (r) { return num(r.median_dom); } },
      { head: "Share with no days on market", get: function (r) { return pct1(r.missing_share); } }
    ], q2);

    // Question 3: heat table with the pattern for each area
    var bins = [175, 225, 275, 350, 450];
    var binLabels = ["Under $175", "$175 to $224", "$225 to $274", "$275 to $349", "$350 to $449", "$450 or more"];
    var binOf = function (v) { for (var i = 0; i < bins.length; i++) if (v < bins[i]) return i + 1; return 6; };
    var scale = byId("q3-scale");
    scale.textContent = "";
    var sl = document.createElement("span"); sl.textContent = "Price per sq ft:"; scale.appendChild(sl);
    binLabels.forEach(function (lab, i) {
      var s = document.createElement("span");
      var sw = document.createElement("i"); sw.style.background = "var(--heat-" + (i + 1) + ")";
      s.appendChild(sw); s.appendChild(document.createTextNode(" " + lab));
      s.style.display = "inline-flex"; s.style.alignItems = "center"; s.style.gap = "0.3rem"; s.style.marginRight = "0.5rem";
      scale.appendChild(s);
    });
    var holder = byId("q3-table");
    holder.textContent = "";
    var t = document.createElement("table"); t.className = "heat";
    var cap = document.createElement("caption"); cap.className = "sr-only"; cap.textContent = "Median price per square foot by campus area and distance band";
    t.appendChild(cap);
    var hr = t.createTHead().insertRow();
    ["Campus area"].concat(d.q3.bands, ["With distance"]).forEach(function (h) { var th = document.createElement("th"); th.scope = "col"; th.textContent = h; hr.appendChild(th); });
    var tb = t.createTBody();
    d.q3.rows.forEach(function (r) {
      var tr = tb.insertRow();
      var th = document.createElement("th"); th.scope = "row"; th.textContent = r.campus; th.style.fontWeight = "500"; tr.appendChild(th);
      r.cells.forEach(function (c, i) {
        var td = tr.insertCell();
        if (c.median_pps == null) {
          td.className = "cell none";
          td.textContent = c.n === 0 ? "No sales" : SMALL;
          if (c.n > 0) { var sm = document.createElement("small"); sm.textContent = c.n + " sold"; td.appendChild(sm); }
        } else {
          td.className = "cell h" + binOf(c.median_pps);
          td.textContent = money(c.median_pps);
          var small = document.createElement("small"); small.textContent = int(c.n) + " sold"; td.appendChild(small);
        }
        td.setAttribute("aria-label", r.campus + ", " + d.q3.bands[i] + ": " + (c.median_pps == null ? (c.n === 0 ? "no sales" : "fewer than 20 sales") : money2(c.median_pps) + " per sq ft, " + c.n + " sales"));
      });
      var pt = tr.insertCell(); pt.className = "pattern" + (r.pattern === "does not fall" ? " flag" : ""); pt.textContent = r.pattern.charAt(0).toUpperCase() + r.pattern.slice(1);
    });
    holder.appendChild(t);

    // Question 4: columns by month
    var months = d.q4.months;
    var minDom = Math.min.apply(null, months.map(function (r) { return r.median_dom; }));
    var maxDom = Math.max.apply(null, months.map(function (r) { return r.median_dom; }));
    var top = Math.ceil(maxDom / 5) * 5;
    var ticks = []; for (var k = 0; k <= top; k += 5) ticks.push(k);
    C.columns(byId("q4-chart"), {
      aria: "Column chart of median days on market by listing month. " + f["q4.fastestNames"] + " are fastest at " + f["q4.fastest"] + "; " + f["q4.slowestName"] + " is slowest at " + f["q4.slowest"] + ".",
      max: top, ticks: ticks,
      rows: months.map(function (r) {
        var ext = r.median_dom === minDom || r.median_dom === maxDom;
        return { label: MONTHS[r.month - 1], value: r.median_dom, display: num(r.median_dom),
          cls: ext ? "hl" : "", showValue: ext,
          tip: [[r.name + " listings"], [days(r.median_dom), "median"], [int(r.n), "sales"]] };
      })
    });
    table(byId("q4-table"), [
      { head: "Month listed", get: function (r) { return r.name; } },
      { head: "Sales with both dates", get: function (r) { return int(r.n); } },
      { head: "Median days on market", get: function (r) { return num(r.median_dom); } }
    ], months);

    // Question 5: assessment ratio, lowest first
    C.hbar(byId("q5-chart"), {
      aria: "Bar chart of the median ratio of assessed value to sale price by campus area. " + f["q5.far"] + " are far below 1; the rest are between " + f["q5.restMin"] + " and " + f["q5.restMax"] + " of the sale price.",
      max: 1.0, refLine: { value: 1, label: "1.00 = assessed at sale price" },
      rows: d.q5.map(function (r) {
        return { label: r.campus, value: r.median_ratio, display: r.median_ratio.toFixed(2), cls: r.median_ratio < 0.5 ? "hl" : "",
          tip: [[r.campus + ", " + r.state], [r.median_ratio.toFixed(3), "median ratio"], [int(r.n), "sales"]] };
      })
    });
    table(byId("q5-table"), [
      { head: "Campus area", get: areaName },
      { head: "State", get: function (r) { return r.state; } },
      { head: "Sales used", get: function (r) { return int(r.n); } },
      { head: "Median assessed / sale price", get: function (r) { return r.median_ratio.toFixed(3); } }
    ], d.q5);

    // Question 6: dumbbell for areas with at least 20 sales at repeated addresses, plus all areas
    var q6 = d.q6;
    var shown = q6.rows.filter(function (r) { return r.median_miles_multi != null; });
    var dots = [{ campus: "All areas", sales: q6.total.sales, median_miles_multi: q6.total.median_miles_multi, median_miles_other: q6.total.median_miles_other }].concat(shown);
    var maxMi = Math.ceil(Math.max.apply(null, dots.map(function (r) { return Math.max(r.median_miles_multi, r.median_miles_other); })) / 2) * 2;
    var miTicks = []; for (var m = 0; m <= maxMi; m += 2) miTicks.push(m);
    C.dumbbell(byId("q6-chart"), {
      aria: "Dot chart comparing median distance from campus for repeated addresses and other sales: all areas " + f["q6.multi"] + " against " + f["q6.other"] + " miles; " + f["q6.big0Name"] + " " + f["q6.nearMulti"] + " against " + f["q6.nearOther"] + ".",
      max: maxMi, ticks: miTicks, aName: "other sales", bName: "repeated addresses",
      rows: dots.map(function (r) {
        return { label: r.campus, a: r.median_miles_other, b: r.median_miles_multi, adisp: mi(r.median_miles_other) + " mi", bdisp: mi(r.median_miles_multi) + " mi",
          tip: [[r.campus], [mi(r.median_miles_multi) + " mi", "repeated addresses (" + r.sales + " sales)"], [mi(r.median_miles_other) + " mi", "all other sales"]] };
      })
    });
    table(byId("q6-table"), [
      { head: "Campus area", get: areaName },
      { head: "Addresses with 2+ sales", get: function (r) { return r.addresses; } },
      { head: "Sales at those addresses", get: function (r) { return r.sales; } },
      { head: "Median miles, those sales", get: function (r) { return r.sales === 0 ? "No sales" : r.median_miles_multi == null ? SMALL : mi(r.median_miles_multi); } },
      { head: "Median miles, other sales", get: function (r) { return mi(r.median_miles_other); } }
    ], q6.rows,
    ["All areas", String(q6.total.addresses), String(q6.total.sales), mi(q6.total.median_miles_multi), mi(q6.total.median_miles_other)]);
  }

  fetch("data/answers.json")
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(render)
    .catch(function (err) {
      document.querySelectorAll(".loading").forEach(function (p) {
        p.textContent = "The data file didn't load (" + err.message + "). Open this page through a web server, not straight from the file.";
      });
      if (window.console) console.error(err);
    });
})();
