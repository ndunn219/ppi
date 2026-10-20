// HD2 Superelevation and side friction: e + f = V²/(15R).
(function () {
  "use strict";
  var PE = (typeof window !== "undefined" ? window : globalThis).PEWidgets;

  // The design side friction factors the course's problems use (see the
  // min_radius solver), by design speed in mi/h.
  var FMAX = { 40: 0.16, 45: 0.15, 50: 0.14, 55: 0.13, 60: 0.12, 65: 0.11, 70: 0.10 };
  var SPEEDS = [40, 45, 50, 55, 60, 65, 70];
  var fmaxAt = function (V) { return FMAX[V] !== undefined ? FMAX[V] : FMAX[Math.min(70, Math.max(40, Math.round(V / 5) * 5))]; };
  var rmin = function (V, e) { return V * V / (15 * (e + fmaxAt(V))); };

  PE.register("banked-curve", {
    title: "Superelevation and side friction share the load",
    height: 320,
    params: [
      { key: "V", label: "Design speed V", min: 40, max: 70, step: 5, value: 60, unit: "mi/h" },
      { key: "R", label: "Radius R", min: 300, max: 4000, step: 50, value: 1200, unit: "ft" },
      { key: "e", label: "Superelevation e", min: 0, max: 0.12, step: 0.01, value: 0.08 },
    ],
    compute: function (v) {
      var demand = v.V * v.V / (15 * v.R);
      var fmax = fmaxAt(v.V);
      var fneed = demand - v.e;
      return { demand: demand, fmax: fmax, fneed: fneed, rmin: rmin(v.V, v.e), ok: fneed <= fmax + 1e-9 };
    },
    outputs: function (v, c) {
      var f = PE.helpers.fmt;
      return [
        { label: "Needed: V²/(15R)", value: f(c.demand, 3) },
        { label: "Friction needed: f = V²/15R − e", value: f(c.fneed, 3), strong: true },
        { label: "Design f at " + v.V + " mi/h", value: f(c.fmax, 2) },
        { label: "R_min for this V and e", value: f(c.rmin, 0) + " ft" },
      ];
    },
    note: function (v, c) {
      var f = PE.helpers.fmt;
      if (c.fneed < 0) return "The slope alone more than balances the turn: a slow vehicle would tend to slide toward the inside, so friction acts outward. That is one reason e is capped.";
      if (c.ok) return "Superelevation supplies " + f(v.e, 2) + " and friction the remaining " + f(c.fneed, 3) + ", within the design value of " + f(c.fmax, 2) + ". The curve works at " + v.V + " mi/h.";
      return "Friction would need to supply " + f(c.fneed, 3) + ", more than the design value of " + f(c.fmax, 2) + ". This radius is too sharp for " + v.V + " mi/h with e = " + f(v.e, 2) + "; it needs at least " + f(c.rmin, 0) + " ft.";
    },
    draw: function (v, c, h) {
      var out = "";
      // Left: a cross-section of the roadway, slope drawn four times steeper.
      var cx = 175, cy = 210, half = 130, th = Math.atan(v.e) * 4;
      var dx = Math.cos(th) * half, dy = Math.sin(th) * half;
      out += h.line(cx - dx, cy + dy, cx + dx, cy - dy, "w-road");
      out += h.text(cx - dx, cy + dy + 26, "inside of curve", { cls: "w-label w-small" });
      out += h.text(cx + dx, cy - dy - 14, "outside", { anchor: "end", cls: "w-label w-small" });
      // The vehicle, a box sitting square on the slope.
      var nx = Math.sin(th), ny = Math.cos(th), tx = Math.cos(th), ty = -Math.sin(th);
      var w = 36, hh = 34, base = [cx, cy];
      var corner = function (a, b) { return [base[0] + tx * a - nx * b, base[1] + ty * a - ny * b]; };
      out += h.polygon([corner(-w, 7), corner(w, 7), corner(w, 7 + hh), corner(-w, 7 + hh)], "w-fill-muted");
      var g = corner(0, 7 + hh / 2);
      // Weight straight down, and the sideways force the turn needs, toward the inside.
      out += h.arrow(g[0], g[1], g[0], g[1] + 62, "w-thin") + h.text(g[0] + 6, g[1] + 60, "W", { cls: "w-label w-small" });
      var need = Math.min(150, c.demand * 520);
      out += h.arrow(g[0], g[1] - 4, g[0] - need, g[1] - 4, "w-bad");
      out += h.text(g[0] - need / 2, g[1] - 14, "needed toward center", { anchor: "middle", cls: "w-label-bad w-small" });
      out += h.text(20, 24, "e = " + h.fmt(v.e, 2) + " (slope drawn 4× steeper)", { cls: "w-label w-small" });

      // Right: what is needed against what e and f supply.
      var top = Math.max(c.demand, v.e + c.fmax, 0.05) * 1.15;
      var Y = h.scale(0, top, 280, 40);
      var bw = 70, xa = 400, xb = 520;
      out += h.line(370, 280, 620, 280, "w-thin");
      out += h.rect(xa, Y(c.demand), bw, 280 - Y(c.demand), "w-fill-bad", 3);
      out += h.text(xa + bw / 2, Y(c.demand) - 6, h.fmt(c.demand, 3), { anchor: "middle", cls: "w-label-bad" });
      out += h.text(xa + bw / 2, 298, "Needed", { anchor: "middle", cls: "w-label-strong" });
      out += h.text(xa + bw / 2, 312, "V²/(15R)", { anchor: "middle", cls: "w-label w-small" });
      out += h.rect(xb, Y(v.e), bw, 280 - Y(v.e), "w-fill", 0);
      if (v.e > 0.012) out += h.text(xb + bw / 2, (Y(v.e) + 280) / 2 + 4, "e", { anchor: "middle", cls: "w-label-accent" });
      var fUsed = Math.max(0, Math.min(c.fneed, c.fmax));
      if (fUsed > 0) {
        out += h.rect(xb, Y(v.e + fUsed), bw, Y(v.e) - Y(v.e + fUsed), "w-fill-amber", 0);
        if (Y(v.e) - Y(v.e + fUsed) > 16) out += h.text(xb + bw / 2, (Y(v.e) + Y(v.e + fUsed)) / 2 + 4, "f", { anchor: "middle", cls: "w-label-amber" });
      }
      if (!c.ok) {
        out += h.rect(xb, Y(c.demand), bw, Y(v.e + c.fmax) - Y(c.demand), "w-fill-bad", 0);
        out += h.text(xb + bw + 6, (Y(c.demand) + Y(v.e + c.fmax)) / 2 + 4, "short", { cls: "w-label-bad w-small" });
      }
      out += h.line(xb - 12, Y(v.e + c.fmax), xb + bw + 12, Y(v.e + c.fmax), "w-dash");
      // Above the line normally; just below it when the shortfall band sits above.
      out += h.text(xb + bw / 2, Y(v.e + c.fmax) + (c.ok ? -6 : 14), "e + f max", { anchor: "middle", cls: "w-label w-small" });
      out += h.text(xb + bw / 2, 298, "Supplied", { anchor: "middle", cls: "w-label-strong" });
      out += h.text(xb + bw / 2, 312, "e + f", { anchor: "middle", cls: "w-label w-small" });
      return out;
    },
  });

  PE.register("rmin-chart", {
    title: "Minimum radius against design speed",
    height: 320,
    params: [
      { key: "e", label: "Maximum superelevation e", min: 0, max: 0.12, step: 0.02, value: 0.08 },
      { key: "V", label: "Design speed V", min: 40, max: 70, step: 5, value: 60, unit: "mi/h" },
    ],
    compute: function (v) {
      return {
        rows: SPEEDS.map(function (s) { return { V: s, R: rmin(s, v.e), R0: s * s / (15 * fmaxAt(s)) }; }),
        R: rmin(v.V, v.e),
      };
    },
    outputs: function (v, c) {
      return [
        { label: "R_min at " + v.V + " mi/h", value: PE.helpers.fmt(c.R, 0) + " ft", strong: true },
        { label: "f used", value: PE.helpers.fmt(fmaxAt(v.V), 2) },
      ];
    },
    note: function (v, c) {
      var r40 = c.rows[0].R, r70 = c.rows[6].R;
      return "From 40 to 70 mi/h the minimum radius grows " + PE.helpers.fmt(r70 / r40, 1) + " times: speed is squared, and the friction allowed drops as speed rises. The dashed line is the same curve with no superelevation.";
    },
    draw: function (v, c, h) {
      var X = h.scale(40, 70, 80, 600), Y = h.scale(0, 3500, 280, 30);
      var out = h.gridY([0, 500, 1000, 1500, 2000, 2500, 3000, 3500], Y, 80, 600, function (t) { return h.fmt(t, 0); });
      SPEEDS.forEach(function (s) { out += h.text(X(s), 298, s + "", { anchor: "middle", cls: "w-label w-small" }); });
      out += h.text(340, 316, "Design speed (mi/h)", { anchor: "middle", cls: "w-label w-small" });
      out += h.text(80, 16, "R_min (ft)", { cls: "w-label w-small" });
      out += h.poly(c.rows.map(function (r) { return [X(r.V), Y(r.R0)]; }), "w-dash");
      out += h.poly(c.rows.map(function (r) { return [X(r.V), Y(r.R)]; }), "w-accent");
      c.rows.forEach(function (r) { out += h.circle(X(r.V), Y(r.R), 3.5, "w-dot"); });
      out += h.text(X(50), Y(c.rows[2].R0) - 10, "e = 0", { anchor: "middle", cls: "w-label w-small" });
      out += h.text(X(50), Y(c.rows[2].R) + 22, "e = " + h.fmt(v.e, 2), { anchor: "middle", cls: "w-label-accent w-small" });
      out += h.line(X(v.V), Y(c.R), X(v.V), 280, "w-dash");
      out += h.circle(X(v.V), Y(c.R), 6, "w-dot-amber");
      out += h.text(X(v.V) + (v.V >= 60 ? -10 : 10), Y(c.R) - 10, h.fmt(c.R, 0) + " ft", { anchor: v.V >= 60 ? "end" : "start", cls: "w-label-amber" });
      return out;
    },
  });
})();
