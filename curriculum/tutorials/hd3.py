"""HD3 Horizontal sight distance.

Every number below was worked by hand and checked in Python. The angle
28.65 S / R is in degrees. Stopping sight distances in the stretch example
use the course's SSD formula (t = 2.5 s, a = 11.2 ft/s², level grade).
"""

SIGHT = "sightline"

TUTORIAL = {
    "minutes": 25,
    "blocks": [
        {
            "kind": "text",
            "title": "Seeing around a curve",
            "body": """
On a straight road, sight distance is limited only by the vertical profile. On a horizontal curve, anything on the **inside** of the curve (a wall, a cut slope, a building, trees) can block the driver's line of sight to an object in the lane ahead.

The driver's sightline is a straight **chord** between their eye and the object, cutting across the inside of the curve. To keep stopping sight distance, the area between that chord and the lane must be clear. The depth of that area at the middle of the curve is the **horizontal sightline offset M**.
""",
        },
        {
            "kind": "text",
            "title": "The offset formula",
            "body": """
For a sight distance S measured **along the lane** (S shorter than the curve):

::

    M = R · (1 − cos(28.65 · S / R))      angle in degrees
    R = radius to the centerline of the INSIDE lane (ft)
    M = offset from that centerline to the obstruction (ft)

Where 28.65 comes from: the sightline subtends a central angle of S/R radians, and half of it is S/(2R) radians = 28.65·S/R degrees (since 180/(2π) = 28.65).

For small angles, a handy check is M ≈ S² / (8R).
""",
        },
        {
            "kind": "explorer",
            "title": "Clear the sightline",
            "widget": SIGHT,
            "body": "Move the radius, the required sight distance and how far the obstruction sits from the inside lane's centerline. The sightline turns red when the obstruction cuts across it. Offsets are drawn exaggerated so you can see them.",
        },
        {
            "kind": "check",
            "title": "Predict first",
            "prompt": "Keep S = 400 ft and **double the radius** from 1,000 ft to 2,000 ft. Predict what happens to M, then check in the explorer.",
            "choices": [
                {"label": "M roughly halves, from about 20 ft to about 10 ft", "correct": True, "why": "M ≈ S²/(8R): with S fixed, M is inversely proportional to R. The exact values are 19.94 ft and 9.99 ft."},
                {"label": "M doubles", "correct": False, "why": "A flatter curve bends the lane away from the sightline less, so less clearance is needed, not more."},
                {"label": "M stays the same, because S is the same", "correct": False, "why": "The same S on a gentler curve cuts a shallower chord."},
                {"label": "M drops to a quarter", "correct": False, "why": "That would be true if M depended on 1/R². It depends on S²/R, so doubling R halves M."},
            ],
            "explanation": """
::

    R = 1,000 ft:  M = 1,000 × (1 − cos 11.46°)  = 19.94 ft
    R = 2,000 ft:  M = 2,000 × (1 − cos 5.73°)   = 9.99 ft

And S²/(8R) gives 20.00 ft and 10.00 ft: close, because the angles are small.
""",
            "widget": SIGHT,
            "config": {"values": {"R": 2000, "S": 400, "C": 25}},
        },
        {
            "kind": "example",
            "title": "Offset for stopping sight distance (core)",
            "prompt": "A curve has a radius of **1,000 ft** to the centerline of the inside lane. The required stopping sight distance is **400 ft**. How far from the inside lane centerline must obstructions be kept?",
            "steps": [
                {"think": "What is the half-angle, and which units is it in?", "text": "28.65 × 400 / 1,000 = **11.46°** (degrees)."},
                {"text": "cos 11.46° = 0.98006."},
                {"text": "M = 1,000 × (1 − 0.98006) = **19.94 ft**."},
                {"think": "Is there a quick way to check that?", "text": "S²/(8R) = 160,000 / 8,000 = 20.0 ft. Close to 19.94 ft, so the answer is reasonable."},
            ],
            "explanation": "Obstructions must be at least 19.94 ft from the inside lane's centerline, roughly 14 ft beyond its edge for a 12-ft lane.",
            "widget": SIGHT,
            "config": {"values": {"R": 1000, "S": 400, "C": 20}},
        },
        {
            "kind": "check",
            "title": "Compute M",
            "prompt": "R = 800 ft to the inside lane centerline, S = 425 ft. What offset M is needed, in feet?",
            "answer": 28.06,
            "tolerance": 0.05,
            "unit": "ft",
            "hint": "Half-angle = 28.65 × 425 / 800, in degrees. Then M = R(1 − cos).",
            "explanation": """
::

    half-angle = 28.65 × 425 / 800 = 15.22°
    M = 800 × (1 − cos 15.22°) = 800 × 0.03508 = 28.06 ft

The S²/(8R) check gives 28.22 ft, a little high because the angle is larger here.
""",
            "widget": SIGHT,
            "config": {"values": {"R": 800, "S": 425, "C": 29}},
        },
        {
            "kind": "check",
            "title": "Spot the slip",
            "prompt": "For R = 1,000 ft and S = 400 ft, a student gets **M = 552 ft**. What happened?",
            "choices": [
                {"label": "Their calculator was in radian mode", "correct": True, "why": "cos(11.46 rad) = 0.448, so M = 1,000 × 0.552 = 552 ft. The 28.65 factor produces degrees."},
                {"label": "They used S/R instead of the half-angle", "correct": False, "why": "R(1 − cos(S/R rad)) = 1,000 × (1 − cos 0.4) = 78.9 ft."},
                {"label": "They used the radius to the road centerline", "correct": False, "why": "A few feet of difference in R changes M only slightly, nowhere near 552 ft."},
                {"label": "They used S²/(8R)", "correct": False, "why": "That gives 20 ft, close to the right answer."},
            ],
            "explanation": """
A 552-ft offset on a 1,000-ft curve is absurd: it is over half the radius. That is a signal to check calculator mode.

Two equivalent ways to avoid the trap:

* Degree mode: M = R(1 − cos(28.65 S/R)).
* Radian mode: M = R(1 − cos(S / 2R)), since S/(2R) = 0.2 rad gives the same 19.94 ft.
""",
        },
        {
            "kind": "text",
            "title": "Which radius, and which distance?",
            "body": """
Two details decide whether an answer is right:

* **R is to the centerline of the inside lane**, where the driver's eye and the object are assumed to be. The road's centerline radius is larger by half a lane or more.
* **M is measured from that lane centerline** to the obstruction, not from the edge of pavement. To find the clearance beyond the lane edge, subtract half the lane width.

The formula assumes the sight distance lies within the curve (S ≤ L). When the sightline extends onto a tangent, the geometry changes and charts or graphical methods are used.
""",
        },
        {
            "kind": "check",
            "title": "Lane edge or lane centerline?",
            "prompt": "M comes out as 19.94 ft for a 12-ft inside lane. How far beyond the **edge** of that lane must the area be clear?",
            "answer": 13.94,
            "tolerance": 0.02,
            "unit": "ft",
            "hint": "M is measured from the lane's centerline. The edge is half a lane closer.",
            "explanation": """
::

    clearance beyond lane edge = M − lane width / 2 = 19.94 − 6.00 = 13.94 ft

Questions often give a wall's distance from the edge of pavement. Convert to the lane centerline (add half the lane width) before comparing with M.
""",
            "widget": SIGHT,
            "config": {"values": {"R": 1000, "S": 400, "C": 20}},
        },
        {
            "kind": "example",
            "title": "Is an existing wall too close? (standard)",
            "prompt": "A building sits **22 ft** from the centerline of the inside lane of a curve with R = **800 ft**. The required stopping sight distance is **425 ft**. Is the sight distance adequate? If not, how much sight distance does the building allow?",
            "steps": [
                {"think": "What offset does 425 ft of sight distance need?", "text": "From the last check, M = **28.06 ft**. The building is at 22 ft, so it **blocks** the sightline."},
                {"think": "Now reverse the formula: given M = 22 ft, solve for S.", "text": "cos(28.65 S / R) = (R − M) / R = 778 / 800 = 0.9725, so the half-angle = 13.47°."},
                {"text": "S = 13.47 × 800 / 28.65 = **376 ft**."},
            ],
            "explanation": "The building allows only about 376 ft of sight distance, 49 ft short. Options include removing or relocating the obstruction, flattening the curve, or a lower design speed with warning signs.",
            "widget": SIGHT,
            "config": {"values": {"R": 800, "S": 425, "C": 22}},
        },
        {
            "kind": "check",
            "title": "Clear or blocked?",
            "prompt": "Use the explorer: R = 1,500 ft, S = 500 ft, and a retaining wall 18 ft from the inside lane centerline. Is the sightline clear?",
            "choices": [
                {"label": "Blocked: the sightline needs about 20.8 ft", "correct": True, "why": "M = 1,500 × (1 − cos 9.55°) = 20.79 ft, more than the 18 ft available."},
                {"label": "Clear: 18 ft is plenty on a 1,500-ft curve", "correct": False, "why": "500 ft is a long sightline; even on a gentle curve it needs about 20.8 ft."},
                {"label": "Clear, because S is less than R", "correct": False, "why": "S < R doesn't tell you anything about the offset needed."},
                {"label": "It can't be decided without the design speed", "correct": False, "why": "The required S is given, and that is all the offset depends on."},
            ],
            "explanation": """
::

    half-angle = 28.65 × 500 / 1,500 = 9.55°
    M = 1,500 × (1 − cos 9.55°) = 20.79 ft  >  18 ft  → blocked

The wall would need to move back about 2.8 ft.
""",
            "widget": SIGHT,
            "config": {"values": {"R": 1500, "S": 500, "C": 18}},
        },
        {
            "kind": "example",
            "title": "What speed does the curve support? (stretch)",
            "prompt": "A curve has R = **1,200 ft** to the inside lane centerline, and a cut slope **30 ft** from that centerline. Using level-road stopping sight distances (t = 2.5 s, a = 11.2 ft/s²): 50 mi/h needs 423 ft, 55 mi/h needs 492 ft, 60 mi/h needs 566 ft. What is the highest of these speeds the curve supports?",
            "steps": [
                {"think": "Which unknown do you solve for: M or S?", "text": "The offset is fixed at 30 ft, so solve for the sight distance it allows."},
                {"text": "cos(half-angle) = (1,200 − 30) / 1,200 = 0.975, so the half-angle = **12.84°**."},
                {"text": "S = 12.84 × 1,200 / 28.65 = **538 ft**."},
                {"text": "538 ft ≥ 492 ft (55 mi/h) but < 566 ft (60 mi/h). The curve supports **55 mi/h**."},
            ],
            "explanation": "Working the other way confirms it: 55 mi/h needs M = 25.13 ft (under 30, clear), while 60 mi/h needs M = 33.16 ft (over 30, blocked).",
            "widget": SIGHT,
            "config": {"values": {"R": 1200, "S": 492, "C": 30}},
        },
        {
            "kind": "check",
            "title": "Reverse the formula",
            "prompt": "An obstruction is 30 ft from the inside lane centerline on a 1,200-ft curve. What sight distance does it allow, in feet (to the nearest foot)?",
            "answer": 538,
            "tolerance": 1,
            "unit": "ft",
            "hint": "S = (R / 28.65) × arccos((R − M) / R), with arccos in degrees.",
            "explanation": """
::

    S = (1,200 / 28.65) × arccos(1,170 / 1,200)
      = 41.88 × 12.84°
      = 538 ft

This reversed form is the one to use for existing obstructions: it turns an offset into an available sight distance you can compare with what a design speed needs.
""",
            "widget": SIGHT,
            "config": {"values": {"R": 1200, "S": 525, "C": 30}},
        },
        {
            "kind": "text",
            "title": "Common mistakes, and exam day",
            "body": """
* **Radian mode** with the 28.65 form. Use degrees, or use S/(2R) in radians.
* **The wrong radius.** Use the inside lane's centerline, not the road's centerline.
* **Measuring from the pavement edge** instead of the lane centerline.
* **Forgetting to reverse the formula** for an existing obstruction: solve for S, then compare with the required SSD.

The sightline offset equation and design charts are in the Green Book, Chapter 3, with sight distance on horizontal curves; search **horizontal sightline offset**. Check every answer with S²/(8R).
""",
        },
    ],
}
