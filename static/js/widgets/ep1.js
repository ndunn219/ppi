// EP1 Earthwork quantities: end areas, the prism between them, and how
// bank, loose and compacted volumes differ when cut is placed as fill.
(function () {
  "use strict";
  var PE = (typeof window !== "undefined" ? window : globalThis).PEWidgets;
  var BASE = 40; // ft, roadway width at the bottom of the cut, for drawing only
  var SLOPE = 2; // horizontal per vertical, for drawing only

  // Depth of a 2:1 trapezoidal cut with a 40-ft base that has area A.
  function depthFor(A) {
    if (A <= 0) return 0;
    return (-BASE + Math.sqrt(BASE * BASE + 4 * SLOPE * A)) / (2 * SLOPE);
  }

  // Corners of a section's cut, drawn with the vertical scale exaggerated
  // so shallow cuts stay readable.
  function corners(cx, top, A, sx, sy) {
    var d = depthFor(A);
    var halfTop = BASE / 2 + SLOPE * d;
    return {
      d: d,
      tl: [cx - halfTop * sx, top], tr: [cx + halfTop * sx, top],
      br: [cx + BASE / 2 * sx, top + d * sy], bl: [cx - BASE / 2 * sx, top + d * sy],
    };
  }

  function section(h, k, top, A, label) {
    var out = h.line(k.tl[0] - 30, top, k.tr[0] + 30, top, "w-thin");
    if (k.d > 0) {
      out += h.polygon([k.tl, k.tr, k.br, k.bl], "w-fill-amber");
      var mid = (k.tl[0] + k.tr[0]) / 2;
      var depthPx = k.bl[1] - top;
      out += h.text(mid, depthPx > 34 ? top + depthPx / 2 + 5 : k.bl[1] + 18, h.fmt(A, 0) + " ft²", { anchor: "middle", cls: "w-label-strong" });
    } else {
      out += h.text((k.tl[0] + k.tr[0]) / 2, top + 60, "No cut: A = 0", { anchor: "middle", cls: "w-label w-small" });
    }
    out += h.text((k.tl[0] + k.tr[0]) / 2, top - 10, label, { anchor: "middle", cls: "w-label-strong w-small" });
    return out;
  }

  PE.register("end-areas", {
    title: "Volume between two cross-sections",
    height: 300,
    params: [
      { key: "A1", label: "End area A₁", min: 0, max: 800, step: 10, value: 300, unit: "ft²" },
      { key: "A2", label: "End area A₂", min: 0, max: 800, step: 10, value: 500, unit: "ft²" },
      { key: "L", label: "Distance between sections L", min: 25, max: 200, step: 25, value: 100, unit: "ft" },
    ],
    compute: function (v) {
      var cf = v.L * (v.A1 + v.A2) / 2;
      var pyramid = (v.A1 === 0 || v.A2 === 0) ? v.L * Math.max(v.A1, v.A2) / 3 : null;
      return { cf: cf, cy: cf / 27, pyramid: pyramid, pyramidCy: pyramid === null ? null : pyramid / 27 };
    },
    outputs: function (v, c) {
      var f = PE.helpers.fmt;
      var out = [
        { label: "Average area", value: f((v.A1 + v.A2) / 2, 0) + " ft²" },
        { label: "Volume", value: f(c.cf, 0) + " ft³" },
        { label: "Volume ÷ 27", value: f(c.cy, 1) + " yd³", strong: true },
      ];
      if (c.pyramid !== null && c.pyramid > 0) out.push({ label: "Pyramid V = AL/3", value: f(c.pyramidCy, 1) + " yd³" });
      return out;
    },
    note: function (v, c) {
      var f = PE.helpers.fmt;
      if (v.A1 === 0 && v.A2 === 0) return "Both areas are zero, so there is no earthwork between these stations.";
      if (c.pyramid !== null) return "One end area is zero, so the true shape is closer to a pyramid. Average end area gives " + f(c.cy, 1) + " yd³ against " + f(c.pyramidCy, 1) + " yd³ for a pyramid: it overestimates here.";
      return "Average end area treats the earth between the sections as a prism with the mean of the two areas. It is exact only when the areas are equal.";
    },
    draw: function (v, c, h) {
      var maxD = depthFor(800);
      var sx = 220 / (BASE + 2 * SLOPE * maxD);
      var sy = 120 / maxD;
      var top = 80;
      var k1 = corners(165, top, v.A1, sx, sy), k2 = corners(475, top, v.A2, sx, sy);
      var out = "";
      // The solid between the sections: join matching corners.
      if (k1.d > 0 || k2.d > 0) {
        ["tl", "tr", "br", "bl"].forEach(function (key) {
          out += h.line(k1[key][0], k1[key][1], k2[key][0], k2[key][1], "w-dash");
        });
      }
      out += section(h, k1, top, v.A1, "Station 1: A₁");
      out += section(h, k2, top, v.A2, "Station 2: A₂");
      out += h.dim(165, 36, 475, 36, "L = " + h.fmt(v.L, 0) + " ft", { offset: -6 });
      out += h.text(320, 262, "V = L × (A₁ + A₂) / 2 = " + h.fmt(v.L, 0) + " × (" + h.fmt(v.A1, 0) + " + " + h.fmt(v.A2, 0) + ") / 2 = " + h.fmt(c.cf, 0) + " ft³", { anchor: "middle", cls: "w-label" });
      out += h.text(320, 284, "÷ 27 = " + h.fmt(c.cy, 1) + " yd³", { anchor: "middle", cls: "w-label-accent" });
      out += h.text(632, 296, "Depth exaggerated", { anchor: "end", cls: "w-label w-small" });
      return out;
    },
  });

  PE.register("borrow-balance", {
    title: "Cut, fill and borrow in bank, loose and compacted yards",
    height: 330,
    params: [
      { key: "Vc", label: "Usable cut (bank)", min: 0, max: 60000, step: 500, value: 20000, unit: "yd³" },
      { key: "Vf", label: "Fill needed (compacted)", min: 0, max: 60000, step: 500, value: 30000, unit: "yd³" },
      { key: "s", label: "Shrinkage", min: 0, max: 35, step: 1, value: 20, unit: "%" },
      { key: "w", label: "Swell (for hauling)", min: 0, max: 50, step: 1, value: 25, unit: "%" },
    ],
    compute: function (v) {
      var s = v.s / 100, w = v.w / 100;
      var placed = v.Vc * (1 - s); // compacted yards the cut makes
      var gap = v.Vf - placed;     // + shortfall, − surplus (compacted)
      var bank = Math.abs(gap) / (1 - s);
      return { placed: placed, gap: gap, bank: bank, loose: bank * (1 + w), short: gap > 0 };
    },
    outputs: function (v, c) {
      var f = PE.helpers.fmt;
      return [
        { label: "Cut once compacted", value: f(c.placed, 0) + " yd³" },
        { label: c.short ? "Compacted shortfall" : "Compacted surplus", value: f(Math.abs(c.gap), 0) + " yd³" },
        { label: c.short ? "Borrow (bank)" : "Waste (bank)", value: f(c.bank, 0) + " yd³", strong: true },
        { label: c.short ? "Borrow hauled (loose)" : "Waste hauled (loose)", value: f(c.loose, 0) + " yd³" },
      ];
    },
    note: function (v, c) {
      if (Math.abs(c.gap) < 1) return "Cut and fill balance: no borrow and no waste.";
      if (c.short) return "The cut shrinks when compacted, so it covers only part of the fill. Borrow must also shrink, so more bank volume is dug than the shortfall itself.";
      return "The cut makes more compacted fill than needed. The extra must be wasted (hauled away).";
    },
    draw: function (v, c, h) {
      var rows = [
        { label: "Cut (bank)", value: v.Vc, cls: "w-fill-amber" },
        { label: "Cut once compacted", value: c.placed, cls: "w-fill" },
        { label: "Fill needed (compacted)", value: v.Vf, cls: "w-fill-muted" },
        { label: c.short ? "Shortfall (compacted)" : "Surplus (compacted)", value: Math.abs(c.gap), cls: c.short ? "w-fill-bad" : "w-fill-muted" },
        { label: c.short ? "Borrow (bank)" : "Waste (bank)", value: c.bank, cls: "w-fill-amber" },
        { label: c.short ? "Borrow hauled (loose)" : "Waste hauled (loose)", value: c.loose, cls: "w-fill-amber" },
      ];
      var max = Math.max.apply(null, rows.map(function (r) { return r.value; }).concat([1]));
      var X = h.scale(0, max, 230, 560);
      var out = "";
      rows.forEach(function (r, i) {
        var y = 20 + i * 50;
        out += h.text(220, y + 20, r.label, { anchor: "end", cls: "w-label" });
        out += h.rect(230, y + 4, X(r.value) - 230, 24, r.cls, 4);
        out += h.text(Math.min(X(r.value) + 8, 568), y + 21, h.fmt(r.value, 0), { cls: "w-label-strong w-small" });
      });
      out += h.line(230, 14, 230, 316, "w-thin");
      return out;
    },
  });
})();
