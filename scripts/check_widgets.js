// Render every widget with its defaults and with every config the
// tutorials use, in Node, and fail on any exception, NaN in the output,
// or empty drawing.
//
//   .venv/bin/python manage.py check_tutorials --export /tmp/widget-configs.json
//   node scripts/check_widgets.js /tmp/widget-configs.json [code]
"use strict";
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..", "static", "js");
require(path.join(root, "tutorials.js"));
const only = process.argv[3];
for (const f of fs.readdirSync(path.join(root, "widgets"))) {
  if (f.endsWith(".js") && (!only || f === only.toLowerCase() + ".js")) require(path.join(root, "widgets", f));
}
const PE = globalThis.PEWidgets;
const configs = process.argv[2] ? JSON.parse(fs.readFileSync(process.argv[2], "utf8")) : [];
let failures = 0;

function check(name, config, label) {
  const spec = PE.get(name);
  if (!spec) { console.log("MISSING", name, label); failures++; return; }
  try {
    const v = PE.defaults(spec, config);
    const res = PE.render(spec, v);
    const text = res.svg + JSON.stringify(res.outputs) + res.note;
    if (/NaN|undefined|Infinity/.test(text)) throw new Error("NaN/undefined/Infinity in output: " + text.match(/.{0,60}(NaN|undefined|Infinity).{0,30}/)[0]);
    if (res.svg.length < 300) throw new Error("drawing looks empty");
    // Sweep each numeric param across its range to catch edge cases.
    for (const p of spec.params) {
      if (p.options) { for (const o of p.options) PE.render(spec, Object.assign({}, v, { [p.key]: o.value })); continue; }
      for (const x of [p.min, (p.min + p.max) / 2, p.max]) {
        const r = PE.render(spec, Object.assign({}, v, { [p.key]: x }));
        const t = r.svg + JSON.stringify(r.outputs) + r.note;
        if (/NaN|undefined|Infinity/.test(t)) throw new Error(`NaN/undefined at ${p.key}=${x}`);
      }
    }
    console.log("ok", name, label);
  } catch (e) {
    failures++;
    console.log("FAIL", name, label, "-", e.message);
  }
}

for (const name of PE.names()) check(name, {}, "(defaults)");
for (const c of configs) if (!only || c.code === only.toUpperCase()) check(c.widget, c.config, `${c.code} block ${c.block}`);
console.log(failures ? `${failures} failure(s)` : "All widgets render.");
process.exit(failures ? 1 : 0);
