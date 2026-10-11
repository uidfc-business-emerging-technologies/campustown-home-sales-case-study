/* Close to Campus: filters a year of sales by campus, budget and distance, then draws
   the headline numbers, the dot map, the campus comparison and the table. */
(function () {
  "use strict";
  var C = window.Charts;
  var MIN_GROUP = 20;

  var money = function (v) { return "$" + Math.round(v).toLocaleString("en-US"); };
  var int = function (v) { return Math.round(v).toLocaleString("en-US"); };
  var pct = function (v) { return Math.round(v * 100) + "%"; };
  var byId = function (id) { return document.getElementById(id); };

  function median(arr) {
    if (!arr.length) return null;
    var s = arr.slice().sort(function (a, b) { return a - b; });
    var m = Math.floor(s.length / 2);
    return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
  }

  var D = null;          // the data file
  var byCampus = [];     // row indexes for each campus
  var state = { campus: 0, budget: 400000, dist: 3 };

  // Figures for one campus at the current budget and distance.
  function summarize(ci) {
    var S = D.sales, rows = byCampus[ci];
    var near = 0, inBudget = 0, sqft = [], beds = [], dom = [], domMissing = 0;
    for (var k = 0; k < rows.length; k++) {
      var i = rows[k];
      if (S.miles[i] > state.dist) continue;
      near++;
      if (S.price[i] > state.budget) continue;
      inBudget++;
      if (S.sqft[i] != null) sqft.push(S.sqft[i]);
      if (S.beds[i] != null) beds.push(S.beds[i]);
      if (S.dom[i] != null) dom.push(S.dom[i]); else domMissing++;
    }
    return {
      ci: ci, near: near, inBudget: inBudget, share: near ? inBudget / near : null,
      sqft: sqft.length >= MIN_GROUP ? median(sqft) : null,
      beds: beds.length >= MIN_GROUP ? median(beds) : null,
      dom: dom.length >= MIN_GROUP ? median(dom) : null,
      domMissing: inBudget ? domMissing / inBudget : null
    };
  }

  function setText(id, s) { byId(id).textContent = s; }

  function renderStats(sum, camp) {
    var dist = state.dist + (state.dist === 1 ? " mile" : " miles");
    setText("s1-k", "Homes sold within " + dist + " at or under " + money(state.budget));
    if (sum.near === 0) {
      setText("s1-v", "None"); byId("s1-v").className = "v small";
      setText("s1-d", "No homes sold within " + dist + " of " + camp.landmark + " in the past 12 months.");
    } else {
      setText("s1-v", pct(sum.share)); byId("s1-v").className = "v";
      setText("s1-d", int(sum.inBudget) + " of the " + int(sum.near) + " homes sold within " + dist + " of " + camp.landmark + " in the past 12 months.");
    }
    setText("s2-k", "Median size of those homes");
    if (sum.sqft == null) {
      setText("s2-v", "Too few sales"); byId("s2-v").className = "v small";
      setText("s2-d", "Fewer than 20 homes in budget, so no median is shown. Try a larger budget or distance.");
    } else {
      setText("s2-v", int(sum.sqft) + " sq ft"); byId("s2-v").className = "v";
      setText("s2-d", "Median of " + (sum.beds == null ? "?" : sum.beds) + " bedrooms. Half the homes in budget are larger, half smaller.");
    }
    setText("s3-k", "Median days to go under contract");
    if (sum.dom == null) {
      setText("s3-v", "Too few sales"); byId("s3-v").className = "v small";
      setText("s3-d", "Fewer than 20 homes in budget have both a listing and a contract date.");
    } else {
      setText("s3-v", sum.dom + (sum.dom === 1 ? " day" : " days")); byId("s3-v").className = "v";
      setText("s3-d", "From listing to accepted offer, for homes in budget. " + pct(sum.domMissing) + " of them had no listing or contract date and are not counted.");
    }
  }

  // Dot map of one campus area: sales placed by latitude and longitude around the landmark.
  function renderMap(camp) {
    var box = byId("map"), S = D.sales, rows = byCampus[state.campus];
    var R = Math.min(15, Math.max(2.5, state.dist * 1.6));   // miles from the landmark to the edge
    C.responsive(box, function (width) {
      var h = Math.round(Math.min(width, 520));
      var svg = C.el("svg", { width: width, height: h, viewBox: "0 0 " + width + " " + h, role: "img",
        "aria-label": "Map of home sales around " + camp.landmark + ", " + camp.town + ". Blue dots are at or under budget, gray dots are over budget. The ring marks " + state.dist + " miles." }, box);
      C.el("rect", { x: 0, y: 0, width: width, height: h, rx: 8, "class": "map-frame" }, svg);
      var cx = width / 2, cy = h / 2, scale = (Math.min(width, h) / 2 - 14) / R;
      var kx = 69.17 * Math.cos(camp.lat * Math.PI / 180), ky = 69.0;
      var px = function (lon) { return cx + (lon - camp.lon) * kx * scale; };
      var py = function (lat) { return cy - (lat - camp.lat) * ky * scale; };
      var pts = [], hidden = 0;
      var layers = { far: C.el("g", {}, svg), over: C.el("g", {}, svg), inb: C.el("g", {}, svg) };
      rows.forEach(function (i) {
        var x = px(S.lon[i]), y = py(S.lat[i]);
        if (x < 4 || x > width - 4 || y < 4 || y > h - 4) { hidden++; return; }
        var near = S.miles[i] <= state.dist, ok = S.price[i] <= state.budget;
        var cls = !near ? "pt-far" : ok ? "pt-in" : "pt-over";
        var layer = !near ? layers.far : ok ? layers.inb : layers.over;
        C.el("circle", { cx: x.toFixed(1), cy: y.toFixed(1), r: 3, "class": cls }, layer);
        pts.push([x, y, i]);
      });
      var ringR = state.dist * scale;
      C.el("circle", { cx: cx, cy: cy, r: ringR, "class": "ring" }, svg);
      C.txt(svg, cx, cy - ringR - 6, state.dist + " mi", "ring-lbl", "middle");
      C.el("rect", { x: cx - 5, y: cy - 5, width: 10, height: 10, rx: 1.5, "class": "landmark" }, svg);
      C.txt(svg, cx + 10, cy + 18, camp.landmark, "landmark-lbl", "start");
      // Scale bar: 1 mile
      var sb = scale, sx = 14, sy = h - 14;
      C.el("line", { x1: sx, x2: sx + sb, y1: sy, y2: sy, "class": "axis", "stroke-width": 2 }, svg);
      C.txt(svg, sx + sb + 6, sy + 4, "1 mile", "scale-lbl");
      // Hover: nearest sale within 14px.
      var hover = C.el("circle", { r: 6, "class": "pt-hover", visibility: "hidden" }, svg);
      var anchor = C.el("rect", { width: 1, height: 1, fill: "transparent" }, svg);
      svg.addEventListener("pointermove", function (e) {
        var rect = svg.getBoundingClientRect();
        var mx = e.clientX - rect.left, my = e.clientY - rect.top, best = null, bd = 196;
        for (var k = 0; k < pts.length; k++) {
          var dx = pts[k][0] - mx, dy = pts[k][1] - my, d2 = dx * dx + dy * dy;
          if (d2 < bd) { bd = d2; best = pts[k]; }
        }
        if (!best) { hover.setAttribute("visibility", "hidden"); C.tipHide(); return; }
        var i = best[2];
        hover.setAttribute("cx", best[0]); hover.setAttribute("cy", best[1]); hover.setAttribute("visibility", "visible");
        anchor.setAttribute("x", best[0]); anchor.setAttribute("y", best[1]);
        var lines = [[money(S.price[i]), S.price[i] <= state.budget ? "(at or under budget)" : "(over budget)"]];
        lines.push([S.sqft[i] != null ? int(S.sqft[i]) + " sq ft" : "Size not reported", S.beds[i] != null ? S.beds[i] + " bedrooms" : ""]);
        lines.push([S.miles[i].toFixed(1) + " mi", "from " + camp.landmark]);
        if (S.dom[i] != null) lines.push([S.dom[i] + " days", "to go under contract"]);
        C.tipShow(anchor, lines);
      });
      svg.addEventListener("pointerleave", function () { hover.setAttribute("visibility", "hidden"); C.tipHide(); });
      var note = hidden ? int(hidden) + " sales more than about " + R.toFixed(0) + " miles out are outside the map." : "";
      setText("map-note", note);
    });
    setText("map-sub", "Each dot is one sale near " + camp.landmark + " (" + camp.town + ") in the past 12 months, placed by its latitude and longitude. Faded dots are farther out than " + state.dist + (state.dist === 1 ? " mile." : " miles."));
  }

  function renderBars(sums) {
    var rows = sums.filter(function (s) { return s.near > 0; })
      .sort(function (a, b) { return b.share - a.share; })
      .map(function (s) {
        var c = D.campuses[s.ci];
        return { label: c.short, value: s.share, display: pct(s.share), cls: s.ci === state.campus ? "hl" : "", ci: s.ci,
          tip: [[c.short + " (" + c.town + ")"], [pct(s.share), "at or under budget"], [int(s.inBudget) + " of " + int(s.near), "homes sold within " + state.dist + " mi"]] };
      });
    C.hbar(byId("bars"), {
      aria: "Bar chart of the share of homes sold within " + state.dist + " miles of campus that were at or under " + money(state.budget) + ", by campus area.",
      max: 1, rows: rows,
      onPick: function (r) { state.campus = r.ci; byId("campus").value = String(r.ci); update(); }
    });
    var missing = sums.filter(function (s) { return s.near === 0; }).map(function (s) { return D.campuses[s.ci].short; });
    setText("bars-sub", "Share of homes sold within " + state.dist + (state.dist === 1 ? " mile" : " miles") + " of campus that were at or under " + money(state.budget) + ". Orange marks the campus area you picked; select another bar to switch." + (missing.length ? " No sales that close: " + missing.join(", ") + "." : ""));
  }

  function renderTable(sums) {
    var holder = byId("table");
    holder.textContent = "";
    setText("table-sub", "Budget " + money(state.budget) + ", within " + state.dist + (state.dist === 1 ? " mile" : " miles") + " of each campus landmark. Sorted by share in budget.");
    var t = document.createElement("table");
    var head = ["Campus area", "Homes sold nearby", "At or under budget", "Share in budget", "Median size (sq ft)", "Median bedrooms", "Median days on market"];
    var hr = t.createTHead().insertRow();
    head.forEach(function (h) { var th = document.createElement("th"); th.scope = "col"; th.textContent = h; hr.appendChild(th); });
    var tb = t.createTBody();
    sums.slice().sort(function (a, b) { return (b.share || 0) - (a.share || 0); }).forEach(function (s) {
      var c = D.campuses[s.ci], tr = tb.insertRow();
      if (s.ci === state.campus) tr.className = "sel";
      var th = document.createElement("th"); th.scope = "row"; th.textContent = c.short + " (" + c.town + ")"; tr.appendChild(th);
      var cells = [int(s.near), int(s.inBudget), s.near ? pct(s.share) : "No sales",
        s.sqft == null ? "Too few" : int(s.sqft), s.beds == null ? "Too few" : String(s.beds), s.dom == null ? "Too few" : String(s.dom)];
      cells.forEach(function (v) { var td = tr.insertCell(); td.textContent = v; if (v === "Too few" || v === "No sales") td.className = "na"; });
    });
    holder.appendChild(t);
  }

  function update() {
    var camp = D.campuses[state.campus];
    var sums = D.campuses.map(function (_c, ci) { return summarize(ci); });
    byId("budget-out").textContent = money(state.budget);
    renderStats(sums[state.campus], camp);
    renderMap(camp);
    renderBars(sums);
    renderTable(sums);
  }

  function longDate(iso) {
    var p = iso.split("-").map(Number);
    return new Date(Date.UTC(p[0], p[1] - 1, p[2])).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric", timeZone: "UTC" });
  }

  // The figures quoted in the introduction and the data notes, from the data file.
  function fillFacts() {
    var f = {
      count: int(D.sales_count),
      window: longDate(D.window[0]) + " to " + longDate(D.window[1]),
      quarters: String(D.full_quarters),
      qLow: money(D.quarterly_median_range[0]),
      qHigh: money(D.quarterly_median_range[1]),
      excluded: int(D.excluded_under_min_price),
      minPrice: money(D.rules.min_price),
      lowest: money(D.lowest_excluded_price),
      doubles: int(D.likely_double_records)
    };
    document.querySelectorAll("[data-fact]").forEach(function (el) {
      var v = f[el.getAttribute("data-fact")];
      if (v === undefined) throw new Error("No value for " + el.getAttribute("data-fact"));
      el.textContent = v;
    });
  }

  function start(data) {
    D = data;
    fillFacts();
    D.campuses.forEach(function () { byCampus.push([]); });
    D.sales.campus.forEach(function (ci, i) { byCampus[ci].push(i); });
    var sel = byId("campus");
    D.campuses.forEach(function (c, i) {
      var o = document.createElement("option");
      o.value = String(i); o.textContent = c.short + " (" + c.town + ")";
      sel.appendChild(o);
    });
    sel.value = String(state.campus);
    sel.addEventListener("change", function () { state.campus = Number(sel.value); update(); });
    byId("budget").addEventListener("input", function (e) { state.budget = Number(e.target.value); update(); });
    document.querySelectorAll('input[name="dist"]').forEach(function (r) {
      r.addEventListener("change", function () { state.dist = Number(r.value); update(); });
    });
    byId("controls").addEventListener("submit", function (e) { e.preventDefault(); });
    // Pick up values the browser restored (for example after going back).
    state.budget = Number(byId("budget").value);
    var checked = document.querySelector('input[name="dist"]:checked');
    if (checked) state.dist = Number(checked.value);
    update();
  }

  fetch("data/sales.json")
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(start)
    .catch(function (err) {
      setText("s1-d", "The data file didn't load (" + err.message + "). Open this page through a web server, not straight from the file.");
      if (window.console) console.error(err);
    });
})();
