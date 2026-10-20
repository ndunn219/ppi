// SD1 Stopping sight distance: reaction distance plus braking distance,
// SSD = 1.47Vt + V² / (30((a/32.2) ± G)), a = 11.2 ft/s².
(function () {
  "use strict";
  var PE = (typeof window !== "undefined" ? window : globalThis).PEWidgets;
  var A = 11.2, G = 32.2;

  function ssd(V, t, grade) {
    var f = A / G + grade / 100;
    var react = 1.47 * V * t;
    var brake = f > 0.01 ? V * V / (30 * f) : V * V / 0.3;
    return { react: react, brake: brake, total: react + brake, f: f };
  }

  PE.register("ssd-bars", {
    title: "Stopping sight distance: reaction plus braking",
    height: 300,
    params: [
      { key: "V", label: "Design speed V", min: 20, max: 80, step: 5, value: 60, unit: "mi/h" },
      { key: "t", label: "Brake reaction time t", min: 1, max: 3.5, step: 0.1, value: 2.5, unit: "s" },
      { key: "G", label: "Grade (+ up, − down)", min: -8, max: 8, step: 0.5, value: 0, unit: "%" },
    ],
    compute: function (v) {
      var now = ssd(v.V, v.t, v.G), level = ssd(v.V, v.t, 0);
      return { now: now, level: level };
    },
    outputs: function (v, c) {
      var f = PE.helpers.fmt;
      return [
        { label: "Reaction 1.47Vt", value: f(c.now.react, 1) + " ft" },
        { label: "Braking V²/(30(a/g ± G))", value: f(c.now.brake, 1) + " ft" },
        { label: "SSD", value: f(c.now.total, 0) + " ft", strong: true },
        { label: "a/g ± G", value: f(c.now.f, 3) },
      ];
    },
    note: function (v, c) {
      var f = PE.helpers.fmt;
      if (v.G === 0) return "On level ground. Reaction distance grows in proportion to speed; braking distance grows with the square of speed.";
      var diff = c.now.total - c.level.total;
      return (v.G < 0 ? "Downhill" : "Uphill") + ", SSD is " + f(Math.abs(diff), 0) + " ft " + (diff > 0 ? "longer" : "shorter") + " than on level ground (the grey bar). Only the braking part changes.";
    },
    draw: function (v, c, h) {
      var maxD = Math.max(c.now.total, c.level.total) * 1.12;
      var X = h.scale(0, maxD, 40, 610);
      var out = "";
      // Road with car and object.
      out += h.rect(20, 34, 600, 40, "w-fill-muted");
      out += h.line(20, 54, 620, 54, "w-dash");
      out += h.rect(X(0) - 4, 44, 30, 16, "w-fill-amber", 4);
      out += h.rect(X(c.now.total) - 5, 40, 10, 18, "w-fill-bad", 2);
      out += h.text(X(c.now.total), 30, "object", { anchor: "middle", cls: "w-label w-small" });
      out += h.text(40, 96, v.G === 0 ? "Level grade" : (v.G > 0 ? "+" : "") + h.fmt(v.G, 1) + "% grade", { cls: "w-label-strong" });
      // Current grade: reaction then braking.
      out += h.rect(X(0), 106, X(c.now.react) - X(0), 34, "w-fill-amber");
      out += h.rect(X(c.now.react), 106, X(c.now.total) - X(c.now.react), 34, "w-fill");
      if (X(c.now.react) - X(0) > 90) out += h.text((X(0) + X(c.now.react)) / 2, 127, "reaction " + h.fmt(c.now.react, 0) + " ft", { anchor: "middle", cls: "w-label w-small" });
      if (X(c.now.total) - X(c.now.react) > 90) out += h.text((X(c.now.react) + X(c.now.total)) / 2, 127, "braking " + h.fmt(c.now.brake, 0) + " ft", { anchor: "middle", cls: "w-label w-small" });
      out += h.dim(X(0), 160, X(c.now.total), 160, "SSD = " + h.fmt(c.now.total, 0) + " ft", { offset: 18, labelCls: "w-label-accent" });
      // Level grade for comparison.
      out += h.text(40, 212, "Same speed on level ground", { cls: "w-label" });
      out += h.rect(X(0), 222, X(c.level.react) - X(0), 22, "w-fill-muted");
      out += h.rect(X(c.level.react), 222, X(c.level.total) - X(c.level.react), 22, "w-fill-muted");
      out += h.line(X(c.level.react), 222, X(c.level.react), 244, "w-thin");
      out += h.text(Math.min(X(c.level.total) + 8, 560), 238, h.fmt(c.level.total, 0) + " ft", { cls: "w-label w-small" });
      [0, 0.25, 0.5, 0.75, 1].forEach(function (s) {
        var d = maxD * s;
        out += h.line(X(d), 262, X(d), 268, "w-thin") + h.text(X(d), 284, h.fmt(d, 0) + " ft", { anchor: "middle", cls: "w-label w-small" });
      });
      return out;
    },
  });

  PE.register("ssd-speed", {
    title: "Why speed matters so much: SSD against speed",
    height: 300,
    params: [
      { key: "V", label: "Design speed V", min: 20, max: 80, step: 5, value: 50, unit: "mi/h" },
      { key: "t", label: "Brake reaction time t", min: 1, max: 3.5, step: 0.1, value: 2.5, unit: "s" },
      { key: "G", label: "Grade (+ up, − down)", min: -8, max: 8, step: 0.5, value: 0, unit: "%" },
    ],
    compute: function (v) {
      return { now: ssd(v.V, v.t, v.G), double: v.V * 2 <= 80 ? ssd(v.V * 2, v.t, v.G) : null };
    },
    outputs: function (v, c) {
      var f = PE.helpers.fmt;
      var out = [
        { label: "Reaction at " + v.V + " mi/h", value: f(c.now.react, 0) + " ft" },
        { label: "Braking at " + v.V + " mi/h", value: f(c.now.brake, 0) + " ft" },
        { label: "SSD", value: f(c.now.total, 0) + " ft", strong: true },
      ];
      if (c.double) out.push({ label: "Braking at " + v.V * 2 + " mi/h", value: f(c.double.brake, 0) + " ft (×" + f(c.double.brake / c.now.brake, 1) + ")" });
      return out;
    },
    note: function (v, c) {
      if (c.double) return "Doubling the speed doubles the reaction distance but multiplies the braking distance by four.";
      return "Above 40 mi/h, braking is the larger share of stopping sight distance.";
    },
    draw: function (v, c, h) {
      var maxD = ssd(80, v.t, v.G).total * 1.05;
      var X = h.scale(20, 80, 70, 610), Y = h.scale(0, maxD, 250, 20);
      var out = h.gridY(h.ticks(0, maxD, 4), Y, 70, 610, function (t) { return h.fmt(t, 0); });
      out += h.line(70, 250, 610, 250, "w-thin");
      var tot = [], rea = [];
      for (var s = 20; s <= 80; s += 2) {
        var d = ssd(s, v.t, v.G);
        tot.push([X(s), Y(d.total)]);
        rea.push([X(s), Y(d.react)]);
      }
      out += h.poly(rea, "w-amber") + h.poly(tot, "w-accent");
      out += h.text(X(80) - 4, Y(ssd(80, v.t, v.G).react) - 8, "reaction only", { anchor: "end", cls: "w-label-amber" });
      out += h.text(X(70) - 6, Y(ssd(70, v.t, v.G).total) - 10, "SSD", { anchor: "end", cls: "w-label-accent" });
      out += h.line(X(v.V), Y(c.now.total), X(v.V), 250, "w-dash");
      out += h.circle(X(v.V), Y(c.now.total), 6, "w-dot");
      out += h.circle(X(v.V), Y(c.now.react), 5, "w-dot-amber");
      [20, 30, 40, 50, 60, 70, 80].forEach(function (s) { out += h.text(X(s), 268, s, { anchor: "middle", cls: "w-label w-small" }); });
      out += h.text(340, 290, "Design speed (mi/h)", { anchor: "middle", cls: "w-label" });
      out += h.text(16, 135, "Distance (ft)", { anchor: "middle", cls: "w-label", rotate: -90 });
      return out;
    },
  });
})();
