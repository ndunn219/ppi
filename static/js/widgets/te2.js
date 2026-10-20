// TE2 Signal timing: the yellow change interval and Webster's cycle length.
(function () {
  "use strict";
  var PE = (typeof window !== "undefined" ? window : globalThis).PEWidgets;
  var G = 32.2, A = 10;

  PE.register("yellow-interval", {
    title: "Yellow change interval and stopping distance",
    height: 300,
    params: [
      { key: "V", label: "Approach speed", min: 25, max: 65, step: 5, value: 45, unit: "mi/h" },
      { key: "G", label: "Grade (+ up, − down)", min: -6, max: 6, step: 0.5, value: 0, unit: "%" },
      { key: "t", label: "Perception-reaction time", min: 0.5, max: 2, step: 0.1, value: 1, unit: "s" },
    ],
    compute: function (v) {
      var speed = 1.47 * v.V;
      var denom = 2 * A + 2 * G * v.G / 100;
      var Y = v.t + speed / denom;
      var react = speed * v.t, brake = speed * speed / denom;
      return { speed: speed, denom: denom, Y: Y, react: react, brake: brake, stop: react + brake, travel: speed * Y };
    },
    outputs: function (v, c) {
      var f = PE.helpers.fmt;
      return [
        { label: "v = 1.47 × V", value: f(c.speed, 1) + " ft/s" },
        { label: "2a + 2Gg", value: f(c.denom, 2) + " ft/s²" },
        { label: "Yellow Y", value: f(c.Y, 2) + " s", strong: true },
        { label: "Stopping distance", value: f(c.stop, 0) + " ft" },
      ];
    },
    note: function (v, c) {
      var f = PE.helpers.fmt;
      return "A driver more than " + f(c.stop, 0) + " ft from the stop bar when the yellow starts can stop comfortably. A driver closer than that keeps going and, at " + f(v.V, 0) + " mi/h, covers exactly " + f(c.travel, 0) + " ft during the " + f(c.Y, 2) + "-s yellow, reaching the stop bar just as it ends.";
    },
    draw: function (v, c, h) {
      var maxD = Math.max(c.stop * 1.18, 200);
      var bar = 590;
      var X = h.scale(0, maxD, bar, 40); // distance back from the stop bar
      var out = "";
      // Road and stop bar.
      out += h.rect(20, 60, 600, 54, "w-fill-muted");
      out += h.line(20, 87, bar, 87, "w-dash");
      out += h.line(bar, 56, bar, 118, "w-line");
      out += h.text(bar, 48, "Stop bar", { anchor: "middle", cls: "w-label-strong" });
      // Vehicle at the start of the stopping distance.
      out += h.rect(X(c.stop) - 16, 92, 32, 16, "w-fill-amber", 4);
      out += h.text(X(c.stop), 136, "Yellow starts here", { anchor: X(c.stop) < 120 ? "start" : "middle", cls: "w-label w-small" });
      // Stopping distance: reaction then braking.
      out += h.text(30, 170, "If the driver stops", { cls: "w-label-strong" });
      out += h.rect(X(c.stop), 180, X(c.brake) - X(c.stop), 26, "w-fill-amber");
      out += h.rect(X(c.brake), 180, bar - X(c.brake), 26, "w-fill");
      if (X(c.brake) - X(c.stop) > 70) out += h.text((X(c.stop) + X(c.brake)) / 2, 198, "reaction " + h.fmt(c.react, 0) + " ft", { anchor: "middle", cls: "w-label w-small" });
      if (bar - X(c.brake) > 80) out += h.text((X(c.brake) + bar) / 2, 198, "braking " + h.fmt(c.brake, 0) + " ft", { anchor: "middle", cls: "w-label w-small" });
      // Distance travelled during the yellow at constant speed.
      out += h.text(30, 236, "If the driver keeps going for Y", { cls: "w-label-strong" });
      out += h.dim(X(c.travel), 256, bar, 256, h.fmt(c.travel, 0) + " ft in " + h.fmt(c.Y, 2) + " s at " + h.fmt(c.speed, 1) + " ft/s", { offset: 22, labelCls: "w-label-accent w-small" });
      out += h.line(X(c.stop), 120, X(c.stop), 280, "w-dash");
      return out;
    },
  });

  PE.register("webster-cycle", {
    title: "Webster's optimum cycle length",
    height: 300,
    params: [
      { key: "L", label: "Total lost time L", min: 6, max: 20, step: 1, value: 12, unit: "s" },
      { key: "Y", label: "Sum of critical flow ratios Y", min: 0.3, max: 0.92, step: 0.01, value: 0.6 },
    ],
    compute: function (v) {
      var Yc = Math.min(Math.max(v.Y, 0), 0.95);
      var C = (1.5 * v.L + 5) / (1 - Yc);
      return { Y: Yc, C: C, green: C - v.L, num: 1.5 * v.L + 5 };
    },
    outputs: function (v, c) {
      var f = PE.helpers.fmt;
      return [
        { label: "1.5L + 5", value: f(c.num, 1) + " s" },
        { label: "1 − Y", value: f(1 - c.Y, 2) },
        { label: "C₀", value: f(c.C, 1) + " s", strong: true },
        { label: "Effective green C₀ − L", value: f(c.green, 1) + " s" },
      ];
    },
    note: function (v, c) {
      if (c.Y >= 0.85) return "As Y nears 1 the cycle grows without limit: the intersection is close to capacity, and no cycle length leaves enough green for everyone.";
      return "Going from Y to Y + 0.1 adds more seconds the closer Y already is to 1. The curve is gentle on the left and steep on the right.";
    },
    draw: function (v, c, h) {
      var y0 = 0.2, y1 = 0.92;
      var cmax = c.num / (1 - y1);
      var X = h.scale(y0, y1, 70, 610), Y = h.scale(0, cmax * 1.05, 250, 20);
      var out = h.gridY(h.ticks(0, cmax, 4), Y, 70, 610, function (t) { return h.fmt(t, 0) + " s"; });
      out += h.line(70, 250, 610, 250, "w-thin");
      var pts = [];
      for (var i = 0; i <= 72; i++) { var yy = y0 + (y1 - y0) * i / 72; pts.push([X(yy), Y(c.num / (1 - yy))]); }
      out += h.poly(pts, "w-accent");
      out += h.line(X(c.Y), Y(c.C), X(c.Y), 250, "w-dash");
      out += h.circle(X(c.Y), Y(c.C), 6, "w-dot-amber");
      var left = X(c.Y) > 420;
      out += h.text(X(c.Y) + (left ? -10 : 10), Y(c.C) - 8, "C₀ = " + h.fmt(c.C, 0) + " s", { anchor: left ? "end" : "start", cls: "w-label-amber" });
      [0.2, 0.4, 0.6, 0.8].forEach(function (t) { out += h.text(X(t), 268, h.fmt(t, 1), { anchor: "middle", cls: "w-label w-small" }); });
      out += h.text(340, 290, "Sum of critical flow ratios Y", { anchor: "middle", cls: "w-label" });
      return out;
    },
  });
})();
