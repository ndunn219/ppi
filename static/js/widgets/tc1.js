// TC1 Temporary traffic control tapers: a plan view of a work zone drawn
// to a fixed length scale, so tapers for different speeds compare.
(function () {
  "use strict";
  var PE = (typeof window !== "undefined" ? window : globalThis).PEWidgets;
  var SHARE = { merging: 1, shifting: 0.5, shoulder: 1 / 3 };
  var SHARE_LABEL = { merging: "L", shifting: "L/2", shoulder: "L/3" };

  function compute(v) {
    var low = v.S <= 40;
    var L = low ? v.W * v.S * v.S / 60 : v.W * v.S;
    var other = low ? v.W * v.S : v.W * v.S * v.S / 60;
    return { low: low, L: L, other: other, T: L * SHARE[v.kind] };
  }

  PE.register("lane-closure", {
    title: "Work zone taper, plan view to scale",
    height: 262,
    params: [
      { key: "kind", label: "Taper", value: "merging", options: [
        { value: "merging", label: "Merging (lane closed)" },
        { value: "shifting", label: "Shifting (lanes move over)" },
        { value: "shoulder", label: "Shoulder (shoulder closed)" },
      ] },
      { key: "S", label: "Speed S", min: 20, max: 70, step: 5, value: 55, unit: "mi/h" },
      { key: "W", label: "Offset width W", min: 8, max: 14, step: 1, value: 12, unit: "ft" },
    ],
    compute: compute,
    outputs: function (v, c) {
      var f = PE.helpers.fmt;
      return [
        { label: "Formula", value: c.low ? "L = WS² / 60 (S ≤ 40)" : "L = WS (S ≥ 45)" },
        { label: "Base length L", value: f(c.L, 0) + " ft" },
        { label: "Share for this taper", value: SHARE_LABEL[v.kind] },
        { label: "Minimum taper length", value: f(c.T, 0) + " ft", strong: true },
      ];
    },
    note: function (v, c) {
      var f = PE.helpers.fmt;
      var which = c.low ? "At " + v.S + " mi/h the WS²/60 form applies." : "At " + v.S + " mi/h the WS form applies.";
      var cmp = " The other form would give " + f(c.other, 0) + " ft for the base length.";
      return which + cmp + " A " + v.kind + " taper needs at least " + SHARE_LABEL[v.kind] + " = " + f(c.T, 0) + " ft.";
    },
    draw: function (v, c, h) {
      var X = h.scale(0, 1100, 96, 610);
      var lane = 34;
      var top = 70;
      var out = "";
      var y1 = top, y2 = top + lane, y3 = top + 2 * lane, y4 = top + 2 * lane + 22; // shoulder below lane 2
      var x0 = X(0), xT = X(c.T), xEnd = X(1100);

      // Pavement, lanes and shoulder.
      out += h.rect(x0, y1, xEnd - x0, y4 - y1, "w-fill-muted");
      out += h.line(x0, y1, xEnd, y1, "w-line");
      out += h.line(x0, y2, xEnd, y2, "w-dash");
      out += h.line(x0, y3, xEnd, y3, "w-thin");
      out += h.line(x0, y4, xEnd, y4, "w-line");
      out += h.text(x0 - 6, y1 + 21, "Lane 1", { anchor: "end", cls: "w-label w-small" });
      out += h.text(x0 - 6, y2 + 21, "Lane 2", { anchor: "end", cls: "w-label w-small" });
      out += h.text(x0 - 6, y3 + 15, "Shoulder", { anchor: "end", cls: "w-label w-small" });
      out += h.arrow(x0 + 70, y1 - 14, x0 + 150, y1 - 14, "w-thin");
      out += h.text(x0 + 156, y1 - 10, "Traffic", { cls: "w-label w-small" });

      // The taper's line of channelizing devices, and the closed area after it.
      var a, b, closedTop, closedBot;
      if (v.kind === "shoulder") { a = y4; b = y3; closedTop = y3; closedBot = y4; }
      else if (v.kind === "shifting") { a = y4; b = y2; closedTop = null; }
      else { a = y3; b = y2; closedTop = y2; closedBot = y3; }
      if (closedTop !== null) out += h.rect(xT, closedTop, xEnd - xT, closedBot - closedTop, "w-fill-amber");
      if (v.kind === "shifting") {
        // Both lanes shift toward the shoulder side by W.
        out += h.line(x0, y2, xT, y3, "w-dash");
        out += h.line(xT, y3, xEnd, y3, "w-dash");
        out += h.line(x0, y1, xT, y2, "w-amber");
        out += h.line(xT, y2, xEnd, y2, "w-amber");
        out += h.rect(xT, y1, xEnd - xT, y2 - y1, "w-fill-amber");
        out += h.text(xT + 8, y1 + 21, "Work area", { cls: "w-label-amber w-small" });
      } else {
        out += h.text(xT + 8, closedTop + (closedBot - closedTop) / 2 + 5, "Work area", { cls: "w-label-amber w-small" });
      }
      var n = 9;
      for (var i = 0; i <= n; i++) {
        var t = i / n;
        var xi = x0 + (xT - x0) * t, yi = v.kind === "shifting" ? y1 + (y2 - y1) * t : a + (b - a) * t;
        out += h.circle(xi, yi, 3.5, "w-dot-amber");
      }
      if (v.kind !== "shifting") out += h.line(xT, b, xEnd, b, "w-amber");

      // Taper length, with a ruler for scale.
      out += h.dim(x0, y4 + 30, xT, y4 + 30, "Taper " + h.fmt(c.T, 0) + " ft", { offset: 16 });
      var ry = y4 + 68;
      out += h.line(x0, ry, xEnd, ry, "w-thin");
      [0, 200, 400, 600, 800, 1000].forEach(function (ft) {
        out += h.line(X(ft), ry - 4, X(ft), ry + 4, "w-thin");
        out += h.text(X(ft), ry + 18, ft + " ft", { anchor: "middle", cls: "w-label w-small" });
      });
      out += h.text(610, 24, "Plan view; width not to scale", { anchor: "end", cls: "w-label w-small" });
      return out;
    },
  });
})();
