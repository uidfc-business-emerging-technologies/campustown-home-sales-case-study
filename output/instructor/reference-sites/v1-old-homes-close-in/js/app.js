/* Old Homes, Close In: reads data/age.json (made by scripts/build_data.py) and draws the
   findings, the headline numbers, three charts and a table. A campus picker drives the
   numbers and the first two charts. No number on the page is typed by hand. */
(function () {
  "use strict";
  var C = window.Charts;
  var ALL = "All campus areas";

  var money = function (v) { return "$" + Math.round(v).toLocaleString("en-US"); };
  var int = function (v) { return Math.round(v).toLocaleString("en-US"); };
  var pct = function (v) { return Math.round(v * 100) + "%"; };
  var pct1 = function (v) { return (v * 100).toFixed(1) + "%"; };
  var decade = function (d) { return d + "s"; };
  var byId = function (id) { return document.getElementById(id); };
  function setText(id, s) { byId(id).textContent = s; }

  var D = null, current = ALL;

  // Highest and lowest decades by median price per square foot, among decades shown.
  function extremes(area) {
    var shown = D.areas[area].by_decade.filter(function (d) { return d.median_pps != null; });
    var hi = shown.reduce(function (a, b) { return b.median_pps > a.median_pps ? b : a; });
    var lo = shown.reduce(function (a, b) { return b.median_pps < a.median_pps ? b : a; });
    return { hi: hi, lo: lo, shown: shown };
  }

  // The farthest distance band that has a median, for "near against far" comparisons.
  function farthest(area) {
    var bands = D.areas[area].by_band;
    for (var i = bands.length - 1; i > 0; i--) if (bands[i].median_year != null) return { band: D.bands[i], value: bands[i].median_year };
    return null;
  }

  function fillFacts() {
    var all = D.areas[ALL], ex = extremes(ALL);
    var nearOldest = D.campuses.filter(function (c) {
      var b = D.areas[c.short].by_band, near = b[0].median_year;
      return near != null && b.every(function (x) { return x.median_year == null || x.median_year >= near; });
    }).length;
    var f = {
      rows: int(D.rows),
      nearYear: String(all.by_band[0].median_year),
      farYear: String(all.by_band[3].median_year),
      nearOldest: String(nearOldest),
      peakDecade: decade(ex.hi.decade), peakPps: money(ex.hi.median_pps),
      lowDecade: decade(ex.lo.decade), lowPps: money(ex.lo.median_pps),
      newDecadePps: money(all.by_decade[all.by_decade.length - 1].median_pps),
      newShare: pct1(all.new_share),
      newNoList: pct(D.listing.new_no_list_share), oldNoList: pct(D.listing.older_no_list_share),
      built1900: int(D.counts.built_1900), built1901: int(D.counts.built_1901),
      perYear: String(Math.round(D.counts.built_1902_1909_per_year)),
      yearMissing: D.counts.year_built_missing === 1 ? "One" : int(D.counts.year_built_missing),
      ppsSales: int(D.counts.pps_sales), presale: int(D.counts.sold_before_finished), datedSales: int(D.counts.dated_sales)
    };
    document.querySelectorAll("[data-fact]").forEach(function (el) {
      var v = f[el.getAttribute("data-fact")];
      if (v === undefined) throw new Error("No value for " + el.getAttribute("data-fact"));
      el.textContent = v;
    });
  }

  function renderStats() {
    var a = D.areas[current], near = a.by_band[0].median_year, far = farthest(current), ex = extremes(current);
    var where = current === ALL ? "all 11 campus areas" : current;
    if (near == null) {
      setText("s1-v", "Too few sales"); setText("s1-d", "Fewer than 20 sales under 1 mile from campus in " + where + ".");
    } else {
      setText("s1-v", String(near));
      setText("s1-d", "In " + where + ". Homes " + far.band.toLowerCase() + " from campus: " + far.value + ".");
    }
    setText("s2-v", decade(ex.hi.decade));
    setText("s2-d", "Homes built in the " + decade(ex.hi.decade) + ": " + money(ex.hi.median_pps) + " per sq ft. Lowest: the " + decade(ex.lo.decade) + ", at " + money(ex.lo.median_pps) + ".");
    setText("s3-v", pct1(a.new_share));
    setText("s3-d", int(a.new_homes) + " new homes. " + (a.new_no_list_share == null ? "Too few to say how many sold without a listing." : pct(a.new_no_list_share) + " of them sold without a listing on record."));
  }

  function renderBands() {
    var a = D.areas[current];
    var vals = a.by_band.map(function (b) { return b.median_year; }).filter(function (v) { return v != null; });
    var min = Math.floor((Math.min.apply(null, vals) - 5) / 20) * 20, max = Math.ceil((Math.max.apply(null, vals) + 5) / 20) * 20;
    var ticks = []; for (var t = min; t <= max; t += 20) ticks.push(t);
    C.dots(byId("c1"), {
      aria: "Dot plot of the median year built by distance from campus in " + current + ": " + a.by_band.map(function (b, i) { return D.bands[i] + " " + (b.median_year == null ? (b.n ? "fewer than 20 sales" : "no sales") : b.median_year); }).join("; ") + ".",
      min: min, max: max, ticks: ticks,
      rows: a.by_band.map(function (b, i) {
        var label = D.bands[i];
        if (b.median_year == null) return { label: label, value: null, display: b.n ? "Fewer than 20 sales" : "No sales", tip: [[label], [int(b.n), "sales"]] };
        return { label: label, value: b.median_year, display: String(b.median_year), tip: [[label], [String(b.median_year), "median year built"], [int(b.n), "sales"]] };
      })
    });
    setText("c1-sub", "Median year built of the homes sold in each distance band, " + (current === ALL ? "all 11 campus areas" : current) + ".");
  }

  function renderDecades() {
    var a = D.areas[current], ex = extremes(current);
    var top = Math.ceil(Math.max.apply(null, ex.shown.map(function (d) { return d.median_pps; })) / 100) * 100;
    var ticks = []; for (var t = 0; t <= top; t += 100) ticks.push(t);
    C.columns(byId("c2"), {
      aria: "Column chart of median price per square foot by decade built in " + current + ". Highest: the " + decade(ex.hi.decade) + " at " + money(ex.hi.median_pps) + ". Lowest: the " + decade(ex.lo.decade) + " at " + money(ex.lo.median_pps) + ".",
      max: top, ticks: ticks, height: 190,
      rows: a.by_decade.map(function (d) {
        var ext = d === ex.hi || d === ex.lo;
        // A full year at the start of each century, so 1900 and 2000 can't be confused.
        var short = d.decade % 100 === 0 ? String(d.decade) : "'" + String(d.decade).slice(2);
        return { label: short, value: d.median_pps == null ? 0 : d.median_pps, display: d.median_pps == null ? "too few" : money(d.median_pps),
          cls: ext ? "hl" : "", showValue: ext,
          tip: [[decade(d.decade)], d.median_pps == null ? ["Fewer than 20 sales", ""] : [money(d.median_pps), "per sq ft (median)"], [int(d.n), "sales"]] };
      })
    });
    setText("c2-sub", "Median price per square foot by decade built, " + (current === ALL ? "all 11 campus areas" : current) + ". The highest and lowest decades are in orange; decades with fewer than 20 sales have no bar.");
  }

  function renderNew() {
    var rows = D.campuses.map(function (c) { return { c: c, a: D.areas[c.short] }; })
      .sort(function (x, y) { return y.a.new_share - x.a.new_share; });
    C.hbar(byId("c3"), {
      aria: "Bar chart of the share of sales that were new homes, by campus area, from " + pct1(rows[rows.length - 1].a.new_share) + " to " + pct1(rows[0].a.new_share) + ".",
      rows: rows.map(function (r) {
        return { label: r.c.short, value: r.a.new_share, display: pct1(r.a.new_share), cls: r.c.short === current ? "hl" : "", area: r.c.short,
          tip: [[r.c.name], [pct1(r.a.new_share), "of sales were new homes"], [int(r.a.new_homes), "new homes"]] };
      }),
      onPick: function (r) { choose(r.area); }
    });
  }

  function renderTable() {
    var holder = byId("table");
    holder.textContent = "";
    var t = document.createElement("table");
    var head = ["Campus area", "Sales", "Median year built", "Under 1 mile", D.bands[3], "New homes", "New homes sold without a listing"];
    var hr = t.createTHead().insertRow();
    head.forEach(function (h) { var th = document.createElement("th"); th.scope = "col"; th.textContent = h; hr.appendChild(th); });
    var tb = t.createTBody();
    [{ short: ALL, name: ALL }].concat(D.campuses).forEach(function (c) {
      var a = D.areas[c.short], tr = tb.insertRow();
      if (c.short === current) tr.className = "sel";
      if (c.short === ALL) tr.className += " all";
      var th = document.createElement("th"); th.scope = "row"; th.textContent = c.short === ALL ? ALL : c.name; tr.appendChild(th);
      var yr = function (b) { return b.median_year == null ? (b.n ? "Too few" : "No sales") : String(b.median_year); };
      [int(a.rows), String(a.median_year), yr(a.by_band[0]), yr(a.by_band[3]), pct1(a.new_share),
        a.new_no_list_share == null ? "Too few" : pct(a.new_no_list_share)].forEach(function (v) {
        var td = tr.insertCell(); td.textContent = v; if (v === "Too few" || v === "No sales") td.className = "na";
      });
    });
    holder.appendChild(t);
  }

  function update() { renderStats(); renderBands(); renderDecades(); renderNew(); renderTable(); }
  function choose(area) { current = area; byId("area").value = area; update(); }

  function start(data) {
    D = data;
    fillFacts();
    var sel = byId("area");
    [ALL].concat(D.campuses.map(function (c) { return c.short; })).forEach(function (s) {
      var o = document.createElement("option");
      o.value = s;
      o.textContent = s === ALL ? ALL : D.campuses.filter(function (c) { return c.short === s; })[0].name;
      sel.appendChild(o);
    });
    sel.value = current;
    sel.addEventListener("change", function () { choose(sel.value); });
    byId("picker").addEventListener("submit", function (e) { e.preventDefault(); });
    if (sel.value !== current) current = sel.value;
    update();
  }

  fetch("data/age.json")
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(start)
    .catch(function (err) {
      setText("s1-d", "The data file didn't load (" + err.message + "). Open this page through a web server, not straight from the file.");
      document.querySelectorAll(".loading").forEach(function (p) { p.textContent = "The data file didn't load."; });
      if (window.console) console.error(err);
    });
})();
