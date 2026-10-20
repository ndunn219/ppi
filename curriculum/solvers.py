"""Solvers for problem templates.

A solver takes the drawn parameters and returns the answer, the worked
steps, and the wrong answers that named mistakes produce. Because every
distractor carries its cause, a wrong pick is diagnosed without guessing.

A solver may add derived values to `p` for the stem to print (a speed's
side-friction factor, say), and raises Redraw when the drawn numbers make
an unrealistic problem.

All formulas are the standard textbook forms. None of this content has
been reviewed by a licensed PE yet; see BUILD_LOG.md.
"""

import math
from dataclasses import dataclass, field

G_FT = 32.2  # ft/s²
MPH_TO_FPS = 1.47


class Redraw(Exception):
    """The drawn parameters make a problem that should not be shown."""


@dataclass
class Step:
    text: str
    wrong: str = ""
    why: str = ""


@dataclass
class Distractor:
    value: float
    cause: str
    note: str


@dataclass
class Solution:
    answer: float
    steps: list[Step]
    distractors: list[Distractor] = field(default_factory=list)


REGISTRY = {}


def solver(name):
    def register(fn):
        REGISTRY[name] = fn
        return fn

    return register


def fmt(x, d=2):
    return f"{x:,.{d}f}"


def station(ft, d=2):
    """12345.67 ft → '123+45.67'."""
    sign = "-" if ft < 0 else ""
    ft = abs(ft)
    hundreds = int(ft // 100)
    rest = ft - hundreds * 100
    return f"{sign}{hundreds}+{rest:0{3 + d if d else 2}.{d}f}"


# --- Traffic flow -----------------------------------------------------------


@solver("flow_rate")
def flow_rate(p):
    k, v, n = p["k"], p["v"], p["lanes"]
    q_lane = k * v
    q = q_lane * n
    return Solution(
        q,
        [
            Step("Flow, density and space mean speed are related by q = k × v."),
            Step(
                f"Per lane: q = {k} veh/mi/ln × {v} mi/h = {fmt(q_lane, 0)} veh/h/ln.",
                wrong=f"Per lane: q = {k} / {v} = {fmt(k / v, 2)} veh/h/ln.",
                why="Flow is density times speed, not density divided by speed.",
            ),
            Step(f"All {n} lanes: q = {fmt(q_lane, 0)} × {n} = {fmt(q, 0)} veh/h."),
        ],
        [
            Distractor(q_lane, "setup", "Gave the per-lane flow; the question asks for all lanes."),
            Distractor(q * MPH_TO_FPS, "units", "Converted mi/h to ft/s; density is per mile, so no conversion is needed."),
            Distractor(k * n * 60, "concept", "Multiplied by 60 as if speed were in miles per minute."),
        ],
    )


@solver("phf")
def phf(p):
    V, phf_true = p["V"], p["phf"]
    v15 = round(V / (4 * phf_true))
    p["V15"] = v15
    ans = V / (4 * v15)
    return Solution(
        ans,
        [
            Step("PHF = hourly volume / (4 × peak 15-minute volume)."),
            Step(
                f"PHF = {V} / (4 × {v15}) = {V} / {4 * v15} = {fmt(ans, 3)}.",
                wrong=f"PHF = (4 × {v15}) / {V} = {fmt(4 * v15 / V, 3)}.",
                why="The ratio is inverted; a PHF is never greater than 1.",
            ),
        ],
        [
            Distractor(4 * v15 / V, "concept", "Inverted the ratio; a PHF can't exceed 1.0."),
            Distractor(v15 / V, "setup", "Left out the factor of 4."),
            Distractor(V / (3 * v15), "misread", "Treated the peak count as a 20-minute count."),
        ],
    )


@solver("design_flow_rate")
def design_flow_rate(p):
    V, f = p["V"], p["phf"]
    ans = V / f
    return Solution(
        ans,
        [
            Step("The peak flow rate within the hour is v = V / PHF."),
            Step(
                f"v = {V} / {f} = {fmt(ans, 0)} veh/h.",
                wrong=f"v = {V} × {f} = {fmt(V * f, 0)} veh/h.",
                why="Multiplying by the PHF lowers the flow; the peak rate is higher than the hourly volume.",
            ),
        ],
        [
            Distractor(V * f, "concept", "Multiplied by the PHF; the peak rate must exceed the hourly volume."),
            Distractor(V / (4 * f), "setup", "Divided by 4 as well, giving a 15-minute volume, not an hourly rate."),
            Distractor(float(V), "misread", "Gave the hourly volume without the peak adjustment."),
        ],
    )


# --- Signals ----------------------------------------------------------------


@solver("yellow_interval")
def yellow_interval(p):
    V, G = p["V"], p["G"]
    t, a = 1.0, 10.0
    v = MPH_TO_FPS * V
    g = G / 100
    denom = 2 * a + 2 * G_FT * g
    y = t + v / denom
    return Solution(
        y,
        [
            Step("Yellow change interval: Y = t + v / (2a + 2Gg), with v in ft/s and G as a decimal."),
            Step(f"v = 1.47 × {V} = {fmt(v, 1)} ft/s; G = {G}% = {fmt(g, 2)}."),
            Step(
                f"2a + 2Gg = 2(10) + 2(32.2)({fmt(g, 2)}) = {fmt(denom, 2)} ft/s².",
                wrong=f"2a + 2Gg = 2(10) + 2(32.2)({fmt(-g, 2)}) = {fmt(2 * a - 2 * G_FT * g, 2)} ft/s².",
                why="The grade sign is flipped: an upgrade (positive G) helps the driver stop and shortens the interval.",
            ),
            Step(f"Y = 1.0 + {fmt(v, 1)} / {fmt(denom, 2)} = {fmt(y, 1)} s."),
        ],
        [
            Distractor(t + V / denom, "units", "Used mi/h in a formula that needs ft/s."),
            Distractor(t + v / (2 * a - 2 * G_FT * g), "setup", "Used the wrong sign for the grade."),
            Distractor(t + v / (a + G_FT * g), "arithmetic", "Dropped the factor of 2 in the denominator."),
        ],
    )


@solver("webster_cycle")
def webster_cycle(p):
    L = p["L"]
    ys = [p["y1"], p["y2"], p["y3"]]
    Y = sum(ys)
    if not 0.45 <= Y <= 0.85:
        raise Redraw
    p["Y"] = fmt(Y, 2)
    c = (1.5 * L + 5) / (1 - Y)
    return Solution(
        c,
        [
            Step("Webster's optimum cycle: C₀ = (1.5L + 5) / (1 − Y), where Y is the sum of critical flow ratios."),
            Step(f"Y = {ys[0]} + {ys[1]} + {ys[2]} = {fmt(Y, 2)}."),
            Step(
                f"C₀ = (1.5 × {L} + 5) / (1 − {fmt(Y, 2)}) = {fmt(1.5 * L + 5, 1)} / {fmt(1 - Y, 2)} = {fmt(c, 0)} s.",
                wrong=f"C₀ = (1.5 × {L} + 5) / {fmt(Y, 2)} = {fmt((1.5 * L + 5) / Y, 0)} s.",
                why="The denominator is 1 − Y, the share of time left over, not Y itself.",
            ),
        ],
        [
            Distractor((1.5 * L + 5) / Y, "concept", "Divided by Y instead of 1 − Y."),
            Distractor(1.5 * L + 5 / (1 - Y), "arithmetic", "Applied the division to the 5 only."),
            Distractor((L + 5) / (1 - Y), "misread", "Left out the 1.5 multiplier on lost time."),
        ],
    )


# --- Safety -----------------------------------------------------------------


@solver("crash_rate_intersection")
def crash_rate_intersection(p):
    C, N, V = p["C"], p["N"], p["V"]
    r = C * 1e6 / (365 * N * V)
    return Solution(
        r,
        [
            Step("Intersection crash rate per million entering vehicles: R = C × 10⁶ / (365 × N × V)."),
            Step(
                f"R = {C} × 1,000,000 / (365 × {N} × {V:,}) = {fmt(r, 2)} crashes per MEV.",
                wrong=f"R = {C} × 1,000,000 / (365 × {V:,}) = {fmt(C * 1e6 / (365 * V), 2)} crashes per MEV.",
                why="The crashes span N years, so the exposure needs N years of traffic too.",
            ),
        ],
        [
            Distractor(C * 1e6 / (365 * V), "setup", "Left out the number of years."),
            Distractor(C * 1e6 / (N * V), "units", "Left out 365 days per year; V is a daily volume."),
            Distractor(C * 1e8 / (365 * N * V), "concept", "Used the segment-rate multiplier of 10⁸."),
        ],
    )


@solver("crash_rate_segment")
def crash_rate_segment(p):
    C, N, V, L = p["C"], p["N"], p["V"], p["L"]
    r = C * 1e8 / (365 * N * V * L)
    return Solution(
        r,
        [
            Step("Segment crash rate per 100 million vehicle-miles: R = C × 10⁸ / (365 × N × V × L)."),
            Step(f"Exposure = 365 × {N} × {V:,} × {L} = {fmt(365 * N * V * L, 0)} vehicle-miles."),
            Step(
                f"R = {C} × 10⁸ / {fmt(365 * N * V * L, 0)} = {fmt(r, 1)} crashes per 100 MVMT.",
                wrong=f"R = {C} × 10⁶ / {fmt(365 * N * V * L, 0)} = {fmt(r / 100, 1)}.",
                why="Segment rates are per 100 million vehicle-miles, so the multiplier is 10⁸.",
            ),
        ],
        [
            Distractor(r / 100, "concept", "Used 10⁶, the intersection multiplier."),
            Distractor(r * L, "setup", "Left out the segment length."),
            Distractor(r * N, "setup", "Left out the number of years."),
        ],
    )


# --- Horizontal curves ------------------------------------------------------


@solver("hcurve_length")
def hcurve_length(p):
    R, D = p["R"], p["delta"]
    T = R * math.tan(math.radians(D / 2))
    L = R * math.radians(D)
    return Solution(
        L,
        [
            Step("Curve length: L = R × Δ × π / 180, with Δ in degrees."),
            Step(
                f"L = {R} × {D} × π / 180 = {fmt(L, 1)} ft.",
                wrong=f"L = {R} × {D} = {fmt(R * D, 0)} ft.",
                why="Δ must be in radians when multiplied by R.",
            ),
            Step(f"Check: L is shorter than the two tangents, 2T = 2R tan(Δ/2) = {fmt(2 * T, 1)} ft, as it must be."),
        ],
        [
            Distractor(T, "concept", "Gave the tangent length T, not the curve length L."),
            Distractor(2 * T, "setup", "Doubled the tangent length; the arc is shorter than two tangents."),
            Distractor(R * math.radians(D / 2), "arithmetic", "Used Δ/2 in the arc length."),
        ],
    )


@solver("hcurve_pt_station")
def hcurve_pt_station(p):
    R, D, PI = p["R"], p["delta"], p["PI"]
    p["PI_sta"] = station(PI)
    T = R * math.tan(math.radians(D / 2))
    L = R * math.radians(D)
    PC = PI - T
    PT = PC + L
    return Solution(
        PT,
        [
            Step(f"T = R tan(Δ/2) = {R} × tan({D / 2}°) = {fmt(T, 2)} ft."),
            Step(f"L = R Δ π / 180 = {fmt(L, 2)} ft."),
            Step(f"PC = PI − T = {station(PI)} − {fmt(T, 2)} = {station(PC)}."),
            Step(
                f"PT = PC + L = {station(PC)} + {fmt(L, 2)} = {station(PT)}.",
                wrong=f"PT = PI + T = {station(PI)} + {fmt(T, 2)} = {station(PI + T)}.",
                why="Stationing runs along the curve, not along the tangents, so PT = PC + L.",
            ),
        ],
        [
            Distractor(PI + T, "setup", "Added T to the PI; stations follow the arc, so PT = PC + L."),
            Distractor(PC, "misread", "Gave the PC station."),
            Distractor(PC + R * D / 100, "units", "Used Δ in degrees without converting to radians in L."),
        ],
    )


@solver("min_radius")
def min_radius(p):
    V, e = p["V"], p["e"]
    f = {40: 0.16, 45: 0.15, 50: 0.14, 55: 0.13, 60: 0.12, 65: 0.11, 70: 0.10}[V]
    p["f"] = f
    R = V**2 / (15 * (e + f))
    return Solution(
        R,
        [
            Step("Point-mass equation: e + f = V² / (15R), so R = V² / (15(e + f)), with V in mi/h."),
            Step(
                f"R = {V}² / (15 × ({e} + {f})) = {V**2:,} / {fmt(15 * (e + f), 2)} = {fmt(R, 0)} ft.",
                wrong=f"R = {V}² / (15 × {e} + {f}) = {fmt(V**2 / (15 * e + f), 0)} ft.",
                why="The 15 multiplies the whole sum e + f.",
            ),
        ],
        [
            Distractor(V**2 / (15 * e + f), "arithmetic", "Missing parentheses around e + f."),
            Distractor((MPH_TO_FPS * V) ** 2 / (15 * (e + f)), "units", "Converted to ft/s; the 15 already handles mi/h."),
            Distractor(V**2 / (15 * f), "setup", "Left out the superelevation."),
        ],
    )


@solver("required_superelevation")
def required_superelevation(p):
    V, R, f = p["V"], p["R"], p["f"]
    e = V**2 / (15 * R) - f
    if not 0.02 <= e <= 0.10:
        raise Redraw
    return Solution(
        e,
        [
            Step("Rearrange e + f = V² / (15R): e = V² / (15R) − f."),
            Step(f"V² / (15R) = {V**2:,} / (15 × {R:,}) = {fmt(V**2 / (15 * R), 3)}."),
            Step(
                f"e = {fmt(V**2 / (15 * R), 3)} − {f} = {fmt(e, 3)} ft/ft.",
                wrong=f"e = {fmt(V**2 / (15 * R), 3)} + {f} = {fmt(V**2 / (15 * R) + f, 3)} ft/ft.",
                why="Side friction supplies part of the force, so it is subtracted.",
            ),
        ],
        [
            Distractor(V**2 / (15 * R), "setup", "Left out side friction."),
            Distractor(V**2 / (15 * R) + f, "concept", "Added side friction instead of subtracting it."),
            Distractor((MPH_TO_FPS * V) ** 2 / (15 * R) - f, "units", "Converted to ft/s; the 15 already handles mi/h."),
        ],
    )


@solver("hsd_offset")
def hsd_offset(p):
    R, S = p["R"], p["S"]
    if S > 0.9 * R:
        raise Redraw
    ang = 28.65 * S / R
    M = R * (1 - math.cos(math.radians(ang)))
    return Solution(
        M,
        [
            Step("Horizontal sightline offset: M = R(1 − cos(28.65 S / R)), angle in degrees, R to the inside lane centerline."),
            Step(f"28.65 × {S} / {R:,} = {fmt(ang, 3)}°."),
            Step(
                f"M = {R:,} × (1 − cos {fmt(ang, 3)}°) = {fmt(M, 1)} ft.",
                wrong=f"M = {R:,} × (1 − cos {fmt(ang, 3)} rad) = {fmt(R * (1 - math.cos(ang)), 1)} ft.",
                why="The 28.65 factor gives degrees; the calculator must be in degree mode.",
            ),
        ],
        [
            Distractor(R * (1 - math.cos(S / R)), "setup", "Used the full angle S/R; the formula uses the half-angle S/(2R)."),
            Distractor(R * (1 - math.cos(ang)), "arithmetic", "Calculator in radian mode for a degree angle."),
            Distractor(R * math.tan(math.radians(ang)), "concept", "Computed R·tan(θ), a distance along the tangent, not the offset."),
        ],
    )


# --- Vertical curves --------------------------------------------------------


@solver("vcurve_elevation")
def vcurve_elevation(p):
    g1, g2, L = p["g1"], p["g2"], p["L"]
    if g1 == g2:
        raise Redraw
    PVI, E_pvi = p["PVI"], p["E_PVI"]
    x = p["x_frac"] * L
    PVC = PVI - L / 2
    E_pvc = E_pvi - g1 / 100 * L / 2
    sta = PVC + x
    p["PVI_sta"] = station(PVI)
    p["sta"] = station(sta)
    r = (g2 - g1) / 100 / (2 * L)
    y = E_pvc + g1 / 100 * x + r * x**2
    return Solution(
        y,
        [
            Step(f"PVC = PVI − L/2 = {station(PVI)} − {L / 2:g} = {station(PVC)}."),
            Step(f"PVC elevation = {E_pvi} − ({g1 / 100:.3f})({L / 2:g}) = {fmt(E_pvc, 2)} ft."),
            Step(f"x = {station(sta)} − {station(PVC)} = {x:g} ft from the PVC."),
            Step(
                f"y = E_PVC + g₁x + (g₂ − g₁)x² / (2L) = {fmt(E_pvc, 2)} + ({g1 / 100:.3f})({x:g}) + ({(g2 - g1) / 100:.3f})({x:g})² / (2 × {L}) = {fmt(y, 2)} ft.",
                wrong=f"y = {fmt(E_pvc, 2)} + ({g1 / 100:.3f})({x:g}) + ({(g1 - g2) / 100:.3f})({x:g})² / (2 × {L}) = {fmt(E_pvc + g1 / 100 * x - r * x**2, 2)} ft.",
                why="The rate of change of grade is g₂ − g₁, not g₁ − g₂.",
            ),
        ],
        [
            Distractor(E_pvi + g1 / 100 * x + r * x**2, "setup", "Started from the PVI as if it were the PVC."),
            Distractor(E_pvc + g1 / 100 * x - r * x**2, "concept", "Used g₁ − g₂ for the change in grade."),
            Distractor(E_pvc + g1 / 100 * x + (g2 - g1) / (2 * L) * x**2, "units", "Used grades in percent in the curve term."),
        ],
    )


@solver("vcurve_turning_point")
def vcurve_turning_point(p):
    g1, g2, L, PVI = p["g1"], p["g2"], p["L"], p["PVI"]
    if g1 * g2 >= 0:
        raise Redraw
    p["PVI_sta"] = station(PVI)
    p["kind"] = "high" if g1 > 0 else "low"
    PVC = PVI - L / 2
    x = -g1 * L / (g2 - g1)
    sta = PVC + x
    return Solution(
        sta,
        [
            Step(f"PVC = {station(PVI)} − {L / 2:g} = {station(PVC)}."),
            Step(
                f"The turning point is where the grade is zero: x = −g₁L / (g₂ − g₁) = −({g1})({L}) / ({g2} − {g1}) = {fmt(x, 2)} ft from the PVC.",
                wrong=f"x = −g₂L / (g₂ − g₁) = {fmt(-g2 * L / (g2 - g1), 2)} ft from the PVC.",
                why="The distance from the PVC uses the entering grade g₁.",
            ),
            Step(f"Station = {station(PVC)} + {fmt(x, 2)} = {station(sta)}."),
        ],
        [
            Distractor(PVI + x, "setup", "Measured x from the PVI instead of the PVC."),
            Distractor(PVI, "concept", "Assumed the turning point is at the PVI; it is only there for equal and opposite grades."),
            Distractor(PVC + (L - x), "misread", "Used the exit grade, which measures from the PVT."),
        ],
    )


def _ssd_crest(A, S):
    L = A * S**2 / 2158
    return L if S < L else 2 * S - 2158 / A


@solver("crest_length")
def crest_length(p):
    g1, g2, S = p["g1"], p["g2"], p["S"]
    A = abs(g1 - g2)
    if g1 <= g2 or A < 2:
        raise Redraw
    p["A"] = A
    L1 = A * S**2 / 2158
    case1 = S < L1
    L = L1 if case1 else 2 * S - 2158 / A
    if L <= 0:
        raise Redraw
    steps = [
        Step(f"A = |g₁ − g₂| = |{g1} − ({g2})| = {A}%."),
        Step(
            f"Try S < L: L = AS² / 2158 = {A} × {S}² / 2158 = {fmt(L1, 0)} ft.",
            wrong=f"Try S < L: L = AS² / (400 + 3.5S) = {fmt(A * S**2 / (400 + 3.5 * S), 0)} ft.",
            why="That is the sag (headlight) formula; a crest curve uses 2158 for 3.5 ft eye and 2.0 ft object heights.",
        ),
    ]
    if case1:
        steps.append(Step(f"{S} < {fmt(L1, 0)}, so the assumption holds: L = {fmt(L, 0)} ft."))
    else:
        steps.append(Step(f"{S} > {fmt(L1, 0)}, so use S > L: L = 2S − 2158/A = {fmt(L, 0)} ft."))
    other = 2 * S - 2158 / A if case1 else L1
    return Solution(
        L,
        steps,
        [
            Distractor(other, "method", "Used the formula for the other S-versus-L case without checking."),
            Distractor(A * S**2 / (400 + 3.5 * S), "method", "Used the sag (headlight) formula on a crest curve."),
            Distractor(A / 100 * S**2 / 2158, "units", "Used A as a decimal; the formula takes A in percent."),
        ],
    )


@solver("sag_length")
def sag_length(p):
    g1, g2, S = p["g1"], p["g2"], p["S"]
    A = abs(g2 - g1)
    if g2 <= g1 or A < 2:
        raise Redraw
    p["A"] = A
    L1 = A * S**2 / (400 + 3.5 * S)
    case1 = S < L1
    L = L1 if case1 else 2 * S - (400 + 3.5 * S) / A
    if L <= 0:
        raise Redraw
    steps = [
        Step(f"A = |g₂ − g₁| = |{g2} − ({g1})| = {A}%."),
        Step(
            f"Try S < L: L = AS² / (400 + 3.5S) = {A} × {S}² / {fmt(400 + 3.5 * S, 0)} = {fmt(L1, 0)} ft.",
            wrong=f"Try S < L: L = AS² / 2158 = {fmt(A * S**2 / 2158, 0)} ft.",
            why="2158 is the crest formula; sag curves are governed by headlight sight distance.",
        ),
    ]
    if case1:
        steps.append(Step(f"{S} < {fmt(L1, 0)}, so the assumption holds: L = {fmt(L, 0)} ft."))
    else:
        steps.append(Step(f"{S} > {fmt(L1, 0)}, so use S > L: L = 2S − (400 + 3.5S)/A = {fmt(L, 0)} ft."))
    other = 2 * S - (400 + 3.5 * S) / A if case1 else L1
    return Solution(
        L,
        steps,
        [
            Distractor(other, "method", "Used the formula for the other S-versus-L case without checking."),
            Distractor(A * S**2 / 2158, "method", "Used the crest formula on a sag curve."),
            Distractor(A / 100 * S**2 / (400 + 3.5 * S), "units", "Used A as a decimal; the formula takes A in percent."),
        ],
    )


# --- Sight distance ---------------------------------------------------------


@solver("ssd")
def ssd(p):
    V, G, t = p["V"], p["G"], p.get("t", 2.5)
    a = 11.2
    g = G / 100
    p["G_word"] = "downgrade" if G < 0 else ("upgrade" if G > 0 else "level grade")
    p["G_abs"] = abs(G)
    d_r = MPH_TO_FPS * V * t
    d_b = V**2 / (30 * (a / G_FT + g))
    s = d_r + d_b
    return Solution(
        s,
        [
            Step("SSD = 1.47Vt + V² / (30((a / 32.2) ± G)); G is positive for upgrades, negative for downgrades."),
            Step(f"Reaction distance = 1.47 × {V} × {t} = {fmt(d_r, 1)} ft."),
            Step(
                f"Braking distance = {V}² / (30 × ({fmt(a / G_FT, 3)} + ({fmt(g, 2)}))) = {fmt(d_b, 1)} ft.",
                wrong=f"Braking distance = {V}² / (30 × ({fmt(a / G_FT, 3)} − ({fmt(g, 2)}))) = {fmt(V**2 / (30 * (a / G_FT - g)), 1)} ft.",
                why="On a downgrade the grade term reduces the deceleration, which lengthens the distance; the sign is flipped here.",
            ),
            Step(f"SSD = {fmt(d_r, 1)} + {fmt(d_b, 1)} = {fmt(s, 0)} ft."),
        ],
        [
            Distractor(d_r + V**2 / (30 * (a / G_FT - g)), "setup", "Used the wrong sign for the grade.")
            if G
            else Distractor(d_r + V**2 / (30 * a), "units", "Used a in ft/s² without dividing by 32.2."),
            Distractor(V * t + d_b, "units", "Left out the 1.47 conversion in the reaction distance."),
            Distractor(d_b, "concept", "Gave the braking distance only; SSD includes the reaction distance."),
        ],
    )


# --- Earthwork and pavement -------------------------------------------------


@solver("avg_end_area")
def avg_end_area(p):
    A1, A2, L = p["A1"], p["A2"], p["L"]
    V = L * (A1 + A2) / 2 / 27
    return Solution(
        V,
        [
            Step("Average end area: V = L(A₁ + A₂) / 2, then divide by 27 for cubic yards."),
            Step(f"V = {L} × ({A1} + {A2}) / 2 = {fmt(L * (A1 + A2) / 2, 0)} ft³."),
            Step(
                f"V = {fmt(L * (A1 + A2) / 2, 0)} / 27 = {fmt(V, 0)} yd³.",
                wrong=f"V = {fmt(L * (A1 + A2) / 2, 0)} / 9 = {fmt(L * (A1 + A2) / 2 / 9, 0)} yd³.",
                why="A cubic yard is 27 ft³; 9 is the square-yard factor.",
            ),
        ],
        [
            Distractor(L * (A1 + A2) / 2, "units", "Left the answer in cubic feet."),
            Distractor(L * (A1 + A2) / 27, "arithmetic", "Forgot to average the two areas."),
            Distractor(L * (A1 + A2) / 2 / 9, "units", "Divided by 9 instead of 27."),
        ],
    )


@solver("borrow_volume")
def borrow_volume(p):
    Vf, Vc, s = p["Vf"], p["Vc"], p["s"] / 100
    compacted_from_cut = Vc * (1 - s)
    deficit = Vf - compacted_from_cut
    if deficit <= 500:
        raise Redraw
    B = deficit / (1 - s)
    return Solution(
        B,
        [
            Step(f"Cut placed as fill shrinks: {Vc:,} × (1 − {s:.2f}) = {fmt(compacted_from_cut, 0)} compacted yd³."),
            Step(f"Compacted shortfall = {Vf:,} − {fmt(compacted_from_cut, 0)} = {fmt(deficit, 0)} yd³."),
            Step(
                f"Bank borrow = {fmt(deficit, 0)} / (1 − {s:.2f}) = {fmt(B, 0)} bank yd³.",
                wrong=f"Bank borrow = {fmt(deficit, 0)} × (1 − {s:.2f}) = {fmt(deficit * (1 - s), 0)} bank yd³.",
                why="Borrow shrinks too, so more bank volume is needed than the compacted shortfall.",
            ),
        ],
        [
            Distractor(Vf - Vc, "concept", "Ignored shrinkage."),
            Distractor(deficit, "setup", "Gave the compacted shortfall, not bank volume."),
            Distractor(Vf - Vc * (1 + s), "concept", "Treated shrinkage as swell."),
        ],
    )


@solver("structural_number")
def structural_number(p):
    a1, D1, a2, D2, m2, a3, D3, m3 = (p[k] for k in ("a1", "D1", "a2", "D2", "m2", "a3", "D3", "m3"))
    SN = a1 * D1 + a2 * D2 * m2 + a3 * D3 * m3
    return Solution(
        SN,
        [
            Step("SN = a₁D₁ + a₂D₂m₂ + a₃D₃m₃, thicknesses in inches."),
            Step(f"Surface: {a1} × {D1} = {fmt(a1 * D1, 2)}."),
            Step(
                f"Base: {a2} × {D2} × {m2} = {fmt(a2 * D2 * m2, 2)}.",
                wrong=f"Base: {a2} × {D2} = {fmt(a2 * D2, 2)}.",
                why="The base contribution must include its drainage coefficient m₂.",
            ),
            Step(f"Subbase: {a3} × {D3} × {m3} = {fmt(a3 * D3 * m3, 2)}."),
            Step(f"SN = {fmt(SN, 2)}."),
        ],
        [
            Distractor(a1 * D1 + a2 * D2 + a3 * D3, "setup", "Left out the drainage coefficients."),
            Distractor(SN / 12, "units", "Used thicknesses in feet."),
            Distractor(a1 * D1 * m2 + a2 * D2 * m2 + a3 * D3 * m3, "concept", "Applied a drainage coefficient to the asphalt surface."),
        ],
    )


@solver("base_thickness")
def base_thickness(p):
    SNr, a1, D1, a2, m2, a3, D3, m3 = (p[k] for k in ("SN", "a1", "D1", "a2", "m2", "a3", "D3", "m3"))
    D2 = (SNr - a1 * D1 - a3 * D3 * m3) / (a2 * m2)
    if not 4 <= D2 <= 18:
        raise Redraw
    return Solution(
        D2,
        [
            Step("Solve SN = a₁D₁ + a₂D₂m₂ + a₃D₃m₃ for D₂."),
            Step(f"Surface and subbase supply {fmt(a1 * D1, 2)} + {fmt(a3 * D3 * m3, 2)} = {fmt(a1 * D1 + a3 * D3 * m3, 2)}."),
            Step(
                f"D₂ = ({SNr} − {fmt(a1 * D1 + a3 * D3 * m3, 2)}) / ({a2} × {m2}) = {fmt(D2, 1)} in.",
                wrong=f"D₂ = ({SNr} − {fmt(a1 * D1 + a3 * D3 * m3, 2)}) / {a2} = {fmt((SNr - a1 * D1 - a3 * D3 * m3) / a2, 1)} in.",
                why="Divide by a₂m₂, not a₂ alone.",
            ),
        ],
        [
            Distractor((SNr - a1 * D1 - a3 * D3 * m3) / a2, "setup", "Left out m₂."),
            Distractor((SNr - a1 * D1) / (a2 * m2), "concept", "Forgot the subbase contribution."),
            Distractor(SNr / (a2 * m2), "concept", "Assigned the whole SN to the base."),
        ],
    )


# --- Temporary traffic control ----------------------------------------------


@solver("ttc_taper")
def ttc_taper(p):
    W, S, kind = p["W"], p["S"], p["kind"]
    L = W * S**2 / 60 if S <= 40 else W * S
    factor = {"merging": 1, "shifting": 0.5, "shoulder": 1 / 3}[kind]
    ans = L * factor
    other = W * S if S <= 40 else W * S**2 / 60
    rule = "L = WS²/60 for S ≤ 40 mi/h" if S <= 40 else "L = WS for S ≥ 45 mi/h"
    share = {"merging": "the full L", "shifting": "at least L/2", "shoulder": "at least L/3"}[kind]
    return Solution(
        ans,
        [
            Step(f"Base taper length: {rule}."),
            Step(
                f"L = {fmt(L, 0)} ft for W = {W} ft and S = {S} mi/h.",
                wrong=f"L = {fmt(other, 0)} ft (other speed formula).",
                why="The formula depends on the posted speed: WS²/60 up to 40 mi/h, WS at 45 mi/h and above.",
            ),
            Step(f"A {kind} taper uses {share}: {fmt(ans, 0)} ft."),
        ],
        [
            Distractor(other * factor, "method", "Used the formula for the other speed range."),
            Distractor(L if factor != 1 else L / 2, "lookup", "Used the wrong taper type's share of L."),
            Distractor(S**2 / 60 * factor if S <= 40 else S * factor, "setup", "Left out the offset width W."),
        ],
    )
