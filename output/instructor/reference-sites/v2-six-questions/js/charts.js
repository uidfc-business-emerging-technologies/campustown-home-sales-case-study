/* Small SVG chart helpers, written for this site. No libraries.
   Colors come from CSS classes, so the charts follow the page's light and dark themes. */
(function () {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";

  function el(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    if (attrs) for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }

  function txt(parent, x, y, str, cls, anchor) {
    var t = el("text", { x: x, y: y, "class": cls || "lbl", "text-anchor": anchor || "start" }, parent);
    t.textContent = str;
    return t;
  }

  // Text width, measured with the page's chart font.
  var canvas = document.createElement("canvas").getContext("2d");
  function measure(str, size, weight) {
    var family = getComputedStyle(document.body).fontFamily;
    canvas.font = (weight || 400) + " " + (size || 12) + "px " + family;
    return canvas.measureText(str).width;
  }

  // Bar shapes: square at the baseline, 4px rounded data end.
  function hBarPath(x, y, w, h) {
    var r = Math.min(4, w, h / 2);
    if (w <= 0) return "";
    return "M" + x + "," + y + "H" + (x + w - r) + "Q" + (x + w) + "," + y + " " + (x + w) + "," + (y + r) +
      "V" + (y + h - r) + "Q" + (x + w) + "," + (y + h) + " " + (x + w - r) + "," + (y + h) + "H" + x + "Z";
  }
  function vBarPath(x, base, w, h) {
    var r = Math.min(4, h, w / 2), top = base - h;
    if (h <= 0) return "";
    return "M" + x + "," + base + "V" + (top + r) + "Q" + x + "," + top + " " + (x + r) + "," + top +
      "H" + (x + w - r) + "Q" + (x + w) + "," + top + " " + (x + w) + "," + (top + r) + "V" + base + "Z";
  }

  // One tooltip for the page. Lines are [value, label] pairs; text only, never HTML.
  var tip = null, tipTarget = null;
  function tipShow(target, lines) {
    tipTarget = target;
    if (!tip) {
      tip = document.createElement("div");
      tip.className = "tip";
      tip.setAttribute("role", "status");
      document.body.appendChild(tip);
    }
    tip.textContent = "";
    lines.forEach(function (ln, i) {
      var row = document.createElement("div");
      row.className = i === 0 ? "tip-title" : "tip-row";
      if (ln[0] !== undefined && ln[0] !== null) {
        var v = document.createElement("strong");
        v.textContent = ln[0];
        row.appendChild(v);
      }
      if (ln[1]) {
        var l = document.createElement("span");
        l.textContent = (ln[0] !== undefined && ln[0] !== null ? " " : "") + ln[1];
        row.appendChild(l);
      }
      tip.appendChild(row);
    });
    tip.hidden = false;
    tipPlace();
  }
  function tipPlace() {
    var r = tipTarget.getBoundingClientRect();
    var tw = tip.offsetWidth, th = tip.offsetHeight;
    var x = Math.min(Math.max(8, r.left + r.width / 2 - tw / 2), window.innerWidth - tw - 8);
    var y = r.top - th - 8;
    if (y < 8) y = r.bottom + 8;
    tip.style.left = x + "px";
    tip.style.top = y + "px";
  }
  function tipHide() { if (tip) tip.hidden = true; tipTarget = null; }
  // Scrolling hides a hover tooltip, but one opened by keyboard focus follows its mark
  // (focusing a mark can itself scroll the page).
  window.addEventListener("scroll", function () {
    if (tip && !tip.hidden && tipTarget && document.activeElement === tipTarget) tipPlace();
    else tipHide();
  }, { passive: true });

  function interactive(g, label, lines) {
    g.setAttribute("tabindex", "0");
    g.setAttribute("aria-label", label);
    g.classList.add("hit");
    var show = function () { g.classList.add("is-hover"); tipShow(g, lines); };
    var hide = function () { g.classList.remove("is-hover"); tipHide(); };
    g.addEventListener("pointerenter", show);
    g.addEventListener("pointerleave", hide);
    g.addEventListener("focus", show);
    g.addEventListener("blur", hide);
  }

  // Re-draw when the container's width changes.
  // One observer per container; calling again replaces the drawing function and redraws now.
  function responsive(container, draw) {
    container._draw = draw;
    container._lastW = 0;
    function run() {
      var w = Math.floor(container.clientWidth);
      if (w && w !== container._lastW) { container._lastW = w; container.textContent = ""; container._draw(w); }
    }
    run();
    if (!container._observed) {
      container._observed = true;
      if (window.ResizeObserver) new ResizeObserver(function () { requestAnimationFrame(run); }).observe(container);
      else window.addEventListener("resize", run);
    }
  }

  function svgRoot(container, width, height, aria) {
    var svg = el("svg", { width: width, height: height, viewBox: "0 0 " + width + " " + height, role: "img", "aria-label": aria }, container);
    return svg;
  }

  /* Horizontal bars. rows: [{label, value, display, cls, tip}] */
  function hbar(container, o) {
    responsive(container, function (width) {
      var rowH = 30, barH = 16, top = o.refLine ? 22 : 4;
      var labelW = Math.min(Math.max.apply(null, o.rows.map(function (r) { return measure(r.label, 13); })) + 14, width * 0.4);
      var valueW = Math.max.apply(null, o.rows.map(function (r) { return measure(r.display, 12, 600); })) + 10;
      var plotW = Math.max(40, width - labelW - valueW - 4);
      var max = o.max || Math.max.apply(null, o.rows.map(function (r) { return r.value; }));
      if (o.refLine) max = Math.max(max, o.refLine.value);
      var x = function (v) { return labelW + (v / max) * plotW; };
      var h = top + o.rows.length * rowH + 4;
      var svg = svgRoot(container, width, h, o.aria);
      el("line", { x1: labelW, x2: labelW, y1: top - 2, y2: h - 2, "class": "axis" }, svg);
      if (o.refLine) {
        var rx = x(o.refLine.value);
        el("line", { x1: rx, x2: rx, y1: top - 4, y2: h - 2, "class": "ref" }, svg);
        txt(svg, rx, 12, o.refLine.label, "ref-lbl", rx > width - 120 ? "end" : "middle");
      }
      o.rows.forEach(function (r, i) {
        var y = top + i * rowH + (rowH - barH) / 2;
        var g = el("g", {}, svg);
        el("rect", { x: 0, y: top + i * rowH, width: width, height: rowH, "class": "row-hit" }, g);
        txt(g, labelW - 10, y + barH / 2 + 4, r.label, "lbl" + (r.cls === "hl" ? " lbl-strong" : ""), "end");
        if (r.value != null) {
          el("path", { d: hBarPath(labelW, y, x(r.value) - labelW, barH), "class": "bar " + (r.cls || "") }, g);
          var vx = o.refLine ? Math.max(x(r.value), x(o.refLine.value)) : x(r.value);
          txt(g, vx + 6, y + barH / 2 + 4, r.display, "val");
        } else {
          txt(g, labelW + 6, y + barH / 2 + 4, r.display, "val muted");
        }
        interactive(g, r.label + ": " + r.display, r.tip || [[r.display, r.label]]);
        if (o.onPick) {
          g.classList.add("pickable");
          g.setAttribute("role", "button");
          g.addEventListener("click", function () { o.onPick(r); });
          g.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); o.onPick(r); } });
        }
      });
    });
  }

  /* Vertical columns. rows: [{label, value, display, cls, tip, showValue}] */
  function columns(container, o) {
    responsive(container, function (width) {
      var padL = 34, padR = 6, padT = 22, axisH = 26, plotH = o.height || 200;
      var h = padT + plotH + axisH;
      var svg = svgRoot(container, width, h, o.aria);
      var max = o.max;
      var y = function (v) { return padT + plotH - (v / max) * plotH; };
      (o.ticks || []).forEach(function (t) {
        el("line", { x1: padL, x2: width - padR, y1: y(t), y2: y(t), "class": t === 0 ? "axis" : "grid" }, svg);
        txt(svg, padL - 6, y(t) + 4, String(t), "tick", "end");
      });
      var band = (width - padL - padR) / o.rows.length;
      var w = Math.min(24, band * 0.62);
      o.rows.forEach(function (r, i) {
        var cx = padL + band * i + band / 2;
        var g = el("g", {}, svg);
        el("rect", { x: cx - band / 2, y: padT, width: band, height: plotH, "class": "row-hit" }, g);
        el("path", { d: vBarPath(cx - w / 2, y(0), w, y(0) - y(r.value)), "class": "bar " + (r.cls || "") }, g);
        if (r.showValue) txt(g, cx, y(r.value) - 6, r.display, "val", "middle");
        txt(g, cx, padT + plotH + 17, r.label, "tick", "middle");
        interactive(g, r.label + ": " + r.display, r.tip || [[r.display, r.label]]);
      });
    });
  }

  /* Rank slope chart. rows: [{label, l, r, ldisp, rdisp, cls}] where l and r are ranks (1 = top). */
  function slope(container, o) {
    responsive(container, function (width) {
      var n = o.rows.length, rowH = 26, padT = 34;
      var full = Math.max.apply(null, o.rows.map(function (r) { return measure(r.label + "  " + r.ldisp, 13, 600); })) + 14;
      var compact = full > width * 0.38;   // on narrow screens, names only (values stay in the tooltip and table)
      var sideW = compact ? Math.max.apply(null, o.rows.map(function (r) { return measure(r.label, 13, 600); })) + 14 : full;
      var xL = sideW, xR = width - sideW;
      var h = padT + n * rowH;
      var svg = svgRoot(container, width, h, o.aria);
      var y = function (rank) { return padT + (rank - 1) * rowH + rowH / 2; };
      txt(svg, compact ? 0 : xL, 14, o.ltitle, "col-head", compact ? "start" : "end");
      txt(svg, compact ? width : xR, 14, o.rtitle, "col-head", compact ? "end" : "start");
      el("line", { x1: xL, x2: xL, y1: padT - 6, y2: h - 4, "class": "axis" }, svg);
      el("line", { x1: xR, x2: xR, y1: padT - 6, y2: h - 4, "class": "axis" }, svg);
      // Draw unchanged rows first so changed ones sit on top.
      var ordered = o.rows.slice().sort(function (a, b) { return (a.cls === "hl") - (b.cls === "hl"); });
      ordered.forEach(function (r) {
        var g = el("g", {}, svg);
        var y1 = y(r.l), y2 = y(r.r);
        el("rect", { x: 0, y: Math.min(y1, y2) - rowH / 2, width: width, height: Math.abs(y2 - y1) + rowH, "class": "row-hit" }, g);
        el("line", { x1: xL, y1: y1, x2: xR, y2: y2, "class": "slope " + (r.cls || "") }, g);
        el("circle", { cx: xL, cy: y1, r: 4.5, "class": "dot " + (r.cls || "") }, g);
        el("circle", { cx: xR, cy: y2, r: 4.5, "class": "dot " + (r.cls || "") }, g);
        var lt = txt(g, xL - 10, y1 + 4, "", "lbl", "end");
        var a = el("tspan", { "class": r.cls === "hl" ? "lbl-strong" : "" }, lt); a.textContent = r.label + "  ";
        if (!compact) { var b = el("tspan", { "class": "val" }, lt); b.textContent = r.ldisp; }
        var rt = txt(g, xR + 10, y2 + 4, "", "lbl", "start");
        if (!compact) { var c = el("tspan", { "class": "val" }, rt); c.textContent = r.rdisp + "  "; }
        var d = el("tspan", { "class": r.cls === "hl" ? "lbl-strong" : "" }, rt); d.textContent = r.label;
        interactive(g, r.label + ": rank " + r.l + " by " + o.ltitle + ", rank " + r.r + " by " + o.rtitle,
          [[r.label], ["#" + r.l, o.ltitle + " (" + r.ldisp + ")"], ["#" + r.r, o.rtitle + " (" + r.rdisp + ")"]]);
      });
    });
  }

  /* Dumbbell: two values per row on one axis. rows: [{label, a, b, adisp, bdisp, tip}] */
  function dumbbell(container, o) {
    responsive(container, function (width) {
      var rowH = 30, padT = 6, axisH = 24;
      var labelW = Math.min(Math.max.apply(null, o.rows.map(function (r) { return measure(r.label, 13); })) + 14, width * 0.36);
      var padR = 16, plotW = width - labelW - padR;
      var x = function (v) { return labelW + (v / o.max) * plotW; };
      var h = padT + o.rows.length * rowH + axisH;
      var svg = svgRoot(container, width, h, o.aria);
      o.ticks.forEach(function (t) {
        el("line", { x1: x(t), x2: x(t), y1: padT, y2: h - axisH, "class": t === 0 ? "axis" : "grid" }, svg);
        txt(svg, x(t), h - axisH + 16, t + (t === o.ticks[o.ticks.length - 1] ? " mi" : ""), "tick", "middle");
      });
      o.rows.forEach(function (r, i) {
        var cy = padT + i * rowH + rowH / 2;
        var g = el("g", {}, svg);
        el("rect", { x: 0, y: padT + i * rowH, width: width, height: rowH, "class": "row-hit" }, g);
        txt(g, labelW - 10, cy + 4, r.label, "lbl", "end");
        el("line", { x1: x(r.a), x2: x(r.b), y1: cy, y2: cy, "class": "connector" }, g);
        el("circle", { cx: x(r.a), cy: cy, r: 5, "class": "dot s1" }, g);
        el("circle", { cx: x(r.b), cy: cy, r: 5, "class": "dot s2" }, g);
        interactive(g, r.label + ": " + o.aName + " " + r.adisp + ", " + o.bName + " " + r.bdisp, r.tip);
      });
    });
  }

  window.Charts = { hbar: hbar, columns: columns, slope: slope, dumbbell: dumbbell, el: el, txt: txt,
    tipShow: tipShow, tipHide: tipHide, interactive: interactive, responsive: responsive, measure: measure };
})();
