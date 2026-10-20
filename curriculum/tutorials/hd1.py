"""HD1 Horizontal curve geometry.

Every number below was worked by hand and checked in Python. Angles are in
degrees; the arc definition of degree of curve is used throughout.
"""

CURVE = "circular-curve"
DEGREE = "degree-of-curve"

TUTORIAL = {
    "minutes": 30,
    "blocks": [
        {
            "kind": "text",
            "title": "Two straight roads and the arc between them",
            "body": """
A highway alignment is a chain of straight **tangents** joined by circular arcs. Where two tangents would meet is the **PI** (point of intersection). The angle the direction of travel turns through there is the **intersection angle Δ**.

The circular curve starts at the **PC** (point of curvature) on the back tangent and ends at the **PT** (point of tangency) on the forward tangent. The curve is tangent to both lines, so a driver feels a smooth change from straight to turning.

Like the PVI of a vertical curve, the PI is **not on the road** once the curve is built. It is a construction point.
""",
        },
        {
            "kind": "text",
            "title": "The five elements",
            "body": """
Everything follows from the radius R and the angle Δ:

::

    T  = R · tan(Δ/2)            tangent length, PC to PI (and PI to PT)
    L  = R · Δ · π / 180         curve length along the arc (Δ in degrees)
    E  = R · (1/cos(Δ/2) − 1)    external distance, PI to the middle of the curve
    M  = R · (1 − cos(Δ/2))      middle ordinate, middle of the curve to the chord
    LC = 2R · sin(Δ/2)           long chord, PC to PT in a straight line

The geometry gives a built-in order you can sanity-check: **LC < L < 2T**, and **E > M**.
""",
        },
        {
            "kind": "explorer",
            "title": "Draw a circular curve",
            "widget": CURVE,
            "body": """
Change the radius and the intersection angle. The green arc is the road. The dashed lines are the tangents it replaces and the long chord. The amber segment is **E** and the red one is **M**. The strip at the bottom compares stationing along the tangents with stationing along the curve.
""",
        },
        {
            "kind": "check",
            "title": "Predict before you slide",
            "prompt": "Hold R at 1,000 ft and increase Δ from 20° to 60°. Predict what happens to the gap between **PI + T** and the true **PT** on the stationing strip. Then try it in the explorer above.",
            "choices": [
                {"label": "The gap grows quickly as Δ grows", "correct": True, "why": "The gap is 2T − L. At Δ = 20° it is about 3.6 ft; at 60° it is about 107.5 ft. The sharper the turn, the more distance the curve cuts off."},
                {"label": "The gap stays the same, because R doesn't change", "correct": False, "why": "The gap depends on Δ as well as R: 2T − L = R(2 tan(Δ/2) − Δπ/180)."},
                {"label": "The gap shrinks, because T and L both grow", "correct": False, "why": "Both grow, but T grows faster than L, since tan(Δ/2) rises faster than the angle itself."},
                {"label": "There is no gap: PT = PI + T", "correct": False, "why": "That would mean the road follows the tangents. The curve is a shortcut inside them, so the PT station is always less than PI + T."},
            ],
            "explanation": """
With R = 1,000 ft:

::

    Δ = 20°:  2T = 352.65 ft,   L = 349.07 ft,   gap = 3.59 ft
    Δ = 60°:  2T = 1,154.70 ft, L = 1,047.20 ft, gap = 107.50 ft

The gap grows roughly with Δ³, so it is small for gentle curves and large for sharp ones. Either way, **PT = PC + L**, never PI + T.
""",
            "widget": CURVE,
            "config": {"values": {"R": 1000, "delta": 60, "pi": 10000}},
        },
        {
            "kind": "check",
            "title": "Tangent length",
            "prompt": "A simple curve has R = 1,000 ft and Δ = 40°. What is the tangent length T, in feet?",
            "answer": 363.97,
            "tolerance": 0.05,
            "unit": "ft",
            "hint": "T = R tan(Δ/2). Put your calculator in degree mode.",
            "explanation": """
::

    T = 1,000 × tan(20°) = 1,000 × 0.36397 = 363.97 ft

If you got 2,237 ft, your calculator was in radian mode: tan(20 rad) = 2.237. If you got 839.10 ft, you used tan(Δ) instead of tan(Δ/2).
""",
            "widget": CURVE,
            "config": {"values": {"R": 1000, "delta": 40, "pi": 10000}},
        },
        {
            "kind": "check",
            "title": "Curve length",
            "prompt": "Same curve: R = 1,000 ft, Δ = 40°. What is the curve length L, in feet?",
            "answer": 698.13,
            "tolerance": 0.05,
            "unit": "ft",
            "hint": "L = R Δ π / 180, with Δ in degrees.",
            "explanation": """
::

    L = 1,000 × 40 × π / 180 = 698.13 ft

Check the order: LC = 2 × 1,000 × sin 20° = 684.04 ft, and 2T = 727.94 ft, so **684.04 < 698.13 < 727.94**. If your L had come out bigger than 2T, something was wrong.
""",
            "widget": CURVE,
            "config": {"values": {"R": 1000, "delta": 40, "pi": 10000}},
        },
        {
            "kind": "example",
            "title": "All the elements (core)",
            "prompt": "A curve has R = 1,200 ft and Δ = 36°. Find T, L, E, M and the long chord.",
            "steps": [
                {"think": "Which angle goes into the trig functions?", "text": "Every element except L uses the half-angle: Δ/2 = **18°**."},
                {"text": "T = 1,200 × tan 18° = 1,200 × 0.32492 = **389.90 ft**."},
                {"text": "L = 1,200 × 36 × π / 180 = **753.98 ft**."},
                {"think": "E and M lie on the same line, the bisector of Δ. Which is longer?", "text": "E = 1,200 × (1/cos 18° − 1) = 1,200 × 0.05146 = **61.75 ft**. M = 1,200 × (1 − cos 18°) = 1,200 × 0.04894 = **58.73 ft**. E is longer, as it must be."},
                {"text": "LC = 2 × 1,200 × sin 18° = **741.64 ft**. Check: 741.64 < 753.98 < 779.81 (= 2T)."},
            ],
            "explanation": "One identity links two of these and makes a quick check: E = M / cos(Δ/2), and 58.73 / cos 18° = 61.75 ft.",
            "widget": CURVE,
            "config": {"values": {"R": 1200, "delta": 36, "pi": 10000}},
        },
        {
            "kind": "text",
            "title": "Stationing follows the road",
            "body": """
Stations measure distance **along the alignment as built**. Before the curve, the alignment is the back tangent; after the PC it is the arc. So:

::

    PC station = PI station − T
    PT station = PC station + L

The tangent from the PI to the PT is not part of the road, so it adds nothing to the stationing. That's why **PT ≠ PI + T**. This is the most common stationing error, and the exam's wrong answers are built around it.
""",
        },
        {
            "kind": "check",
            "title": "Spot the slip",
            "prompt": "The PI is at 45+20.00, R = 900 ft and Δ = 48°, so T = 400.71 ft and L = 753.98 ft. A student reports the PT at **49+20.71**. What went wrong?",
            "choices": [
                {"label": "They added T to the PI instead of L to the PC", "correct": True, "why": "45+20.00 + 400.71 = 49+20.71. The road never runs along the forward tangent from the PI, so this station is wrong by 2T − L = 47.43 ft."},
                {"label": "They used tan(Δ) instead of tan(Δ/2)", "correct": False, "why": "That would make T = 900 × tan 48° = 999.56 ft and the PT far beyond 49+20.71."},
                {"label": "They forgot to subtract T for the PC", "correct": False, "why": "Then PT = 45+20.00 + 753.98 = 52+73.98, not 49+20.71."},
                {"label": "Nothing: that is the PT", "correct": False, "why": "The correct PT is 41+19.29 + 753.98 = 48+73.28."},
            ],
            "explanation": """
::

    PC = 45+20.00 − 400.71 = 41+19.29
    PT = 41+19.29 + 753.98 = 48+73.28
    PI + T = 49+20.71   ← 47.43 ft too far

Look at the stationing strip in the figure: the red end of the tangent row is where the slip lands; the green curve row ends at the true PT.
""",
            "widget": CURVE,
            "config": {"values": {"R": 900, "delta": 48, "pi": 4520}},
        },
        {
            "kind": "example",
            "title": "PC and PT stations (standard)",
            "prompt": "The PI of a curve is at station **45+20.00**. The radius is 900 ft and Δ = 48°. Find the stations of the PC and PT.",
            "steps": [
                {"think": "Which element gets you from the PI to the PC?", "text": "T = 900 × tan 24° = 900 × 0.44523 = **400.71 ft**."},
                {"text": "PC = 45+20.00 − 4+00.71 = **41+19.29**."},
                {"think": "Now, from the PC, what distance takes you to the PT along the road?", "text": "L = 900 × 48 × π / 180 = **753.98 ft**."},
                {"text": "PT = 41+19.29 + 7+53.98 = **48+73.28**."},
            ],
            "explanation": "The PT is 47.43 ft before PI + T (49+20.71). A quick check: the PT must be ahead of the PI, and less than T ahead of it. 48+73.28 is 353.28 ft past the PI, less than T = 400.71 ft.",
            "widget": CURVE,
            "config": {"values": {"R": 900, "delta": 48, "pi": 4520}},
        },
        {
            "kind": "text",
            "title": "Degree of curve",
            "body": """
Some problems give the curve's sharpness as a **degree of curve D** instead of a radius. Under the **arc definition**, used for highways, D is the central angle that 100 ft of arc subtends:

::

    D = 5729.58 / R        (R in feet, D in degrees)
    L = 100 · Δ / D        (the same L as RΔπ/180)

5729.58 is 100 × 180/π. A larger D is a sharper curve.
""",
        },
        {
            "kind": "explorer",
            "title": "What 100 ft of arc means",
            "widget": DEGREE,
            "body": "Shrink the radius and watch the angle that 100 ft of arc subtends grow. The two curve-length formulas always agree.",
        },
        {
            "kind": "check",
            "title": "Radius from degree of curve",
            "prompt": "A curve is specified as a **5° curve** (arc definition). What is its radius, in feet?",
            "answer": 1145.92,
            "tolerance": 0.05,
            "unit": "ft",
            "hint": "Rearrange D = 5729.58 / R.",
            "explanation": """
::

    R = 5729.58 / 5 = 1,145.92 ft

So a 5° curve turns 5° for every 100 ft of arc. Doubling D to 10° halves the radius.
""",
            "widget": DEGREE,
            "config": {"values": {"R": 1146, "delta": 30}},
        },
        {
            "kind": "example",
            "title": "From degree of curve to stations (stretch)",
            "prompt": "A **4° curve** (arc definition) has Δ = 30°20′. The PI is at station **120+00.00**. Find R, T, L and the stations of the PC and PT.",
            "steps": [
                {"think": "Δ is in degrees and minutes. Convert it first.", "text": "Δ = 30 + 20/60 = **30.3333°**, and Δ/2 = 15.1667°."},
                {"text": "R = 5729.58 / 4 = **1,432.40 ft**."},
                {"text": "T = 1,432.40 × tan 15.1667° = **388.28 ft**."},
                {"think": "Which curve-length formula is fastest here?", "text": "L = 100 × 30.3333 / 4 = **758.33 ft**. (RΔπ/180 gives the same.)"},
                {"text": "PC = 120+00.00 − 3+88.28 = **116+11.72**. PT = 116+11.72 + 7+58.33 = **123+70.05**."},
            ],
            "explanation": "Minutes are the classic trap: 30°20′ is 30.333°, not 30.20°. Using 30.20° would make L = 755.00 ft, 3.33 ft short.",
            "widget": CURVE,
            "config": {"values": {"R": 1432.4, "delta": 30.3333, "pi": 12000}},
        },
        {
            "kind": "check",
            "title": "E or M?",
            "prompt": "A question asks how far the **middle of the curve** is from the **PI**. Which element is that?",
            "choices": [
                {"label": "E, the external distance", "correct": True, "why": "E runs from the PI to the curve's midpoint along the bisector of Δ."},
                {"label": "M, the middle ordinate", "correct": False, "why": "M runs from the curve's midpoint to the middle of the long chord, on the inside of the curve."},
                {"label": "T, the tangent length", "correct": False, "why": "T runs along a tangent, from the PI to the PC or PT."},
                {"label": "LC / 2, half the long chord", "correct": False, "why": "That runs along the chord from the PC to its midpoint."},
            ],
            "explanation": """
E and M both lie on the bisector of Δ. Picture walking from the PI toward the center of the circle: you cross the curve after E, then the chord after a further M.

* **E** (PI to curve) matters for clearance at the corner, for example from a building near the PI.
* **M** (curve to chord) matters for sight across the inside of the curve. That is the next topic, HD3.
""",
            "widget": CURVE,
            "config": {"values": {"R": 1200, "delta": 36, "pi": 10000}},
        },
        {
            "kind": "text",
            "title": "Common mistakes, and exam day",
            "body": """
* **PT = PI + T.** It is PC + L.
* **tan(Δ) instead of tan(Δ/2)** in T, E or M.
* **Degree mode.** Every trig function here takes degrees.
* **Degrees and minutes.** Convert 30°20′ to 30.333° before calculating.
* **E and M swapped.** E is outside the curve (toward the PI), M is inside (toward the chord).

The circular curve formulas and diagram are in the NCEES Handbook's transportation chapter; search **circular curve** or **tangent length**. Before calculating, check the order LC < L < 2T on your answers. It catches most slips in seconds.
""",
        },
    ],
}
