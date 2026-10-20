// Interactive tutorials: widgets (explorers and figures), in-tutorial
// checks, and step-by-step worked examples.
//
// A topic's widgets live in static/js/widgets/<code>.js and register here:
//
//   PEWidgets.register("vertical-curve", {
//     params: [{key: "g1", label: "Entering grade", min: -6, max: 6, step: 0.5, value: 3, unit: "%"}],
//     compute: function (v) { return {...derived numbers...}; },
//     outputs: function (v, c) { return [{label: "High point", value: "10+50.00", strong: true}]; },
//     note: function (v, c) { return "One sentence on what the picture shows now."; },
//     draw: function (v, c, h) { return "<svg markup inside a 0 0 640 H viewBox>"; },
//     height: 300,
//   });
//
// A param may instead be a choice: {key, label, options: [{value, label}], value}.
// compute, outputs, note and draw must be pure functions of the values, so
// the same widget draws an explorer (with sliders), a fixed figure, and the
// illustration under a check's explanation. Runs in a browser or in Node
// (scripts/check_widgets.js).
(function (root) {
  "use strict";

  var registry = {};
  var W = 640;

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function fmt(x, d) {
    if (x === null || x === undefined || isNaN(x)) return "—";
    d = d === undefined ? 2 : d;
    return Number(x).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
  }

  function station(ft, d) {
    d = d === undefined ? 2 : d;
    var sign = ft < 0 ? "-" : "";
    ft = Math.abs(ft);
    var h = Math.floor(ft / 100);
    var rest = (ft - h * 100).toFixed(d);
    if (Number(rest) >= 100) { h += 1; rest = (0).toFixed(d); }
    var pad = d ? 3 + d : 2;
    while (rest.length < pad) rest = "0" + rest;
    return sign + h + "+" + rest;
  }

  function attrs(o) {
    var out = "";
    for (var k in o) if (o[k] !== undefined && o[k] !== null && o[k] !== false) out += " " + k + '="' + esc(o[k]) + '"';
    return out;
  }

  // SVG helpers handed to every draw(). Classes are styled in app.css:
  // w-line, w-thin, w-dash, w-accent, w-amber, w-bad, w-muted, w-road,
  // w-fill, w-fill-amber, w-fill-muted, w-grid, w-label, w-label-strong,
  // w-label-accent, w-label-amber, w-small.
  var h = {
    W: W,
    esc: esc,
    fmt: fmt,
    station: station,
    line: function (x1, y1, x2, y2, cls) {
      return "<line" + attrs({ x1: r(x1), y1: r(y1), x2: r(x2), y2: r(y2), "class": cls || "w-line" }) + "/>";
    },
    path: function (d, cls) { return "<path" + attrs({ d: d, "class": cls || "w-line" }) + "/>"; },
    poly: function (pts, cls) {
      return "<polyline" + attrs({ points: pts.map(function (p) { return r(p[0]) + "," + r(p[1]); }).join(" "), "class": cls || "w-line" }) + "/>";
    },
    polygon: function (pts, cls) {
      return "<polygon" + attrs({ points: pts.map(function (p) { return r(p[0]) + "," + r(p[1]); }).join(" "), "class": cls || "w-fill" }) + "/>";
    },
    circle: function (x, y, rad, cls) { return "<circle" + attrs({ cx: r(x), cy: r(y), r: rad, "class": cls || "w-dot" }) + "/>"; },
    rect: function (x, y, w, hh, cls, rx) {
      return "<rect" + attrs({ x: r(x), y: r(y), width: r(Math.max(0, w)), height: r(Math.max(0, hh)), rx: rx || 0, "class": cls || "w-fill" }) + "/>";
    },
    text: function (x, y, s, opt) {
      opt = opt || {};
      return "<text" + attrs({ x: r(x), y: r(y), "text-anchor": opt.anchor || "start", "class": opt.cls || "w-label", transform: opt.rotate ? "rotate(" + opt.rotate + " " + r(x) + " " + r(y) + ")" : null }) + ">" + esc(s) + "</text>";
    },
    arrow: function (x1, y1, x2, y2, cls) {
      return "<line" + attrs({ x1: r(x1), y1: r(y1), x2: r(x2), y2: r(y2), "class": cls || "w-line", "marker-end": "url(#w-arrow)" }) + "/>";
    },
    // A dimension line with arrows at both ends and a label at its middle.
    dim: function (x1, y1, x2, y2, label, opt) {
      opt = opt || {};
      var mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
      var off = opt.offset === undefined ? -6 : opt.offset;
      return "<line" + attrs({ x1: r(x1), y1: r(y1), x2: r(x2), y2: r(y2), "class": opt.cls || "w-thin", "marker-start": "url(#w-arrow-rev)", "marker-end": "url(#w-arrow)" }) + "/>" +
        h.text(mx + (opt.dx || 0), my + off, label, { anchor: "middle", cls: opt.labelCls || "w-label w-small" });
    },
    // Linear scale from a data range to a pixel range.
    scale: function (d0, d1, p0, p1) {
      var f = function (x) { return p0 + (x - d0) / ((d1 - d0) || 1) * (p1 - p0); };
      f.invert = function (p) { return d0 + (p - p0) / ((p1 - p0) || 1) * (d1 - d0); };
      return f;
    },
    // Horizontal grid lines with labels at the left edge.
    gridY: function (ticks, y, x0, x1, label) {
      return ticks.map(function (t) {
        return h.line(x0, y(t), x1, y(t), "w-grid") + h.text(x0 - 6, y(t) + 4, label ? label(t) : String(t), { anchor: "end", cls: "w-label w-small" });
      }).join("");
    },
    ticks: function (lo, hi, n) {
      var span = hi - lo, step = Math.pow(10, Math.floor(Math.log10(span / n)));
      var err = span / n / step;
      if (err >= 7.5) step *= 10; else if (err >= 3.5) step *= 5; else if (err >= 1.5) step *= 2;
      var out = [];
      for (var t = Math.ceil(lo / step) * step; t <= hi + 1e-9; t += step) out.push(Math.round(t / step) * step);
      return out;
    },
  };

  function r(x) { return Math.round(x * 10) / 10; }

  function defaults(spec, config) {
    var v = {};
    spec.params.forEach(function (p) { v[p.key] = p.value; });
    var given = (config && config.values) || {};
    for (var k in given) v[k] = given[k];
    return v;
  }

  function render(spec, v) {
    var c = spec.compute ? spec.compute(v) : {};
    var height = typeof spec.height === "function" ? spec.height(v, c) : (spec.height || 300);
    var svg = '<svg class="w-svg" viewBox="0 0 ' + W + " " + height + '" role="img" aria-label="' + esc(spec.title || "Diagram") + '">' +
      '<defs><marker id="w-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="w-marker"/></marker>' +
      '<marker id="w-arrow-rev" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M10 0L0 5L10 10z" class="w-marker"/></marker></defs>' +
      spec.draw(v, c, h) + "</svg>";
    return {
      computed: c,
      svg: svg,
      outputs: spec.outputs ? spec.outputs(v, c) : [],
      note: spec.note ? spec.note(v, c) : "",
    };
  }

  var PE = (root.PEWidgets = {
    register: function (name, spec) { registry[name] = spec; },
    get: function (name) { return registry[name]; },
    names: function () { return Object.keys(registry); },
    helpers: h,
    defaults: defaults,
    render: render,
  });

  if (typeof document === "undefined") return;

  // --- Mounting widgets -------------------------------------------------------

  function mount(el) {
    var name = el.getAttribute("data-widget");
    var spec = registry[name];
    if (!spec) { el.innerHTML = '<p class="note">Diagram "' + esc(name) + '" is not available.</p>'; return; }
    var config = {};
    try { config = JSON.parse(el.getAttribute("data-config") || "{}"); } catch (e) { config = {}; }
    var fixed = el.getAttribute("data-mode") !== "explorer";
    var values = defaults(spec, config);
    el.innerHTML = '<div class="w-figure"></div>' + (fixed ? "" : '<div class="w-controls"></div>') + '<div class="w-readout"></div><p class="w-note"></p>';
    var fig = el.querySelector(".w-figure"), out = el.querySelector(".w-readout"), note = el.querySelector(".w-note");

    function update() {
      var res = render(spec, values);
      fig.innerHTML = res.svg;
      out.innerHTML = res.outputs.map(function (o) {
        return '<div class="w-out' + (o.strong ? " is-strong" : "") + '"><span>' + esc(o.label) + "</span><strong>" + esc(o.value) + "</strong></div>";
      }).join("");
      note.textContent = res.note || "";
      note.hidden = !res.note;
    }

    if (!fixed) {
      var controls = el.querySelector(".w-controls");
      var shown = config.params ? spec.params.filter(function (p) { return config.params.indexOf(p.key) >= 0; }) : spec.params;
      shown.forEach(function (p) {
        var id = "w-" + name + "-" + p.key + "-" + Math.random().toString(36).slice(2, 7);
        var wrap = document.createElement("div");
        wrap.className = "w-control";
        if (p.options) {
          wrap.innerHTML = '<label for="' + id + '">' + esc(p.label) + '</label><select id="' + id + '">' +
            p.options.map(function (o) { return '<option value="' + esc(o.value) + '"' + (String(o.value) === String(values[p.key]) ? " selected" : "") + ">" + esc(o.label) + "</option>"; }).join("") + "</select>";
          wrap.querySelector("select").addEventListener("change", function (e) {
            var raw = e.target.value;
            values[p.key] = isNaN(Number(raw)) ? raw : Number(raw);
            update();
          });
        } else {
          wrap.innerHTML = '<label for="' + id + '">' + esc(p.label) + ' <output>' + fmt(values[p.key], p.decimals === undefined ? decimalsOf(p.step) : p.decimals) + (p.unit ? " " + esc(p.unit) : "") + '</output></label>' +
            '<input type="range" id="' + id + '" min="' + p.min + '" max="' + p.max + '" step="' + p.step + '" value="' + values[p.key] + '">';
          var input = wrap.querySelector("input"), output = wrap.querySelector("output");
          input.addEventListener("input", function () {
            values[p.key] = Number(input.value);
            output.textContent = fmt(values[p.key], p.decimals === undefined ? decimalsOf(p.step) : p.decimals) + (p.unit ? " " + p.unit : "");
            update();
          });
        }
        controls.appendChild(wrap);
      });
      var reset = document.createElement("button");
      reset.type = "button";
      reset.className = "btn btn-small btn-ghost";
      reset.textContent = "Reset";
      reset.addEventListener("click", function () { mount(el); });
      controls.appendChild(reset);
    }
    update();
  }

  function decimalsOf(step) {
    var s = String(step);
    return s.indexOf(".") >= 0 ? s.split(".")[1].length : 0;
  }

  // --- Checks -----------------------------------------------------------------

  function csrf() {
    var m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? m[1] : "";
  }

  function log(block, correct, response, tries) {
    var url = block.getAttribute("data-log-url");
    if (!url || !window.fetch) return;
    fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrf() },
      body: JSON.stringify({ correct: correct, response: response, tries: tries }),
      credentials: "same-origin",
    }).catch(function () {});
  }

  function reveal(block) {
    var ex = block.querySelector("[data-explanation]");
    if (!ex || !ex.hidden) return;
    ex.hidden = false;
    ex.querySelectorAll("[data-widget]").forEach(mount);
    progress();
  }

  function setupCheck(block) {
    var form = block.querySelector("form");
    var feedback = block.querySelector("[data-feedback]");
    var hint = block.querySelector("[data-hint]");
    var tries = 0;
    var done = false;
    block.querySelector("[data-show]").addEventListener("click", function () {
      done = true;
      block.classList.add("is-answered");
      log(block, false, "(revealed)", tries);
      reveal(block);
    });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (done) return;
      var correct, response, why = "";
      var numeric = form.querySelector("input[name=value]");
      if (numeric) {
        response = numeric.value.replace(/,/g, "").trim();
        if (response === "" || isNaN(Number(response))) { feedback.textContent = "Enter a number."; feedback.className = "t-feedback"; return; }
        correct = Math.abs(Number(response) - Number(form.getAttribute("data-answer"))) <= Number(form.getAttribute("data-tolerance"));
      } else {
        var picked = form.querySelector("input[name=choice]:checked");
        if (!picked) { feedback.textContent = "Pick an answer first."; feedback.className = "t-feedback"; return; }
        response = picked.value;
        correct = picked.getAttribute("data-correct") === "1";
        why = picked.getAttribute("data-why") || "";
        form.querySelectorAll(".choice").forEach(function (c) { c.classList.remove("is-wrong"); });
        picked.closest(".choice").classList.add(correct ? "is-correct" : "is-wrong");
      }
      tries += 1;
      if (correct) {
        done = true;
        feedback.innerHTML = "<strong>Right.</strong> " + esc(why);
        feedback.className = "t-feedback is-good";
        block.classList.add("is-answered");
        log(block, true, response, tries);
        reveal(block);
      } else if (tries === 1) {
        feedback.innerHTML = "<strong>Not yet.</strong> " + esc(why) + (hint ? " Look at the hint, then try again." : " Try again.");
        feedback.className = "t-feedback is-bad";
        if (hint) hint.hidden = false;
      } else {
        done = true;
        feedback.innerHTML = "<strong>Not quite.</strong> " + esc(why) + " Here is the full explanation.";
        feedback.className = "t-feedback is-bad";
        block.classList.add("is-answered");
        if (!numeric) form.querySelectorAll("input[data-correct='1']").forEach(function (i) { i.closest(".choice").classList.add("is-correct"); });
        log(block, false, response, tries);
        reveal(block);
      }
    });
  }

  // --- Worked examples --------------------------------------------------------

  function setupExample(block) {
    var steps = Array.prototype.slice.call(block.querySelectorAll("[data-step]"));
    var btn = block.querySelector("[data-next-step]");
    var i = 0;
    function label() {
      if (i >= steps.length) { btn.hidden = true; var a = block.querySelector("[data-final]"); if (a) a.hidden = false; block.querySelectorAll("[data-final] [data-widget]").forEach(mount); block.classList.add("is-answered"); progress(); return; }
      btn.textContent = "Show step " + (i + 1);
    }
    btn.addEventListener("click", function () {
      var s = steps[i];
      var think = s.querySelector("[data-think]");
      var text = s.querySelector("[data-step-text]");
      if (s.hidden) {
        s.hidden = false;
        if (think) { text.hidden = true; btn.textContent = "Reveal step " + (i + 1); return; }
      } else if (text.hidden) {
        text.hidden = false;
      }
      i += 1;
      label();
    });
    block.querySelector("[data-show-all]").addEventListener("click", function () {
      steps.forEach(function (s) { s.hidden = false; var t = s.querySelector("[data-step-text]"); if (t) t.hidden = false; });
      i = steps.length;
      label();
    });
    label();
  }

  function progress() {
    var el = document.querySelector("[data-tutorial-progress]");
    if (!el) return;
    var all = document.querySelectorAll("[data-interactive]").length;
    var done = document.querySelectorAll("[data-interactive].is-answered").length;
    el.textContent = done + " of " + all + " activities done";
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".t-block [data-widget]").forEach(function (el) {
      if (!el.closest("[data-explanation]") && !el.closest("[data-final]")) mount(el);
    });
    document.querySelectorAll("[data-check]").forEach(setupCheck);
    document.querySelectorAll("[data-example]").forEach(setupExample);
    progress();
  });
})(typeof window !== "undefined" ? window : globalThis);
