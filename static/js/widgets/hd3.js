// HD3 Horizontal sight distance: the sightline across the inside of a
// curve, the offset M it needs, and an obstruction that may block it.
(function () {
  "use strict";
  var PE = (typeof window !== "undefined" ? window : globalThis).PEWidgets;
  var rad = function (d) { return d * Math.PI / 180; };
  var deg = function (r) { return r * 180 / Math.PI; };

  function sight(v) {
    var half = 28.65 * v.S / v.R; // degrees
    var M = v.R * (1 - Math.cos(rad(half)));
    var ratio = Math.min(1, Math.max(-1, (v.R - v.C) / v.R));
    var sAvail = v.R / 28.65 * deg(Math.acos(ratio));
    return { half: half, M: M, approx: v.S * v.S / (8 * v.R), sAvail: sAvail, clear: v.C >= M - 1e-9 };
  }

  PE.register("sightline", {
    title: "Sight distance on a horizontal curve",
    height: 320,
    params: [
      { key: "R", label: "Radius to inside lane centerline R", min: 300, max: 3000, step: 50, value: 1000, unit: "ft" },
      { key: "S", label: "Required sight distance S", min: 100, max: 800, step: 25, value: 400, unit: "ft" },
      { key: "C", label: "Obstruction offset from lane centerline", min: 5, max: 80, step: 1, value: 25, unit: "ft" },
    ],
    compute: sight,
    outputs: function (v, c) {
      var f = PE.helpers.fmt;
      return [
        { label: "Half-angle 28.65 S / R", value: f(c.half, 3) + "°" },
        { label: "M = R(1 − cos)", value: f(c.M) + " ft", strong: true },
        { label: "S²/(8R) approximation", value: f(c.approx) + " ft" },
        { label: "Sight distance the obstruction allows", value: f(c.sAvail, 0) + " ft" },
      ];
    },
    note: function (v, c) {
      var f = PE.helpers.fmt;
      if (c.clear) return "Clear: the sightline needs " + f(c.M) + " ft of offset and the obstruction is " + v.C + " ft away. The driver can see up to " + f(c.sAvail, 0) + " ft ahead along the lane.";
      return "Blocked: the sightline needs " + f(c.M) + " ft but the obstruction is only " + v.C + " ft from the lane centerline, so the driver sees only " + f(c.sAvail, 0) + " ft ahead.";
    },
    draw: function (v, c, h) {
      var R = v.R, th = rad(c.half);
      var phiMax = Math.min(th * 1.3, rad(85));
      var P = function (phi, r) { return [r * Math.sin(phi), r * Math.cos(phi)]; };
      // Offsets inward are tiny next to the chord, so they are drawn exaggerated.
      var sx = 560 / (2 * R * Math.sin(phiMax));
      var dmax = Math.max(c.M, v.C + 8, R * (1 - Math.cos(phiMax)) + 8) * 1.1 + 10;
      var sy = 236 / dmax;
      var X = function (p) { return 320 + p[0] * sx; };
      var Y = function (p) { return 44 + (R - p[1] + 10) * sy; };
      var arcAt = function (r, a0, a1, cls) {
        var pts = [];
        for (var i = 0; i <= 60; i++) { var a = a0 + (a1 - a0) * i / 60; var q = P(a, r); pts.push([X(q), Y(q)]); }
        return h.poly(pts, cls);
      };
      var out = "";
      // The lane: centerline (accent) and its edges 6 ft either side.
      out += arcAt(R + 6, -phiMax, phiMax, "w-thin") + arcAt(R - 6, -phiMax, phiMax, "w-thin");
      out += arcAt(R, -phiMax, phiMax, "w-muted");
      out += arcAt(R, -th, th, "w-accent");
      // The obstruction on the inside of the curve.
      out += arcAt(R - v.C, -th * 0.75, th * 0.75, c.clear ? "w-line" : "w-bad");
      var wl = P(-th * 0.75, R - v.C);
      out += h.text(X(wl), Y(wl) + 16, "obstruction, " + v.C + " ft in", { cls: c.clear ? "w-label w-small" : "w-label-bad w-small" });
      // The sightline: a chord from the driver's eye to the object.
      var A = P(-th, R), B = P(th, R);
      out += h.line(X(A), Y(A), X(B), Y(B), c.clear ? "w-amber" : "w-bad");
      out += h.circle(X(A), Y(A), 5, "w-dot") + h.text(X(A) + 4, Y(A) + 20, "driver", { cls: "w-label-strong" });
      out += h.circle(X(B), Y(B), 5, "w-dot-muted") + h.text(X(B) - 4, Y(B) + 20, "object", { anchor: "end", cls: "w-label-strong" });
      // M at the middle of the curve.
      var top = P(0, R), bot = [0, R * Math.cos(th)];
      out += h.line(X(top), Y(top), X(bot), Y(bot), "w-thin");
      out += h.text(X(top) + 8, (Y(top) + Y(bot)) / 2 + 4, "M = " + h.fmt(c.M) + " ft", { cls: "w-label-accent" });
      out += h.text(320, 18, "S = " + v.S + " ft along the lane, driver to object", { anchor: "middle", cls: "w-label w-small" });
      var k = sy / sx;
      if (k > 1.5) out += h.text(12, 312, "Offsets drawn " + h.fmt(k, 0) + "× wider than to scale", { cls: "w-label w-small" });
      out += h.text(628, 312, "center of curve ↓", { anchor: "end", cls: "w-label w-small" });
      return out;
    },
  });
})();
