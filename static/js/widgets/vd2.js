// VD2 Vertical curve length for sight distance: crest sightlines, sag
// headlight beams, and where the S < L and S > L formulas meet.
(function () {
  "use strict";
  var PE = (typeof window !== "undefined" ? window : globalThis).PEWidgets;
  var TAN1 = Math.tan(Math.PI / 180);

  var KIND = { key: "kind", label: "Curve", value: "crest", options: [{ value: "crest", label: "Crest (driver sightline)" }, { value: "sag", label: "Sag (headlight beam)" }] };

  function lengths(kind, A, S) {
    var shortL, longL;
    if (kind === "sag") {
      shortL = A * S * S / (400 + 3.5 * S);
      longL = 2 * S - (400 + 3.5 * S) / A;
    } else {
      shortL = A * S * S / 2158;
      longL = 2 * S - 2158 / A;
    }
    var case1 = S < shortL;
    var L = case1 ? shortL : longL;
    return { shortL: shortL, longL: longL, case1: case1, L: Math.max(L, 0) };
  }

  function compute(v) {
    var r = lengths(v.kind, v.A, v.S);
    r.K = v.A > 0 ? r.L / v.A : 0;
    return r;
  }

  function outputs(v, c) {
    var f = PE.helpers.fmt;
    return [
      { label: v.kind === "sag" ? "S < L formula: AS² / (400 + 3.5S)" : "S < L formula: AS² / 2158", value: f(c.shortL, 0) + " ft" },
      { label: v.kind === "sag" ? "S > L formula: 2S − (400 + 3.5S)/A" : "S > L formula: 2S − 2158/A", value: f(c.longL, 0) + " ft" },
      { label: "Governs", value: c.case1 ? "S < L" : "S > L" },
      { label: "Minimum L", value: f(c.L, 0) + " ft", strong: true },
      { label: "K = L / A", value: f(c.K, 1) },
    ];
  }

  function note(v, c) {
    var f = PE.helpers.fmt;
    if (c.L <= 0) return "With A this small, the sight distance is available without any curve: the S > L formula gives a negative length, so no minimum governs.";
    if (c.case1) return "The S < L formula gives " + f(c.shortL, 0) + " ft, which is longer than S = " + f(v.S, 0) + " ft, so the assumption holds and L = " + f(c.L, 0) + " ft.";
    return "The S < L formula gives " + f(c.shortL, 0) + " ft, shorter than S = " + f(v.S, 0) + " ft, so the assumption fails. Use S > L: L = " + f(c.L, 0) + " ft.";
  }

  // Road elevation (ft) at x (ft from the middle of a symmetric curve).
  function road(kind, A, L, x) {
    var g = A / 200; // each grade, as a decimal
    var half = L / 2;
    var sgn = kind === "sag" ? 1 : -1;
    if (L <= 0) return sgn * g * Math.abs(x);
    var c = A / 100 / L;
    if (Math.abs(x) <= half) return sgn * c * x * x / 2;
    return sgn * (c * half * half / 2 + g * (Math.abs(x) - half));
  }

  function slope(kind, A, L, x) {
    var g = A / 200, sgn = kind === "sag" ? 1 : -1;
    if (L <= 0) return sgn * g * (x < 0 ? -1 : 1);
    var c = A / 100 / L;
    if (Math.abs(x) <= L / 2) return sgn * c * x;
    return sgn * g * (x < 0 ? -1 : 1);
  }

  // Where a headlight beam from xe first meets the road, or null.
  function beamHit(A, L, xe, reach) {
    var y0 = road("sag", A, L, xe) + 2;
    var m = slope("sag", A, L, xe) + TAN1;
    var step = Math.max(reach / 600, 0.5);
    for (var d = step; d <= reach; d += step) {
      if (y0 + m * d <= road("sag", A, L, xe + d)) return d;
    }
    return null;
  }

  PE.register("sight-profile", {
    title: "Sight distance over a crest or through a sag",
    height: 330,
    params: [
      KIND,
      { key: "A", label: "Algebraic difference A", min: 1, max: 10, step: 0.5, value: 5, unit: "%" },
      { key: "S", label: "Sight distance S", min: 150, max: 900, step: 25, value: 500, unit: "ft" },
    ],
    compute: compute,
    outputs: outputs,
    note: note,
    draw: function (v, c, h) {
      var L = c.L, A = v.A, S = v.S, kind = v.kind;
      var span = Math.max(S, L) * 0.65 + 60;
      var x0 = -span, x1 = span;
      var xe, xo, eyeY, objY, hit = null;

      if (kind === "crest") {
        // Eye and object S apart, centred on the crest. When S < L and L is
        // the minimum, the line between them is exactly tangent to the curve.
        xe = -S / 2;
        xo = S / 2;
        eyeY = road(kind, A, L, xe) + 3.5;
        objY = road(kind, A, L, xo) + 2.0;
      } else {
        // Headlight placed where the beam reaches the road soonest: at the
        // PVC when S < L, and on the approach tangent when S > L.
        if (c.case1 && L > 0) {
          xe = -L / 2;
          hit = beamHit(A, L, xe, span * 2);
        } else {
          var best = null;
          for (var i = 0; i <= 40; i++) {
            var cand = -L / 2 - S * i / 40;
            var d = beamHit(A, L, cand, span * 2);
            if (d !== null && (best === null || d < best.d)) best = { x: cand, d: d };
          }
          xe = best ? best.x : -S / 2;
          hit = best ? best.d : null;
        }
        eyeY = road(kind, A, L, xe) + 2.0;
      }

      // Fit the view (vertical scale exaggerated).
      var ys = [];
      for (var j = 0; j <= 80; j++) ys.push(road(kind, A, L, x0 + (x1 - x0) * j / 80));
      ys.push(eyeY + 2);
      if (objY !== undefined) ys.push(objY + 2);
      var lo = Math.min.apply(null, ys), hi = Math.max.apply(null, ys);
      var pad = Math.max((hi - lo) * 0.15, 2);
      var X = h.scale(x0, x1, 30, 610), Y = h.scale(lo - pad, hi + pad, 250, 22);

      var out = "";
      var pts = [], cpts = [];
      for (var n = 0; n <= 120; n++) {
        var x = x0 + (x1 - x0) * n / 120;
        pts.push([X(x), Y(road(kind, A, L, x))]);
        if (Math.abs(x) <= L / 2) cpts.push([X(x), Y(road(kind, A, L, x))]);
      }
      out += h.poly(pts, "w-line");
      if (cpts.length > 1) out += h.poly(cpts, "w-accent");
      if (L > 0) {
        out += h.line(X(-L / 2), Y(road(kind, A, L, -L / 2)) - 8, X(-L / 2), Y(road(kind, A, L, -L / 2)) + 8, "w-thin");
        out += h.line(X(L / 2), Y(road(kind, A, L, L / 2)) - 8, X(L / 2), Y(road(kind, A, L, L / 2)) + 8, "w-thin");
        out += h.text(X(-L / 2), Y(road(kind, A, L, -L / 2)) + 24, "PVC", { anchor: "middle", cls: "w-label-strong w-small" });
        out += h.text(X(L / 2), Y(road(kind, A, L, L / 2)) + 24, "PVT", { anchor: "middle", cls: "w-label-strong w-small" });
      }

      if (kind === "crest") {
        out += h.line(X(xe), Y(eyeY), X(xo), Y(objY), "w-amber");
        out += h.line(X(xe), Y(road(kind, A, L, xe)), X(xe), Y(eyeY), "w-thin");
        out += h.circle(X(xe), Y(eyeY), 5, "w-dot-amber");
        out += h.text(X(xe) - 8, Y(eyeY) - 8, "Eye 3.5 ft", { anchor: "end", cls: "w-label-amber w-small" });
        out += h.rect(X(xo) - 4, Y(objY), 8, Y(road(kind, A, L, xo)) - Y(objY), "w-fill-bad");
        out += h.text(X(xo) + 8, Y(objY) - 6, "Object 2.0 ft", { cls: "w-label-bad w-small" });
        out += h.dim(X(xe), 278, X(xo), 278, "S = " + h.fmt(S, 0) + " ft", { offset: -6 });
      } else {
        var reach = hit !== null ? hit : S;
        var yEnd = eyeY + (slope(kind, A, L, xe) + TAN1) * reach;
        out += h.line(X(xe), Y(eyeY), X(xe + reach), Y(yEnd), "w-amber");
        out += h.circle(X(xe), Y(eyeY), 5, "w-dot-amber");
        out += h.text(X(xe), Y(eyeY) - 12, "Headlight 2.0 ft", { anchor: X(xe) < 90 ? "start" : "middle", cls: "w-label-amber w-small" });
        out += h.circle(X(xe + reach), Y(yEnd), 4, "w-dot-bad");
        var hx = X(xe + reach);
        out += h.text(hx > 500 ? hx - 6 : hx + 8, Y(yEnd) - 12, "Beam meets road", { anchor: hx > 500 ? "end" : "start", cls: "w-label-bad w-small" });
        out += h.dim(X(xe), 278, X(xe + reach), 278, "S = " + h.fmt(reach, 0) + " ft", { offset: -6 });
      }
      if (L > 0) out += h.dim(X(-L / 2), 310, X(L / 2), 310, "L = " + h.fmt(L, 0) + " ft", { offset: 16 });
      else out += h.text(320, 318, "No curve needed", { anchor: "middle", cls: "w-label w-small" });
      out += h.text(610, 16, "Vertical scale exaggerated", { anchor: "end", cls: "w-label w-small" });
      return out;
    },
  });

  PE.register("length-chart", {
    title: "Minimum curve length against sight distance",
    height: 320,
    params: [
      KIND,
      { key: "A", label: "Algebraic difference A", min: 1, max: 10, step: 0.5, value: 5, unit: "%" },
      { key: "S", label: "Sight distance S", min: 150, max: 900, step: 25, value: 500, unit: "ft" },
    ],
    compute: compute,
    outputs: outputs,
    note: note,
    draw: function (v, c, h) {
      var sMin = 100, sMax = 1000, n = 90;
      var gov = [], shortPts = [], longPts = [], maxL = 0;
      for (var i = 0; i <= n; i++) {
        var s = sMin + (sMax - sMin) * i / n;
        var r = lengths(v.kind, v.A, s);
        maxL = Math.max(maxL, r.L, s);
        gov.push([s, r.L]);
        shortPts.push([s, r.shortL]);
        longPts.push([s, r.longL]);
      }
      maxL = Math.max(maxL, c.L) * 1.08;
      var X = h.scale(sMin, sMax, 84, 610), Y = h.scale(0, maxL, 270, 26);
      var clip = function (p) { return [X(p[0]), Y(Math.max(0, Math.min(p[1], maxL)))]; };
      var out = h.gridY(h.ticks(0, maxL, 4), Y, 84, 610, function (t) { return h.fmt(t, 0); });
      h.ticks(sMin, sMax, 5).forEach(function (t) {
        out += h.text(X(t), 290, h.fmt(t, 0), { anchor: "middle", cls: "w-label w-small" });
      });
      out += h.text(347, 312, "Sight distance S (ft)", { anchor: "middle", cls: "w-label w-small" });
      out += h.text(16, 150, "Minimum L (ft)", { anchor: "middle", cls: "w-label w-small", rotate: -90 });
      // The L = S line: on one side the S < L formula applies, on the other S > L.
      var lsTop = Math.min(sMax, maxL);
      out += h.line(X(sMin), Y(sMin), X(lsTop), Y(lsTop), "w-dash");
      out += h.text(X(lsTop) - 4, Y(lsTop) - 6, "L = S", { anchor: "end", cls: "w-label w-small" });
      out += h.poly(shortPts.filter(function (p) { return p[1] <= maxL; }).map(clip), "w-muted");
      out += h.poly(longPts.filter(function (p) { return p[1] > 0; }).map(clip), "w-muted");
      out += h.poly(gov.map(clip), "w-accent");
      out += h.line(X(v.S), Y(0), X(v.S), Y(c.L), "w-thin");
      out += h.circle(X(v.S), Y(c.L), 6, "w-dot-amber");
      out += h.text(X(v.S) + (v.S > 700 ? -10 : 10), Y(c.L) - 10, h.fmt(c.L, 0) + " ft", { anchor: v.S > 700 ? "end" : "start", cls: "w-label-amber" });
      out += h.text(610, 14, "Green: governing length. Grey: each formula on its own.", { anchor: "end", cls: "w-label w-small" });
      return out;
    },
  });
})();
