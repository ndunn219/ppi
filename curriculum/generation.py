"""Drawing problem instances from templates.

draw() picks parameters from a template's ranges, runs its solver and
returns everything a ProblemInstance stores: the stem with numbers filled
in, the answer, four shuffled choices (each wrong one tagged with the
mistake that produces it) and the worked steps.
"""

import math
import random
from dataclasses import asdict

from .solvers import REGISTRY, Redraw, station

MAX_TRIES = 60


def _draw_value(spec, rng):
    if isinstance(spec, dict):
        return rng.choice(spec["choices"])
    lo, hi, step = spec
    n = int(round((hi - lo) / step))
    value = lo + step * rng.randint(0, n)
    if all(isinstance(x, int) for x in spec):
        return int(value)
    return round(value, 6)


def format_answer(value, template):
    if template.answer_unit == "station":
        return station(value, template.decimals)
    text = f"{value:,.{template.decimals}f}"
    return f"{text} {template.answer_unit}".strip()


def _distinct(values, min_gap):
    """No two choices so close that a correct method could land on either."""
    for i, a in enumerate(values):
        for b in values[i + 1 :]:
            gap = abs(a - b)
            limit = float(min_gap) if min_gap is not None else 0.03 * max(abs(a), abs(b))
            if gap < limit:
                return False
    return True


def draw(template, rng=None):
    rng = rng or random.Random()
    fn = REGISTRY[template.solver]
    for _ in range(MAX_TRIES):
        params = {name: _draw_value(spec, rng) for name, spec in template.params.items()}
        try:
            solution = fn(params)
        except (Redraw, ZeroDivisionError, ValueError):
            continue
        values = [solution.answer] + [d.value for d in solution.distractors]
        if solution.answer <= 0 or any(v <= 0 for v in values):
            continue
        if not _distinct(values, getattr(template, "min_gap", None)):
            continue
        break
    else:
        raise RuntimeError(f"Could not draw a valid instance of {template.slug}")

    choices = [{"value": solution.answer, "label": format_answer(solution.answer, template), "cause": "", "note": ""}]
    for d in solution.distractors[:3]:
        choices.append({"value": d.value, "label": format_answer(d.value, template), "cause": d.cause, "note": d.note})
    rng.shuffle(choices)
    return {
        "params": params,
        "stem": template.stem.format(**params),
        "answer": solution.answer,
        "answer_label": format_answer(solution.answer, template),
        "choices": choices,
        "steps": [asdict(s) for s in solution.steps],
    }


def _sig(x, figures=2):
    """Round to significant figures for a readable range label."""
    if x == 0:
        return "0"
    digits = figures - 1 - int(math.floor(math.log10(abs(x))))
    value = round(x, digits)
    return f"{value:,.{max(digits, 0)}f}"


def estimate_buckets(answer, rng=None):
    """Four ranges for Estimate first, each twice the one before, one of
    which holds the answer. Doubling ranges test order of magnitude, which
    is what an estimate is for."""
    rng = rng or random.Random()
    k = rng.randint(0, 3)  # which bucket holds the answer
    lo0 = answer / 2 ** (k + rng.uniform(0.15, 0.85))
    buckets = []
    for i in range(4):
        lo, hi = lo0 * 2**i, lo0 * 2 ** (i + 1)
        buckets.append({"lo": lo, "hi": hi, "label": f"{_sig(lo)} to {_sig(hi)}", "correct": lo <= answer < hi})
    return buckets


UNIT_CONVERSIONS = [
    ("mi/h", "ft/s", 1.4667, 2, "1 mi/h = 5,280 ft / 3,600 s = 1.467 ft/s"),
    ("ft/s", "mi/h", 1 / 1.4667, 1, "1 ft/s = 3,600 / 5,280 mi/h = 0.682 mi/h"),
    ("ft³", "yd³", 1 / 27, 1, "1 yd³ = 27 ft³"),
    ("yd³", "ft³", 27, 0, "1 yd³ = 27 ft³"),
    ("acre", "ft²", 43560, 0, "1 acre = 43,560 ft²"),
    ("mi", "ft", 5280, 0, "1 mi = 5,280 ft"),
    ("%", "ft/ft", 0.01, 3, "a grade of 1% = 0.01 ft/ft"),
    ("km/h", "mi/h", 0.6214, 1, "1 km/h = 0.6214 mi/h"),
    ("veh/15 min", "veh/h", 4, 0, "4 fifteen-minute periods per hour"),
    ("ft³/s", "gal/min", 448.83, 0, "1 ft³/s = 448.8 gal/min"),
]


def units_question(rng=None):
    rng = rng or random.Random()
    src, dst, factor, decimals, rule = rng.choice(UNIT_CONVERSIONS)
    magnitude = rng.choice([1, 2, 3, 5, 8, 12, 15, 25, 40, 55, 65, 120, 350, 1200])
    if src == "%":
        magnitude = rng.choice([1, 2, 3, 4, 5, 6])
    answer = magnitude * factor
    return {
        "value": magnitude,
        "src": src,
        "dst": dst,
        "answer": round(answer, decimals),
        "decimals": decimals,
        "rule": rule,
    }
