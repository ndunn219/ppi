// TE1 Traffic flow and peak hour factor: the flow-density relationship
// (Greenshields model) and the peak hour factor from four 15-minute counts.
(function () {
  "use strict";
  var PE = (typeof window !== "undefined" ? window : globalThis).PEWidgets;

  PE.register("flow-density", {
    title: "Flow versus density, Greenshields model",
    height: 320,
    params: [
      { key: "vf", label: "Free-flow speed v_f", min: 30, max: 80, step: 1, value: 60, unit: "mi/h" },
      { key: "kj", label: "Jam density k_j", min: 100, max: 250, step: 5, value: 200, unit: "veh/mi/ln" },
      { key: "k", label: "Density k", min: 0, max: 250, step: 1, value: 40, unit: "veh/mi/ln" },
    ],
    compute: function (v) {
      var kj = Math.max(v.kj, 1);
      var k = Math.min(Math.max(v.k, 0), kj);
      var speed = v.vf * (1 - k / kj);
      return {
        k: k, kj: kj, speed: speed, q: speed * k,
        qmax: v.vf * kj / 4, kc: kj / 2, vc: v.vf / 2,
        congested: k > kj / 2, clamped: v.k > kj,
      };
    },
    outputs: function (v, c) {
      var f = PE.helpers.fmt;
      return [
        { label: "Speed v", value: f(c.speed, 1) + " mi/h" },
        { label: "Flow q = k × v", value: f(c.q, 0) + " veh/h/ln", strong: true },
        { label: "Capacity q_max", value: f(c.qmax, 0) + " veh/h/ln" },
        { label: "At capacity", value: "k = " + f(c.kc, 0) + ", v = " + f(c.vc, 1) },
      ];
    },
    note: function (v, c) {
      var f = PE.helpers.fmt;
      if (c.clamped) return "Density can't exceed jam density, so the point sits at k_j: traffic is stopped and flow is zero.";
      if (c.k === 0) return "With no vehicles there is no flow, even though anyone driving could go at free-flow speed.";
      if (Math.abs(c.k - c.kc) < 0.5) return "This is capacity: half of jam density, half of free-flow speed, and the most flow the lane can carry.";
      return (c.congested ? "Congested side: " : "Uncongested side: ") + "the same flow of " + f(c.q, 0) + " veh/h/ln also occurs at " + f(c.kj - c.k, 0) + " veh/mi/ln on the " + (c.congested ? "uncongested" : "congested") + " side. Speed is the slope of the dashed line from the origin.";
    },
    draw: function (v, c, h) {
      var X = h.scale(0, c.kj, 70, 610), Y = h.scale(0, Math.max(c.qmax * 1.25, 1), 270, 25);
      var out = h.gridY(h.ticks(0, c.qmax * 1.2, 4), Y, 70, 610, function (t) { return h.fmt(t, 0); });
      out += h.line(70, 270, 610, 270, "w-thin");
      // Uncongested and congested halves.
      out += h.rect(X(c.kc), 25, X(c.kj) - X(c.kc), 245, "w-fill-muted");
      out += h.text(X(c.kc / 2), 44, "Uncongested", { anchor: "middle", cls: "w-label w-small" });
      out += h.text(X(c.kc * 1.5), 44, "Congested", { anchor: "middle", cls: "w-label w-small" });
      var pts = [];
      for (var i = 0; i <= 60; i++) { var k = c.kj * i / 60; pts.push([X(k), Y(v.vf * k * (1 - k / c.kj))]); }
      out += h.poly(pts, "w-accent");
      // Capacity.
      out += h.line(X(c.kc), Y(c.qmax), X(c.kc), 270, "w-dash");
      out += h.circle(X(c.kc), Y(c.qmax), 5.5, "w-dot-amber");
      out += h.text(X(c.kc), Y(c.qmax) - 10, "Capacity " + h.fmt(c.qmax, 0), { anchor: "middle", cls: "w-label-amber" });
      // Speed is the slope of the ray from the origin to the point.
      if (c.k > 0) out += h.line(X(0), Y(0), X(c.k), Y(c.q), "w-dash");
      out += h.line(X(c.k), Y(c.q), X(c.k), 270, "w-thin");
      out += h.circle(X(c.k), Y(c.q), 5.5, "w-dot");
      var right = X(c.k) < 420;
      // Near capacity the point and the capacity label coincide; drop its label lower.
      var nearCap = Math.abs(X(c.k) - X(c.kc)) < 70;
      out += h.text(X(c.k) + (right ? 9 : -9), Y(c.q) + (nearCap ? 36 : 16), "q = " + h.fmt(c.q, 0), { anchor: right ? "start" : "end", cls: "w-label-accent" });
      // Axes.
      out += h.text(X(0), 288, "0", { anchor: "middle", cls: "w-label w-small" });
      out += h.text(X(c.kc), 288, h.fmt(c.kc, 0), { anchor: "middle", cls: "w-label w-small" });
      out += h.text(X(c.kj), 288, h.fmt(c.kj, 0), { anchor: "middle", cls: "w-label w-small" });
      out += h.text(340, 310, "Density k (veh/mi/ln)", { anchor: "middle", cls: "w-label" });
      out += h.text(16, 150, "Flow q (veh/h/ln)", { anchor: "middle", cls: "w-label", rotate: -90 });
      return out;
    },
  });

  PE.register("phf-counts", {
    title: "Peak hour factor from four 15-minute counts",
    height: 300,
    params: [
      { key: "c1", label: "Count, 0 to 15 min", min: 50, max: 800, step: 10, value: 420, unit: "veh" },
      { key: "c2", label: "Count, 15 to 30 min", min: 50, max: 800, step: 10, value: 510, unit: "veh" },
      { key: "c3", label: "Count, 30 to 45 min", min: 50, max: 800, step: 10, value: 480, unit: "veh" },
      { key: "c4", label: "Count, 45 to 60 min", min: 50, max: 800, step: 10, value: 390, unit: "veh" },
    ],
    compute: function (v) {
      var counts = [v.c1, v.c2, v.c3, v.c4];
      var V = counts.reduce(function (a, b) { return a + b; }, 0);
      var peak = Math.max.apply(null, counts);
      var phf = peak > 0 ? V / (4 * peak) : 1;
      return { counts: counts, V: V, peak: peak, peakIndex: counts.indexOf(peak), phf: phf, rate: 4 * peak, avg: V / 4 };
    },
    outputs: function (v, c) {
      var f = PE.helpers.fmt;
      return [
        { label: "Hourly volume V", value: f(c.V, 0) + " veh" },
        { label: "Peak 15-min count", value: f(c.peak, 0) + " veh" },
        { label: "PHF = V / (4 × V15)", value: f(c.phf, 3), strong: true },
        { label: "Peak flow rate = V / PHF", value: f(c.rate, 0) + " veh/h", strong: true },
      ];
    },
    note: function (v, c) {
      var f = PE.helpers.fmt;
      if (c.phf > 0.999) return "All four counts are equal, so PHF = 1.00: the hour has no peak within it.";
      return "The dashed line is the average count (" + f(c.avg, 0) + "). PHF is the average divided by the peak: the flatter the hour, the closer PHF is to 1.";
    },
    draw: function (v, c, h) {
      var max = Math.max(c.peak * 1.2, 100);
      var Y = h.scale(0, max, 250, 30);
      var out = h.gridY(h.ticks(0, max, 4), Y, 70, 610, function (t) { return h.fmt(t, 0); });
      out += h.line(70, 250, 610, 250, "w-thin");
      var labels = ["0–15", "15–30", "30–45", "45–60"];
      for (var i = 0; i < 4; i++) {
        var x = 100 + i * 130, w = 90;
        var peak = i === c.peakIndex;
        out += h.rect(x, Y(c.counts[i]), w, 250 - Y(c.counts[i]), peak ? "w-fill-amber" : "w-fill", 4);
        out += h.text(x + w / 2, Y(c.counts[i]) - 7, h.fmt(c.counts[i], 0), { anchor: "middle", cls: peak ? "w-label-amber" : "w-label-strong" });
        out += h.text(x + w / 2, 268, labels[i] + " min", { anchor: "middle", cls: "w-label w-small" });
      }
      out += h.line(80, Y(c.avg), 610, Y(c.avg), "w-dash");
      out += h.text(606, Y(c.avg) - 6, "average " + h.fmt(c.avg, 0), { anchor: "end", cls: "w-label w-small" });
      out += h.text(340, 292, "Peak hour, by 15-minute period", { anchor: "middle", cls: "w-label" });
      return out;
    },
  });
})();
