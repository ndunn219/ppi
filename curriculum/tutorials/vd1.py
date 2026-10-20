"""VD1 Vertical curve elevations: the reference tutorial.

Every number below was worked by hand and checked in Python. Grades are in
percent in the widget and in prose, and decimals inside the equations.
"""

CURVE = "vertical-curve"

TUTORIAL = {
    "minutes": 30,
    "blocks": [
        {
            "kind": "text",
            "title": "Why a vertical curve is a parabola",
            "body": """
A highway can't change grade abruptly: drivers would feel a jolt and lose sight distance over a crest. So the profile changes grade **gradually**, at a constant rate, over a length L. A grade that changes at a constant rate traces a parabola.

Three points define the curve:

* **PVC** (point of vertical curvature), where the curve begins.
* **PVI** (point of vertical intersection), where the two grade lines would meet. It is *not* on the curve.
* **PVT** (point of vertical tangency), where the curve ends.

On an *equal-tangent* curve, the PVI sits halfway along, L/2 from each end. That is the usual exam case.
""",
        },
        {
            "kind": "explorer",
            "title": "Shape a vertical curve",
            "widget": CURVE,
            "config": {"params": ["g1", "g2", "L", "xq"]},
            "body": """
Move the grades and the length. Watch three things: whether the curve is a **crest** (grade decreasing) or a **sag** (grade increasing); whether a **high or low point** appears inside the curve; and how the gap *e* between the PVI and the curve grows with L.
""",
        },
        {
            "kind": "check",
            "title": "Crest or sag?",
            "prompt": "A curve joins an entering grade of **+3%** to an exiting grade of **−2%**. What kind of curve is it, and does it have a high or low point between the PVC and PVT?",
            "choices": [
                {"label": "Crest, with a high point inside the curve", "correct": True, "why": "The grade falls from +3% to −2%, so the road climbs, levels off and descends: a crest. Because the grade passes through zero, the top lies inside the curve."},
                {"label": "Sag, with a low point inside the curve", "correct": False, "why": "A sag needs the grade to increase. Here it goes from +3% down to −2%."},
                {"label": "Crest, with its high point at the PVI", "correct": False, "why": "The PVI is where the tangents meet. It isn't on the curve, and the top only falls exactly below it when the two grades are equal and opposite."},
                {"label": "Crest, with no high point inside the curve", "correct": False, "why": "That happens only when both grades have the same sign. Here they change sign, so the grade passes through zero inside the curve."},
            ],
            "explanation": """
The rule of thumb:

* **g₂ < g₁** → crest. **g₂ > g₁** → sag.
* A high or low point lies inside the curve **only if g₁ and g₂ have opposite signs**, because only then does the grade pass through zero.

In the figure the amber dot is the high point. It sits right of the PVI, toward the flatter grade (−2%), not under the PVI.
""",
            "widget": CURVE,
            "config": {"values": {"g1": 3, "g2": -2, "L": 800, "xq": 0.6}},
        },
        {
            "kind": "text",
            "title": "The equation, starting from the PVC",
            "body": """
Every elevation problem starts the same way: **find the PVC**. The equation measures distance from there.

::

    PVC station   = PVI station − L/2
    PVC elevation = PVI elevation − g₁ × (L/2)

Then, with x in feet from the PVC and grades as **decimals**:

::

    y(x) = E_PVC + g₁·x + (g₂ − g₁)·x² / (2L)

The first two terms follow the entering tangent. The last term is the curve "peeling away" from that tangent. It grows with x², so it is small near the PVC and largest at the PVT.
""",
        },
        {
            "kind": "check",
            "title": "Find the PVC elevation",
            "prompt": "A curve is 800 ft long. The PVI is at station 50+00, elevation 500.00 ft. The entering grade is +3%. What is the elevation of the PVC, in feet?",
            "answer": 488.0,
            "tolerance": 0.01,
            "unit": "ft",
            "hint": "The PVC is L/2 = 400 ft back along the entering grade. Going back up a +3% grade means going down in elevation.",
            "explanation": """
The PVC is L/2 = 400 ft before the PVI, along the entering tangent:

::

    E_PVC = 500.00 − 0.03 × 400 = 500.00 − 12.00 = 488.00 ft

A common slip is adding instead of subtracting. Walking backward from the PVI on a rising grade means going *down*.
""",
            "widget": CURVE,
            "config": {"values": {"g1": 3, "g2": -2, "L": 800, "xq": 0}},
        },
        {
            "kind": "example",
            "title": "Elevation at a station (core)",
            "prompt": "Same curve: L = 800 ft, PVI at 50+00 and elevation 500.00 ft, g₁ = +3%, g₂ = −2%. Find the elevation at station **48+00**.",
            "steps": [
                {"think": "Where does the equation start measuring from?", "text": "Find the PVC: 50+00 − 400 = **46+00**, at elevation **488.00 ft** (from the last question)."},
                {"think": "How far is 48+00 from the PVC?", "text": "x = 48+00 − 46+00 = **200 ft**."},
                {"text": "The tangent part: 488.00 + 0.03 × 200 = 488.00 + 6.00 = **494.00 ft**. This is where the road would be if it stayed on the entering grade."},
                {"think": "What is (g₂ − g₁) as a decimal, and what is 2L?", "text": "The curve term: (−0.02 − 0.03) × 200² / (2 × 800) = −0.05 × 40,000 / 1,600 = **−1.25 ft**."},
                {"text": "y = 494.00 − 1.25 = **492.75 ft**."},
            ],
            "explanation": "The curve is 1.25 ft below the entering tangent at this point. On a crest the curve always sits below the tangents; on a sag, above them.",
            "widget": CURVE,
            "config": {"values": {"g1": 3, "g2": -2, "L": 800, "xq": 0.25}},
        },
        {
            "kind": "text",
            "title": "Finding the high or low point",
            "body": """
The grade at any point is the slope of y(x):

::

    grade(x) = g₁ + (g₂ − g₁)·x / L

The high or low point is where the grade is **zero**:

::

    x = −g₁·L / (g₂ − g₁)

You can use grades in percent or decimals here, because the units cancel. But use the same for both. Then plug x back into y(x) for the elevation.

If x comes out negative or greater than L, the grades have the same sign and the extreme point is at the PVC or PVT instead.
""",
        },
        {
            "kind": "check",
            "title": "Where is the top?",
            "prompt": "For the same curve (L = 800 ft, g₁ = +3%, g₂ = −2%), how far past the PVC is the high point, in feet?",
            "answer": 480.0,
            "tolerance": 0.5,
            "unit": "ft",
            "hint": "x = −g₁·L / (g₂ − g₁). Watch the signs: g₂ − g₁ is negative here.",
            "explanation": """
::

    x = −(3)(800) / (−2 − 3) = −2,400 / −5 = 480 ft

So the high point is at 46+00 + 480 = **50+80**, 80 ft past the PVI, on the side of the flatter grade. Its elevation is y(480) = 488.00 + 14.40 − 7.20 = **495.20 ft**.

Use the explorer above to check: set g₁ = 3, g₂ = −2 and L = 800.
""",
            "widget": CURVE,
            "config": {"values": {"g1": 3, "g2": -2, "L": 800, "xq": 0.6}},
        },
        {
            "kind": "check",
            "title": "Same-sign grades",
            "prompt": "A crest curve joins **+4%** to **+1%**. Where is the highest point of the curve?",
            "choices": [
                {"label": "At the PVT", "correct": True, "why": "The grade never reaches zero: it falls from +4% to +1% but stays positive, so the road climbs the whole way and is highest at the end."},
                {"label": "At the PVC", "correct": False, "why": "The road keeps climbing past the PVC, since the grade is still positive throughout."},
                {"label": "At x = −g₁L/(g₂ − g₁) from the PVC", "correct": False, "why": "That formula gives x = −4L/(−3) = 1.33L, beyond the end of the curve. It tells you the grade would only reach zero past the PVT."},
                {"label": "Directly below the PVI", "correct": False, "why": "The PVI isn't on the curve, and nothing special happens below it here."},
            ],
            "explanation": """
When both grades have the same sign, the formula for x puts the turning point **outside** the curve (x < 0 or x > L). The highest or lowest elevation on the curve is then at one of its ends.

Here the road climbs throughout, so the top is the PVT. Always check that 0 ≤ x ≤ L before using the turning point.
""",
            "widget": CURVE,
            "config": {"values": {"g1": 4, "g2": 1, "L": 600, "xq": 1}},
        },
        {
            "kind": "example",
            "title": "High point station and elevation (standard)",
            "prompt": "A 600-ft crest curve has its PVI at station 120+00, elevation 842.30 ft. The grades are **+2.5%** and **−1.5%**. Find the station and elevation of the high point.",
            "steps": [
                {"think": "What comes first, always?", "text": "PVC station = 120+00 − 300 = **117+00**. PVC elevation = 842.30 − 0.025 × 300 = 842.30 − 7.50 = **834.80 ft**."},
                {"think": "Write the zero-grade condition with these numbers.", "text": "x = −(2.5)(600) / (−1.5 − 2.5) = −1,500 / −4 = **375 ft** from the PVC. Check: 0 ≤ 375 ≤ 600, so it is inside the curve."},
                {"text": "Station = 117+00 + 375 = **120+75**."},
                {"think": "Split y(375) into its tangent part and its curve part.", "text": "Tangent part: 834.80 + 0.025 × 375 = 834.80 + 9.375 = 844.175. Curve part: (−0.04) × 375² / 1,200 = −0.04 × 140,625 / 1,200 = −4.6875."},
                {"text": "Elevation = 844.175 − 4.6875 = **839.49 ft**."},
            ],
            "explanation": "A shortcut gives the same elevation: rise above the PVC = g₁²L / (2(g₁ − g₂)) = 0.025² × 600 / (2 × 0.04) = 4.6875 ft, and 834.80 + 4.69 = 839.49 ft. Use it to check your work, not instead of understanding the steps.",
            "widget": CURVE,
            "config": {"values": {"g1": 2.5, "g2": -1.5, "L": 600, "pvi": 12000, "epvi": 842.3, "xq": 0.625}},
        },
        {
            "kind": "text",
            "title": "The offset at the PVI, and the usual mistakes",
            "body": """
At the middle of the curve, the gap between the PVI and the curve is:

::

    e = A·L / 800       (A = |g₂ − g₁| in percent, e in feet)

For +3% to −2% over 800 ft, e = 5 × 800 / 800 = 5.00 ft. That is the PVI at 500.00 ft and the curve at 495.00 ft directly below it. It is a quick sanity check on any answer near the middle of the curve.

Common mistakes:

* **Measuring x from the PVI** instead of the PVC.
* Putting **percent grades** into the x² term. That term needs decimals, or it is off by a factor of 100.
* Using **g₁ − g₂** in the curve term. It is g₂ − g₁, the change from entering to exiting.
* Reporting the **PVI** as the high point.
""",
        },
        {
            "kind": "check",
            "title": "Spot the slip",
            "prompt": "On the 800-ft curve (PVI 50+00 at 500.00 ft, +3% to −2%), a student computes the elevation at 48+00 as **504.75 ft**. Which mistake gives that number?",
            "choices": [
                {"label": "They started from the PVI elevation instead of the PVC", "correct": True, "why": "500.00 + 0.03 × 200 − 1.25 = 504.75 ft. Every term is right except the starting elevation, which must be the PVC's 488.00 ft, so the answer is 12 ft too high."},
                {"label": "They used percent grades in the curve term", "correct": False, "why": "With percent, the curve term becomes −5 × 40,000 / 1,600 = −125 ft, giving about 369 ft."},
                {"label": "They used g₁ − g₂ in the curve term", "correct": False, "why": "That flips the curve term to +1.25 ft, giving 494.00 + 1.25 = 495.25 ft."},
                {"label": "They measured x from the PVI", "correct": False, "why": "48+00 is before the PVI, so x = −200 ft, giving 488.00 − 6.00 − 1.25 = 480.75 ft."},
            ],
            "explanation": """
The correct elevation is 492.75 ft. Each slip leaves its own fingerprint:

* Started at the PVI elevation: **504.75 ft** (12 ft high, the rise from PVC to PVI).
* Used g₁ − g₂ in the curve term: **495.25 ft** (curve term +1.25 instead of −1.25).
* Measured x from the PVI: **480.75 ft**.
* Percent grades in the x² term: about **369 ft**.

When your answer is near one of these, you know which step to recheck.
""",
        },
        {
            "kind": "example",
            "title": "The low point of a sag (stretch)",
            "prompt": "A 500-ft sag curve has its PVI at station 30+00, elevation 410.00 ft, joining **−3%** to **+2%**. A drainage inlet must go at the low point. Find its station and elevation, then the elevation at station 29+00.",
            "steps": [
                {"think": "PVC station and elevation? Careful with the sign of g₁.", "text": "PVC = 30+00 − 250 = **27+50**. Going back up a −3% grade means going *up*: E_PVC = 410.00 − (−0.03)(250) = 410.00 + 7.50 = **417.50 ft**."},
                {"think": "Where is the grade zero?", "text": "x = −(−3)(500) / (2 − (−3)) = 1,500 / 5 = **300 ft**, inside the curve. Station = 27+50 + 300 = **30+50**."},
                {"text": "Low point elevation = 417.50 − 0.03 × 300 + 0.05 × 300² / 1,000 = 417.50 − 9.00 + 4.50 = **413.00 ft**."},
                {"think": "For 29+00, what is x?", "text": "x = 29+00 − 27+50 = 150 ft. y = 417.50 − 0.03 × 150 + 0.05 × 150² / 1,000 = 417.50 − 4.50 + 1.125 = **414.13 ft**."},
            ],
            "explanation": "On a sag the curve sits *above* the tangents, so the curve term is positive. The low point is 50 ft past the PVI, toward the flatter grade (+2%), just as the crest's high point was.",
            "widget": CURVE,
            "config": {"values": {"g1": -3, "g2": 2, "L": 500, "pvi": 3000, "epvi": 410, "xq": 0.6}},
        },
        {
            "kind": "check",
            "title": "Last check: the PVT",
            "prompt": "For that sag curve (PVI 30+00 at 410.00 ft, −3% to +2%, L = 500 ft), what is the elevation of the PVT, in feet?",
            "answer": 415.0,
            "tolerance": 0.01,
            "unit": "ft",
            "hint": "The PVT is L/2 past the PVI along the exiting grade.",
            "explanation": """
From the PVI, go 250 ft along the exiting +2% grade:

::

    E_PVT = 410.00 + 0.02 × 250 = 415.00 ft

Check it with the curve equation from the PVC (x = L = 500):

::

    417.50 − 0.03 × 500 + 0.05 × 500² / 1,000 = 417.50 − 15.00 + 12.50 = 415.00 ft

Both routes agree. Doing the check takes 30 seconds and catches sign slips.
""",
            "widget": CURVE,
            "config": {"values": {"g1": -3, "g2": 2, "L": 500, "pvi": 3000, "epvi": 410, "xq": 1}},
        },
        {
            "kind": "text",
            "title": "On exam day",
            "body": """
The vertical curve equations and diagram are in the NCEES Handbook's transportation chapter. Search **vertical curve** to land on them. Before you calculate, sketch the curve: crest or sag, and which side the turning point falls on. A 10-second sketch catches most sign errors.

Next in the lesson loop: a worked example that fades into problems you solve yourself.
""",
        },
    ],
}
