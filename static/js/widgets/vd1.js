// VD1 Vertical curve elevations: an equal-tangent parabola between two grades.
(function () {
  "use strict";
  var PE = (typeof window !== "undefined" ? window : globalThis).PEWidgets;

  function curve(v) {
    var g1 = v.g1 / 100, g2 = v.g2 / 100, L = v.L;
    var pvc = v.pvi - L / 2, pvt = v.pvi + L / 2;
    var epvc = v.epvi - g1 * L / 2, epvt = v.epvi + g2 * L / 2;
    var y = function (x) { return epvc + g1 * x + (g2 - g1) / (2 * L) * x * x; };
    var turn = null;
    if (g1 * g2 < 0) {
      var xt = -g1 * L / (g2 - g1);
      turn = { x: xt, sta: pvc + xt, elev: y(xt), kind: g1 > 0 ? "High" : "Low" };
    }
    var xq = v.xq * L;
    return {
      pvc: pvc, pvt: pvt, epvc: epvc, epvt: epvt, y: y, turn: turn,
      A: Math.abs(v.g2 - v.g1), crest: v.g2 < v.g1, flat: v.g1 === v.g2,
      xq: xq, eq: y(xq), staq: pvc + xq,
      e: (v.g2 - v.g1) * L / 800, // offset at the PVI, grades in percent
    };
  }

  PE.register("vertical-curve", {
    title: "Equal-tangent vertical curve",
    height: 330,
    params: [
      { key: "g1", label: "Entering grade g₁", min: -6, max: 6, step: 0.5, value: 3, unit: "%" },
      { key: "g2", label: "Exiting grade g₂", min: -6, max: 6, step: 0.5, value: -2, unit: "%" },
      { key: "L", label: "Curve length L", min: 200, max: 1600, step: 50, value: 800, unit: "ft" },
      { key: "xq", label: "Point on the curve (share of L)", min: 0, max: 1, step: 0.05, value: 0.25 },
      { key: "pvi", label: "PVI station (ft)", min: 1000, max: 20000, step: 50, value: 5000, unit: "ft" },
      { key: "epvi", label: "PVI elevation", min: 100, max: 1000, step: 0.5, value: 500, unit: "ft" },
    ],
    compute: curve,
    outputs: function (v, c) {
      var st = PE.helpers.station, f = PE.helpers.fmt;
      var out = [
        { label: "PVC", value: st(c.pvc) + " · " + f(c.epvc) + " ft" },
        { label: "PVT", value: st(c.pvt) + " · " + f(c.epvt) + " ft" },
        { label: "Elevation at " + st(c.staq), value: f(c.eq) + " ft", strong: true },
      ];
      if (c.turn) out.push({ label: c.turn.kind + " point", value: st(c.turn.sta) + " · " + f(c.turn.elev) + " ft", strong: true });
      out.push({ label: "A = |g₂ − g₁|", value: f(c.A, 1) + "%" });
      out.push({ label: "Offset at PVI", value: f(Math.abs(c.e)) + " ft" });
      return out;
    },
    note: function (v, c) {
      if (c.flat) return "The grades are equal, so there is no curve: the profile is a straight line.";
      var kind = c.crest ? "a crest curve (the grade decreases)" : "a sag curve (the grade increases)";
      if (!c.turn) return "This is " + kind + ". Both grades have the same sign, so there is no high or low point inside the curve: the extreme elevation is at the " + ((c.crest ? v.g1 < 0 : v.g1 > 0) ? "PVC" : "PVT") + ".";
      return "This is " + kind + ". The grade passes through zero " + PE.helpers.fmt(c.turn.x, 0) + " ft past the PVC, so the " + c.turn.kind.toLowerCase() + " point is inside the curve.";
    },
    draw: function (v, c, h) {
      var L = v.L, pad = L * 0.18;
      var x0 = c.pvc - pad, x1 = c.pvt + pad;
      var g1 = v.g1 / 100, g2 = v.g2 / 100;
      // Elevations along both tangents and the curve, to fit the view.
      var eLeft = c.epvc - g1 * pad, eRight = c.epvt + g2 * pad;
      var elevs = [eLeft, eRight, v.epvi, c.epvc, c.epvt];
      for (var i = 0; i <= 20; i++) elevs.push(c.y(L * i / 20));
      var lo = Math.min.apply(null, elevs), hi = Math.max.apply(null, elevs);
      var span = Math.max(hi - lo, 2);
      lo -= span * 0.18; hi += span * 0.22;
      var X = h.scale(x0, x1, 60, 620), Y = h.scale(lo, hi, 285, 20);
      var out = h.gridY(h.ticks(lo, hi, 4), Y, 60, 620, function (t) { return h.fmt(t, span < 8 ? 1 : 0); });

      // Tangents through the PVI.
      out += h.line(X(x0), Y(eLeft), X(v.pvi), Y(v.epvi), "w-dash");
      out += h.line(X(v.pvi), Y(v.epvi), X(x1), Y(eRight), "w-dash");
      out += h.line(X(x0), Y(eLeft), X(c.pvc), Y(c.epvc), "w-line");
      out += h.line(X(c.pvt), Y(c.epvt), X(x1), Y(eRight), "w-line");
      // The parabola.
      var pts = [];
      for (var k = 0; k <= 60; k++) { var x = L * k / 60; pts.push([X(c.pvc + x), Y(c.y(x))]); }
      out += h.poly(pts, "w-accent");

      // Offset at the PVI (middle of the curve).
      // The turning point's label goes on its own side of the PVI, the
      // offset label on the other, so the two never collide.
      var turnRight = c.turn ? c.turn.sta >= v.pvi : false;
      if (!c.flat) {
        var ymid = c.y(L / 2);
        out += h.line(X(v.pvi), Y(v.epvi), X(v.pvi), Y(ymid), "w-thin");
        out += h.text(X(v.pvi) + (turnRight ? -6 : 6), (Y(v.epvi) + Y(ymid)) / 2 + 4, "e = " + h.fmt(Math.abs(c.e)) + " ft", { anchor: turnRight ? "end" : "start", cls: "w-label w-small" });
      }

      // Key points.
      out += h.circle(X(c.pvc), Y(c.epvc), 4.5, "w-dot-muted") + h.text(X(c.pvc), Y(c.epvc) + (g1 >= 0 ? 20 : -12), "PVC", { anchor: "middle", cls: "w-label-strong" });
      out += h.circle(X(c.pvt), Y(c.epvt), 4.5, "w-dot-muted") + h.text(X(c.pvt), Y(c.epvt) + (g2 <= 0 ? 20 : -12), "PVT", { anchor: "middle", cls: "w-label-strong" });
      out += h.circle(X(v.pvi), Y(v.epvi), 4, "w-dot-muted") + h.text(X(v.pvi), Y(v.epvi) + (c.crest ? -10 : 20), "PVI", { anchor: "middle", cls: "w-label-strong" });
      out += h.text(X(x0) + 4, Y(eLeft) + (g1 >= 0 ? 18 : -8), "g₁ = " + h.fmt(v.g1, 1) + "%", { cls: "w-label w-small" });
      out += h.text(X(x1) - 4, Y(eRight) + (g2 <= 0 ? 18 : -8), "g₂ = " + h.fmt(v.g2, 1) + "%", { anchor: "end", cls: "w-label w-small" });

      if (c.turn) {
        out += h.circle(X(c.turn.sta), Y(c.turn.elev), 5.5, "w-dot-amber");
        out += h.text(X(c.turn.sta) + (turnRight ? 9 : -9), Y(c.turn.elev) + (c.crest ? -10 : 20), c.turn.kind + " point", { anchor: turnRight ? "start" : "end", cls: "w-label-amber" });
      }

      // The point the student is asking about.
      out += h.line(X(c.staq), Y(c.eq), X(c.staq), 285, "w-dash");
      out += h.circle(X(c.staq), Y(c.eq), 5, "w-dot");
      out += h.text(X(c.staq) + 6, 280, h.station(c.staq), { cls: "w-label-accent w-small" });

      // Curve length along the bottom.
      out += h.dim(X(c.pvc), 305, X(c.pvt), 305, "L = " + h.fmt(L, 0) + " ft", { offset: 18 });
      out += h.line(X(c.pvc), 295, X(c.pvc), 312, "w-thin") + h.line(X(c.pvt), 295, X(c.pvt), 312, "w-thin");
      return out;
    },
  });
})();
