// HD1 Horizontal curve geometry: a simple circular curve in plan, and the
// arc definition of degree of curve.
(function () {
  "use strict";
  var PE = (typeof window !== "undefined" ? window : globalThis).PEWidgets;
  var rad = function (deg) { return deg * Math.PI / 180; };

  function elements(v) {
    var R = v.R, D = v.delta, half = rad(D / 2);
    var T = R * Math.tan(half);
    var L = R * rad(D);
    return {
      T: T, L: L,
      E: R * (1 / Math.cos(half) - 1),
      M: R * (1 - Math.cos(half)),
      LC: 2 * R * Math.sin(half),
      Dc: 5729.58 / R,
      pc: v.pi - T, pt: v.pi - T + L, wrong: v.pi + T,
    };
  }

  PE.register("circular-curve", {
    title: "Simple circular curve in plan",
    height: 360,
    params: [
      { key: "R", label: "Radius R", min: 300, max: 3000, step: 50, value: 1000, unit: "ft" },
      { key: "delta", label: "Intersection angle Δ", min: 5, max: 120, step: 1, value: 40, unit: "°" },
      { key: "pi", label: "PI station (ft)", min: 1000, max: 50000, step: 25, value: 10000, unit: "ft" },
    ],
    compute: elements,
    outputs: function (v, c) {
      var f = PE.helpers.fmt, st = PE.helpers.station;
      return [
        { label: "T = R tan(Δ/2)", value: f(c.T) + " ft" },
        { label: "L = RΔπ/180", value: f(c.L) + " ft" },
        { label: "E", value: f(c.E) + " ft" },
        { label: "M", value: f(c.M) + " ft" },
        { label: "PC = PI − T", value: st(c.pc) },
        { label: "PT = PC + L", value: st(c.pt), strong: true },
        { label: "D (arc)", value: f(c.Dc) + "°" },
      ];
    },
    note: function (v, c) {
      return "Two tangents total " + PE.helpers.fmt(2 * c.T) + " ft, but the curve that replaces them is only " + PE.helpers.fmt(c.L) +
        " ft. Stations follow the built road, so the PT is at " + PE.helpers.station(c.pt) + ", " + PE.helpers.fmt(c.wrong - c.pt) + " ft short of PI + T.";
    },
    draw: function (v, c, h) {
      var D = rad(v.delta), R = v.R, T = c.T;
      // Local plan coordinates in feet: PC at the origin, back tangent heading
      // +x, the curve turning toward +y (down the page), center at (0, R).
      var u = [Math.cos(D), Math.sin(D)];
      var P = [T, 0], PT = [T + T * u[0], T * u[1]], O = [0, R];
      var arcPt = function (phi) { return [R * Math.sin(phi), R - R * Math.cos(phi)]; };
      var mid = arcPt(D / 2), chordMid = [PT[0] / 2, PT[1] / 2];
      var ext = 0.35 * T;
      var back = [-ext, 0], fwd = [PT[0] + ext * u[0], PT[1] + ext * u[1]];
      var pts = [back, P, PT, fwd, [0, 0]];
      for (var i = 0; i <= 24; i++) pts.push(arcPt(D * i / 24));
      var showCenter = v.delta >= 60;
      if (showCenter) pts.push(O);
      var xs = pts.map(function (p) { return p[0]; }), ys = pts.map(function (p) { return p[1]; });
      var minX = Math.min.apply(null, xs), maxX = Math.max.apply(null, xs);
      var minY = Math.min.apply(null, ys), maxY = Math.max.apply(null, ys);
      var s = Math.min(560 / Math.max(maxX - minX, 1), 200 / Math.max(maxY - minY, 1));
      var ox = 320 - (minX + maxX) / 2 * s, oy = 40 + (200 - (maxY - minY) * s) / 2 - minY * s;
      var X = function (p) { return ox + p[0] * s; }, Y = function (p) { return oy + p[1] * s; };
      var seg = function (a, b, cls) { return h.line(X(a), Y(a), X(b), Y(b), cls); };

      var out = "";
      // Tangents: solid where the road runs, dashed where the curve replaces them.
      out += seg(back, [0, 0], "w-line") + seg([0, 0], P, "w-dash") + seg(P, PT, "w-dash") + seg(PT, fwd, "w-line");
      // Radii toward the center.
      if (showCenter) {
        out += seg([0, 0], O, "w-thin") + seg(PT, O, "w-thin") + h.circle(X(O), Y(O), 3, "w-dot-muted");
        out += h.text(X(O) + 6, Y(O) - 6, "center", { cls: "w-label w-small" });
      } else {
        var stub = 40 / s;
        var tOf = function (p) { var dx = O[0] - p[0], dy = O[1] - p[1], n = Math.sqrt(dx * dx + dy * dy) || 1; return [p[0] + dx / n * stub, p[1] + dy / n * stub]; };
        out += seg([0, 0], tOf([0, 0]), "w-dash") + seg(PT, tOf(PT), "w-dash");
        out += h.text(X(tOf([0, 0])) + 4, Y(tOf([0, 0])) + 12, "R toward center", { cls: "w-label w-small" });
      }
      // Chord, then the arc itself.
      out += seg([0, 0], PT, "w-dash");
      var arc = [];
      for (var k = 0; k <= 48; k++) { var a = arcPt(D * k / 48); arc.push([X(a), Y(a)]); }
      out += h.poly(arc, "w-accent");
      // E (PI to curve) and M (curve to chord) lie on the same bisector.
      out += seg(P, mid, "w-amber") + seg(mid, chordMid, "w-bad");
      out += h.text((X(P) + X(mid)) / 2 - 6, (Y(P) + Y(mid)) / 2 + 4, "E", { anchor: "end", cls: "w-label-amber" });
      out += h.text((X(mid) + X(chordMid)) / 2 + 6, (Y(mid) + Y(chordMid)) / 2 + 4, "M", { cls: "w-label-bad" });
      // Points and labels.
      out += h.circle(X([0, 0]), Y([0, 0]), 4.5, "w-dot-muted") + h.text(X([0, 0]), Y([0, 0]) - 10, "PC", { anchor: "middle", cls: "w-label-strong" });
      out += h.circle(X(P), Y(P), 4, "w-dot-muted") + h.text(X(P) - 6, Y(P) - 10, "PI", { anchor: "end", cls: "w-label-strong" });
      out += h.text(X(P) + 8, Y(P) - 10, "Δ = " + h.fmt(v.delta, v.delta % 1 ? 2 : 0) + "°", { cls: "w-label w-small" });
      var ptRight = X(PT) < 560;
      out += h.circle(X(PT), Y(PT), 4.5, "w-dot-muted") + h.text(X(PT) + (ptRight ? 9 : -9), Y(PT) + 4, "PT", { anchor: ptRight ? "start" : "end", cls: "w-label-strong" });
      out += h.text((X([0, 0]) + X(P)) / 2, Y(P) - 8, "T", { anchor: "middle", cls: "w-label w-small" });
      var nrm = [Math.sin(D) * 14, -Math.cos(D) * 14];
      out += h.text((X(P) + X(PT)) / 2 + nrm[0], (Y(P) + Y(PT)) / 2 + nrm[1] + 4, "T", { anchor: "middle", cls: "w-label w-small" });
      // L sits just inside the arc, a quarter of the way along, clear of E, M and T.
      var q = arcPt(D * 0.28), qn = [-Math.sin(D * 0.28), Math.cos(D * 0.28)];
      out += h.text(X(q) + qn[0] * 16, Y(q) + qn[1] * 16 + 4, "L", { anchor: "middle", cls: "w-label-accent" });

      // Stationing strip: along the tangents versus along the curve.
      var x0 = 80, x1 = 600, S = h.scale(c.pc, c.wrong, x0, x1);
      out += h.line(x0 - 12, 262, x1 + 10, 262, "w-grid");
      out += h.text(x0 - 10, 296, "Tangents", { anchor: "end", cls: "w-label w-small" });
      out += h.text(x0 - 10, 336, "Curve", { anchor: "end", cls: "w-label w-small" });
      out += h.line(S(c.pc), 292, S(c.wrong), 292, "w-muted");
      [[c.pc, "PC"], [v.pi, "PI"], [c.wrong, "PI + T"]].forEach(function (m, i) {
        out += h.line(S(m[0]), 286, S(m[0]), 298, "w-thin");
        out += h.text(S(m[0]), 281, m[1] + " " + h.station(m[0]), { anchor: i === 0 ? "start" : (i === 2 ? "end" : "middle"), cls: i === 2 ? "w-label-bad w-small" : "w-label w-small" });
      });
      out += h.line(S(c.pc), 332, S(c.pt), 332, "w-accent");
      out += h.line(S(c.pt), 326, S(c.pt), 338, "w-thin");
      out += h.text(S(c.pc), 352, "PC " + h.station(c.pc), { cls: "w-label w-small" });
      out += h.text(S(c.pt), 352, "PT = PC + L = " + h.station(c.pt), { anchor: "end", cls: "w-label-accent w-small" });
      return out;
    },
  });

  // Degree of curve, arc definition: the central angle that 100 ft of arc subtends.
  PE.register("degree-of-curve", {
    title: "Degree of curve, arc definition",
    height: 300,
    params: [
      { key: "R", label: "Radius R", min: 500, max: 5000, step: 1, value: 1432, unit: "ft" },
      { key: "delta", label: "Intersection angle Δ", min: 5, max: 90, step: 1, value: 30, unit: "°" },
    ],
    compute: function (v) {
      var Dc = 5729.58 / v.R;
      return { Dc: Dc, L: 100 * v.delta / Dc, Lcheck: v.R * rad(v.delta) };
    },
    outputs: function (v, c) {
      var f = PE.helpers.fmt;
      return [
        { label: "D = 5729.58 / R", value: f(c.Dc, 3) + "°", strong: true },
        { label: "L = 100 Δ / D", value: f(c.L) + " ft" },
        { label: "Check: L = RΔπ/180", value: f(c.Lcheck) + " ft" },
      ];
    },
    note: function (v, c) {
      return "A " + PE.helpers.fmt(c.Dc, 2) + "° curve turns " + PE.helpers.fmt(c.Dc, 2) + "° for every 100 ft of arc. Sharper curves have larger D and smaller R. The drawing is not to scale: the angle is drawn four times wider.";
    },
    draw: function (v, c, h) {
      var cx = 320, cy = 285, rp = 245;
      // The true angle is only a few degrees, so it is drawn four times wider.
      var ang = Math.min(Math.max(c.Dc * 4, 10), 50);
      var a0 = rad(-90 - ang / 2), a1 = rad(-90 + ang / 2);
      var p = function (a, r) { return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; };
      var out = "";
      // A wide piece of the circle for context, then the 100-ft arc.
      var ctx = [];
      for (var i = 0; i <= 40; i++) { var a = rad(-90 - 32 + 64 * i / 40); ctx.push(p(a, rp)); }
      out += h.poly(ctx, "w-muted");
      var arc = [];
      for (var k = 0; k <= 20; k++) { var b = a0 + (a1 - a0) * k / 20; arc.push(p(b, rp)); }
      out += h.poly(arc, "w-accent");
      var A = p(a0, rp), B = p(a1, rp);
      out += h.line(cx, cy, A[0], A[1], "w-thin") + h.line(cx, cy, B[0], B[1], "w-thin");
      var lab = p(rad(-90), rp + 16);
      out += h.text(lab[0], lab[1], "100 ft of arc", { anchor: "middle", cls: "w-label-accent" });
      var wedge = [];
      for (var j = 0; j <= 12; j++) { var w = a0 + (a1 - a0) * j / 12; wedge.push(p(w, 46)); }
      out += h.poly(wedge, "w-amber");
      var dl = p(a1, 60);
      out += h.text(dl[0] + 10, dl[1] + 6, "D = " + h.fmt(c.Dc, 2) + "°", { cls: "w-label-amber" });
      out += h.text(A[0] - 10, (cy + A[1]) / 2, "R = " + h.fmt(v.R, 0) + " ft", { anchor: "end", cls: "w-label w-small" });
      out += h.circle(cx, cy, 3, "w-dot-muted") + h.text(cx + 8, cy - 4, "center", { cls: "w-label w-small" });
      return out;
    },
  });
})();
