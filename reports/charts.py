"""Small server-drawn SVG charts, positioned in Python, drawn in templates."""

from datetime import date


def trend_chart(points, target, width=960, height=240):
    """The readiness range over time: a band from low to high, a line at mid,
    and the dashed target line."""
    rows = [p for p in points if p["mid"] is not None]
    left, right, top, bottom = 40, 12, 12, 28
    plot_w, plot_h = width - left - right, height - top - bottom
    if len(rows) < 2:
        return None

    d0 = date.fromisoformat(rows[0]["date"]).toordinal()
    d1 = date.fromisoformat(rows[-1]["date"]).toordinal()
    span = max(d1 - d0, 1)

    def x(p):
        return left + (date.fromisoformat(p["date"]).toordinal() - d0) / span * plot_w

    def y(v):
        return top + (1 - v) * plot_h

    upper = " ".join(f"{x(p):.1f},{y(p['high']):.1f}" for p in rows)
    lower = " ".join(f"{x(p):.1f},{y(p['low']):.1f}" for p in reversed(rows))
    return {
        "width": width,
        "height": height,
        "band": f"{upper} {lower}",
        "line": " ".join(f"{x(p):.1f},{y(p['mid']):.1f}" for p in rows),
        "dots": [{"x": round(x(p), 1), "y": round(y(p["mid"]), 1), "date": p["date"], "mid": p["mid"]} for p in rows],
        "target_y": round(y(target), 1),
        "ticks": [{"y": round(y(v), 1), "label": f"{int(v * 100)}%"} for v in (0.25, 0.5, 0.75, 1.0)],
        "left": left,
        "right": width - right,
        "first": rows[0]["date"],
        "last": rows[-1]["date"],
        "label_y": height - 8,
    }


def pacing_chart(cumulative, pace, width=960, height=240):
    """Cumulative minutes by question against the on-pace line."""
    n = len(cumulative)
    if not n:
        return None
    left, right, top, bottom = 44, 12, 12, 28
    plot_w, plot_h = width - left - right, height - top - bottom
    max_y = max(max(cumulative), n * pace) or 1

    def x(i):
        return left + i / max(n, 1) * plot_w

    def y(v):
        return top + (1 - v / max_y) * plot_h

    actual = " ".join(f"{x(i + 1):.1f},{y(v):.1f}" for i, v in enumerate(cumulative))
    step = 60 if max_y > 240 else (30 if max_y > 90 else 10)
    return {
        "width": width,
        "height": height,
        "actual": f"{x(0):.1f},{y(0):.1f} {actual}",
        "target": f"{x(0):.1f},{y(0):.1f} {x(n):.1f},{y(n * pace):.1f}",
        "ticks": [{"y": round(y(v), 1), "label": f"{v}m"} for v in range(0, int(max_y) + 1, step)],
        "left": left,
        "right": width - right,
        "n": n,
        "label_y": height - 8,
        "end_x": round(x(n), 1),
    }
