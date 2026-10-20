// TE3 Crash rates: crashes divided by exposure, for intersections (per
// million entering vehicles) and segments (per 100 million vehicle-miles).
(function () {
  "use strict";
  var PE = (typeof window !== "undefined" ? window : globalThis).PEWidgets;

  PE.register("crash-rate", {
    title: "Crash rate as crashes per unit of exposure",
    // Tall enough for the rows of crash dots, no more.
    height: function (v) { return 150 + Math.ceil(v.C / 20) * 18 + 50; },
    params: [
      { key: "mode", label: "Location", value: "intersection", options: [{ value: "intersection", label: "Intersection (per MEV)" }, { value: "segment", label: "Segment (per 100 MVMT)" }] },
      { key: "C", label: "Crashes in the period", min: 1, max: 80, step: 1, value: 20 },
      { key: "N", label: "Years of data", min: 1, max: 5, step: 1, value: 3, unit: "yr" },
      { key: "V", label: "ADT (entering, for an intersection)", min: 1000, max: 60000, step: 500, value: 20000, unit: "veh/day" },
      { key: "Lmi", label: "Segment length", min: 0.5, max: 10, step: 0.5, value: 2, unit: "mi" },
    ],
    compute: function (v) {
      var seg = v.mode === "segment";
      var vehicles = 365 * v.N * v.V;
      var exposure = seg ? vehicles * v.Lmi / 1e8 : vehicles / 1e6;
      return { seg: seg, vehicles: vehicles, vmt: vehicles * v.Lmi, exposure: exposure, rate: exposure > 0 ? v.C / exposure : 0, unit: seg ? "100 MVMT" : "MEV" };
    },
    outputs: function (v, c) {
      var f = PE.helpers.fmt;
      var out = [{ label: "Vehicles in the period, 365 × N × V", value: f(c.vehicles / 1e6, 2) + " million" }];
      if (c.seg) out.push({ label: "Vehicle-miles, × L", value: f(c.vmt / 1e6, 2) + " million" });
      out.push({ label: "Exposure", value: f(c.exposure, c.seg ? 3 : 2) + " " + c.unit });
      out.push({ label: "Crash rate R", value: f(c.rate, c.seg ? 1 : 2) + " per " + c.unit, strong: true });
      return out;
    },
    note: function (v, c) {
      var f = PE.helpers.fmt;
      if (c.seg) return "Each tick is a share of 100 million vehicle-miles. Longer or busier roads pile up more exposure, so the same crash count means a lower rate.";
      return "The bar is " + f(c.exposure, 1) + " million entering vehicles over " + v.N + " year" + (v.N > 1 ? "s" : "") + ". The rate is how many crashes fall on each million.";
    },
    draw: function (v, c, h) {
      var out = "";
      var maxE = Math.max(c.exposure * 1.15, c.seg ? 0.1 : 1);
      var X = h.scale(0, maxE, 40, 600);
      // Exposure bar with ticks.
      out += h.text(40, 30, "Exposure: " + h.fmt(c.exposure, c.seg ? 3 : 2) + " " + (c.seg ? "× 100 million vehicle-miles" : "million entering vehicles"), { cls: "w-label-strong" });
      out += h.rect(40, 42, X(c.exposure) - 40, 34, "w-fill", 4);
      var ticks = h.ticks(0, maxE, 6);
      // Enough decimals to tell neighbouring ticks apart (0.25 is not 0.2).
      var step = ticks.length > 1 ? ticks[1] - ticks[0] : 1, dec = 0;
      while (dec < 4 && Math.abs(step * Math.pow(10, dec) - Math.round(step * Math.pow(10, dec))) > 1e-9) dec++;
      ticks.forEach(function (t) {
        out += h.line(X(t), 76, X(t), 84, "w-thin");
        out += h.text(X(t), 98, h.fmt(t, dec), { anchor: "middle", cls: "w-label w-small" });
      });
      // Crashes as dots.
      out += h.text(40, 130, v.C + " crash" + (v.C === 1 ? "" : "es") + " in " + v.N + " year" + (v.N > 1 ? "s" : ""), { cls: "w-label-strong" });
      for (var i = 0; i < v.C; i++) {
        var col = i % 20, row = Math.floor(i / 20);
        out += h.circle(52 + col * 18, 150 + row * 18, 6, "w-dot-bad");
      }
      // The rate.
      var y = 150 + Math.ceil(v.C / 20) * 18 + 24;
      out += h.text(40, y, "R = crashes / exposure = " + v.C + " / " + h.fmt(c.exposure, c.seg ? 3 : 2) + " = " + h.fmt(c.rate, c.seg ? 1 : 2) + " per " + c.unit, { cls: "w-label-accent" });
      out += h.text(40, y + 22, c.seg
        ? "R = C × 10⁸ / (365 × N × V × L)"
        : "R = C × 10⁶ / (365 × N × V)", { cls: "w-label" });
      return out;
    },
  });
})();
