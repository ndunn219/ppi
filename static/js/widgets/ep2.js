// EP2 Flexible pavement structural number: a layered section drawn to
// thickness scale, with each layer's contribution a·D·m to SN.
(function () {
  "use strict";
  var PE = (typeof window !== "undefined" ? window : globalThis).PEWidgets;

  PE.register("pavement-section", {
    title: "Layers of a flexible pavement and their structural number",
    height: 340,
    params: [
      { key: "D1", label: "Asphalt thickness D₁", min: 1, max: 8, step: 0.5, value: 4, unit: "in" },
      { key: "a1", label: "Asphalt coefficient a₁", min: 0.3, max: 0.48, step: 0.01, value: 0.44 },
      { key: "D2", label: "Base thickness D₂", min: 0, max: 18, step: 0.5, value: 10, unit: "in" },
      { key: "a2", label: "Base coefficient a₂", min: 0.08, max: 0.16, step: 0.01, value: 0.14 },
      { key: "m2", label: "Base drainage m₂", min: 0.6, max: 1.4, step: 0.05, value: 1.0 },
      { key: "D3", label: "Subbase thickness D₃", min: 0, max: 20, step: 0.5, value: 8, unit: "in" },
      { key: "a3", label: "Subbase coefficient a₃", min: 0.06, max: 0.14, step: 0.01, value: 0.11 },
      { key: "m3", label: "Subbase drainage m₃", min: 0.6, max: 1.4, step: 0.05, value: 1.0 },
      { key: "SNreq", label: "Required SN", min: 1, max: 7, step: 0.1, value: 4.0 },
    ],
    compute: function (v) {
      var s1 = v.a1 * v.D1, s2 = v.a2 * v.D2 * v.m2, s3 = v.a3 * v.D3 * v.m3;
      var sn = s1 + s2 + s3;
      return { s1: s1, s2: s2, s3: s3, sn: sn, gap: sn - v.SNreq };
    },
    outputs: function (v, c) {
      var f = PE.helpers.fmt;
      return [
        { label: "Asphalt a₁D₁", value: f(c.s1) },
        { label: "Base a₂D₂m₂", value: f(c.s2) },
        { label: "Subbase a₃D₃m₃", value: f(c.s3) },
        { label: "SN provided", value: f(c.sn), strong: true },
        { label: c.gap >= 0 ? "Exceeds required by" : "Short of required by", value: f(Math.abs(c.gap)) },
      ];
    },
    note: function (v, c) {
      var f = PE.helpers.fmt;
      var top = [["asphalt", c.s1], ["base", c.s2], ["subbase", c.s3]].sort(function (a, b) { return b[1] - a[1]; })[0];
      var msg = c.gap >= 0 ? "The section provides SN " + f(c.sn) + ", enough for the required " + f(v.SNreq) + "." : "The section provides SN " + f(c.sn) + ", short of the required " + f(v.SNreq) + ".";
      return msg + " The " + top[0] + " contributes the most. Per inch, asphalt is worth a₁/a₂ = " + f(v.a1 / v.a2, 1) + " inches of base.";
    },
    draw: function (v, c, h) {
      var maxIn = 8 + 18 + 20;
      var px = 210 / maxIn;
      var x0 = 40, x1 = 220, y = 24;
      var layers = [
        { name: "Asphalt", D: v.D1, cls: "w-fill-muted", text: "Asphalt " + h.fmt(v.D1, 1) + " in × a₁ " + h.fmt(v.a1) + " = " + h.fmt(c.s1) },
        { name: "Base", D: v.D2, cls: "w-fill-amber", text: "Base " + h.fmt(v.D2, 1) + " in × a₂ " + h.fmt(v.a2) + " × m₂ " + h.fmt(v.m2) + " = " + h.fmt(c.s2) },
        { name: "Subbase", D: v.D3, cls: "w-fill", text: "Subbase " + h.fmt(v.D3, 1) + " in × a₃ " + h.fmt(v.a3) + " × m₃ " + h.fmt(v.m3) + " = " + h.fmt(c.s3) },
      ];
      var out = "";
      var labelY = [52, 120, 188];
      layers.forEach(function (L, i) {
        var hgt = L.D * px;
        if (hgt > 0) out += h.rect(x0, y, x1 - x0, hgt, L.cls);
        var mid = y + hgt / 2;
        if (hgt > 0) out += h.line(x1, mid, 236, labelY[i] - 4, "w-thin");
        out += h.text(242, labelY[i], L.text, { cls: i === 0 ? "w-label-strong" : "w-label-strong" });
        y += hgt;
      });
      // Subgrade below, with hatching.
      out += h.line(x0, y, x1, y, "w-line");
      for (var x = x0; x < x1; x += 14) out += h.line(x, y + 14, x + 10, y, "w-thin");
      out += h.text(x0, y + 30, "Subgrade", { cls: "w-label w-small" });
      out += h.text((x0 + x1) / 2, 18, "Section to scale (in)", { anchor: "middle", cls: "w-label w-small" });

      // Stacked SN bar against the required SN.
      var max = Math.max(c.sn, v.SNreq, 1) * 1.1;
      var X = h.scale(0, max, 60, 600);
      var by = 296;
      out += h.text(60, by - 12, "SN provided against SN required", { cls: "w-label w-small" });
      out += h.rect(X(0), by, X(c.s1) - X(0), 22, "w-fill-muted");
      out += h.rect(X(c.s1), by, X(c.s1 + c.s2) - X(c.s1), 22, "w-fill-amber");
      out += h.rect(X(c.s1 + c.s2), by, X(c.sn) - X(c.s1 + c.s2), 22, "w-fill");
      out += h.line(X(v.SNreq), by - 6, X(v.SNreq), by + 28, c.gap >= 0 ? "w-accent" : "w-bad");
      var reqRight = X(v.SNreq) > 520;
      out += h.text(X(v.SNreq) + (reqRight ? -6 : 6), by + 40, "Required " + h.fmt(v.SNreq, 1), { anchor: reqRight ? "end" : "start", cls: c.gap >= 0 ? "w-label-accent w-small" : "w-label-bad w-small" });
      out += h.text(Math.min(X(c.sn) + 6, 598), by + 16, h.fmt(c.sn), { anchor: X(c.sn) + 6 > 560 ? "end" : "start", cls: "w-label-strong w-small" });
      return out;
    },
  });
})();
