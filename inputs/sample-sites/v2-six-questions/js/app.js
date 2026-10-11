/* Builds the charts and tables from data/answers.json (made by scripts/build_data.py). */
(function () {
  "use strict";
  var C = window.Charts;

  var money = function (v) { return "$" + Math.round(v).toLocaleString("en-US"); };
  var money2 = function (v) { return "$" + v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); };
  var int = function (v) { return Math.round(v).toLocaleString("en-US"); };
  var pct = function (v) { return Math.round(v * 100) + "%"; };
  var days = function (v) { return (v % 1 ? v.toFixed(1) : String(v)) + (v === 1 ? " day" : " days"); };
  var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  var MONTHS_LONG = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

  // Build a table with text nodes only. cols: [{head, get, cls}]
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

  function byId(id) { return document.getElementById(id); }

  function render(d) {
    var full = {};
    d.campuses.forEach(function (c) { full[c.short] = c; });
    var areaName = function (r) { return r.campus + " (" + full[r.campus].town + ")"; };

    // Question 1: rank slope chart
    var changed = function (r) { return r.rank_price !== r.rank_pps; };
    C.slope(byId("q1-chart"), {
      aria: "Slope chart comparing each campus area's rank by median sale price with its rank by median price per square foot. Only Florida and Georgia change rank.",
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
    ], d.q1.slice().sort(function (a, b) { return a.rank_price - b.rank_price; }));

    // Question 2: two aligned bar charts
    var q2 = d.q2.slice().sort(function (a, b) { return a.median_dom - b.median_dom || a.campus.localeCompare(b.campus); });
    C.hbar(byId("q2-chart-a"), {
      aria: "Bar chart of median days on market by campus area, from 7 days to 27 days.",
      rows: q2.map(function (r) {
        return { label: r.campus, value: r.median_dom, display: days(r.median_dom),
          tip: [[r.campus], [days(r.median_dom), "median"], [int(r.dom_sales), "sales with both dates"]] };
      })
    });
    C.hbar(byId("q2-chart-b"), {
      aria: "Bar chart of the share of sales with no days on market, by campus area, from 16% to 35%.",
      max: 0.4,
      rows: q2.map(function (r) {
        return { label: r.campus, value: r.missing_share, display: pct(r.missing_share), cls: "dim",
          tip: [[r.campus], [pct(r.missing_share), "with no days on market"], [int(r.rows - r.dom_sales) + " of " + int(r.rows), "sales"]] };
      })
    });
    table(byId("q2-table"), [
      { head: "Campus area", get: areaName },
      { head: "All sales", get: function (r) { return int(r.rows); } },
      { head: "Sales with both dates", get: function (r) { return int(r.dom_sales); } },
      { head: "Median days on market", get: function (r) { return r.median_dom; } },
      { head: "Share with no days on market", get: function (r) { return (r.missing_share * 100).toFixed(1) + "%"; } }
    ], q2);

    // Question 3: heat table
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
    cap.style.position = "absolute"; cap.style.left = "-9999px"; t.appendChild(cap);
    var hr = t.createTHead().insertRow();
    ["Campus area"].concat(d.q3.bands).forEach(function (h) { var th = document.createElement("th"); th.scope = "col"; th.textContent = h; hr.appendChild(th); });
    var tb = t.createTBody();
    var addRow = function (label, cells, cls) {
      var tr = tb.insertRow(); if (cls) tr.className = cls;
      var th = document.createElement("th"); th.scope = "row"; th.textContent = label; th.style.fontWeight = cls ? "700" : "500"; tr.appendChild(th);
      cells.forEach(function (c, i) {
        var td = tr.insertCell();
        if (c.median_pps == null) {
          td.className = "cell none";
          td.textContent = c.n === 0 ? "No sales" : "Fewer than 20 sales";
          if (c.n > 0) { var sm = document.createElement("small"); sm.textContent = c.n + " sold"; td.appendChild(sm); }
        } else {
          td.className = "cell h" + binOf(c.median_pps);
          td.textContent = money(c.median_pps);
          var small = document.createElement("small"); small.textContent = int(c.n) + " sold"; td.appendChild(small);
        }
        td.setAttribute("aria-label", label + ", " + d.q3.bands[i] + ": " + (c.median_pps == null ? "fewer than 20 sales" : money2(c.median_pps) + " per sq ft, " + c.n + " sales"));
      });
    };
    d.q3.rows.forEach(function (r) { addRow(r.campus, r.cells); });
    addRow("All areas", d.q3.all, "all");
    holder.appendChild(t);

    // Question 4: columns by month
    var q4 = d.q4;
    var minDom = Math.min.apply(null, q4.map(function (r) { return r.median_dom; }));
    var maxDom = Math.max.apply(null, q4.map(function (r) { return r.median_dom; }));
    C.columns(byId("q4-chart"), {
      aria: "Column chart of median days on market by listing month. March to May are 7 days; December is 25 days.",
      max: 30, ticks: [0, 10, 20, 30],
      rows: q4.map(function (r) {
        var ext = r.median_dom === minDom || r.median_dom === maxDom;
        return { label: MONTHS[r.month - 1], value: r.median_dom, display: String(r.median_dom),
          cls: r.median_dom === maxDom ? "hl" : "", showValue: ext,
          tip: [[MONTHS_LONG[r.month - 1] + " listings"], [days(r.median_dom), "median"], [int(r.n), "sales"]] };
      })
    });
    table(byId("q4-table"), [
      { head: "Month listed", get: function (r) { return MONTHS_LONG[r.month - 1]; } },
      { head: "Sales with both dates", get: function (r) { return int(r.n); } },
      { head: "Median days on market", get: function (r) { return r.median_dom; } }
    ], q4);

    // Question 5: assessment ratio
    var q5 = d.q5.slice().sort(function (a, b) { return a.median_ratio - b.median_ratio; });
    C.hbar(byId("q5-chart"), {
      aria: "Bar chart of the median ratio of assessed value to sale price by campus area. Penn State is 0.18, Michigan 0.33, and the rest between 0.78 and 1.00.",
      max: 1.0, refLine: { value: 1, label: "1.00 = assessed at sale price" },
      rows: q5.map(function (r) {
        return { label: r.campus, value: r.median_ratio, display: r.median_ratio.toFixed(2), cls: r.median_ratio < 0.5 ? "hl" : "",
          tip: [[r.campus + ", " + r.state], [r.median_ratio.toFixed(3), "median ratio"], [int(r.n), "sales"]] };
      })
    });
    table(byId("q5-table"), [
      { head: "Campus area", get: areaName },
      { head: "State", get: function (r) { return r.state; } },
      { head: "Sales used", get: function (r) { return int(r.n); } },
      { head: "Median assessed / sale price", get: function (r) { return r.median_ratio.toFixed(3); } }
    ], q5);

    // Question 6: dumbbell of median miles
    var q6 = d.q6.filter(function (r) { return r.sales > 0; })
      .sort(function (a, b) { return b.sales - a.sales; });
    var mi = function (v) { return v.toFixed(1) + " mi"; };
    C.dumbbell(byId("q6-chart"), {
      aria: "Dot chart comparing median distance from campus for multi-sale addresses and other sales in each area.",
      max: 8, ticks: [0, 2, 4, 6, 8], aName: "other sales", bName: "multi-sale addresses",
      rows: q6.map(function (r) {
        return { label: r.campus, a: r.median_miles_other, b: r.median_miles_multi, adisp: mi(r.median_miles_other), bdisp: mi(r.median_miles_multi),
          tip: [[r.campus], [mi(r.median_miles_multi), "multi-sale addresses (" + r.sales + " sales)"], [mi(r.median_miles_other), "all other sales"]] };
      })
    });
    var miOrDash = function (v) { return v == null ? "None" : v.toFixed(1); };
    table(byId("q6-table"), [
      { head: "Campus area", get: areaName },
      { head: "Addresses with 2+ sales", get: function (r) { return r.addresses; } },
      { head: "Sales at those addresses", get: function (r) { return r.sales; } },
      { head: "Median miles, those sales", get: function (r) { return miOrDash(r.median_miles_multi); } },
      { head: "Median miles, other sales", get: function (r) { return miOrDash(r.median_miles_other); } }
    ], d.q6.slice().sort(function (a, b) { return b.sales - a.sales; }),
    ["All areas", String(d.q6_total.addresses), String(d.q6_total.sales), d.q6_total.median_miles_multi.toFixed(1), d.q6_total.median_miles_other.toFixed(1)]);
  }

  fetch("data/answers.json")
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(render)
    .catch(function (err) {
      document.querySelectorAll(".loading").forEach(function (p) {
        p.textContent = "The data file didn't load (" + err.message + "). Open this page through a web server, not straight from the file.";
      });
    });
})();
