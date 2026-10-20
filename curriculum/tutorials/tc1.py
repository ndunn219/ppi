"""TC1 Temporary traffic control tapers.

Every number below was checked in Python. Formulas match
curriculum/solvers.py: L = WS²/60 for S ≤ 40 mi/h, L = WS for S ≥ 45 mi/h;
merging taper at least L, shifting at least L/2, shoulder at least L/3.
"""

CLOSURE = "lane-closure"

TUTORIAL = {
    "minutes": 25,
    "blocks": [
        {
            "kind": "text",
            "title": "What a taper does",
            "body": """
When work blocks part of a road, drivers need room to move over smoothly. A **taper** is the line of cones, drums or other channelizing devices that guides traffic out of the closed space. Too short, and drivers swerve or brake hard. Long enough, and they merge at speed without conflict.

The taper length depends on two things:

* **S**, the speed in mi/h: the posted speed, or the 85th-percentile speed.
* **W**, the width of the lateral shift, in feet. This is often one lane width.

The base taper length L comes from one of two formulas, picked by speed:

::

    S ≤ 40 mi/h:   L = W·S² / 60
    S ≥ 45 mi/h:   L = W·S
""",
        },
        {
            "kind": "explorer",
            "title": "Lay out a lane closure",
            "widget": CLOSURE,
            "config": {"values": {"kind": "merging", "S": 55, "W": 12}},
            "body": """
The plan view is drawn to a fixed length scale (the ruler underneath), so you can compare tapers. Slide the speed from 40 to 45 mi/h and watch the formula switch. Then try the three taper types.
""",
        },
        {
            "kind": "check",
            "title": "Predict the jump",
            "prompt": "For a 12-ft lane closure, the merging taper at 40 mi/h is 320 ft. Before you move the slider, predict the taper at **45 mi/h**.",
            "choices": [
                {"label": "540 ft: the formula switches to WS", "correct": True, "why": "At 45 mi/h, L = WS = 12 × 45 = 540 ft. The switch to the linear form brings a big step up from 320 ft."},
                {"label": "405 ft: still WS²/60", "correct": False, "why": "12 × 45² / 60 = 405 ft, but WS²/60 applies only up to 40 mi/h. At 45 mi/h use WS."},
                {"label": "360 ft: one-eighth longer, since 45/40 = 1.125", "correct": False, "why": "Taper length isn't proportional to speed across the switch. The formula itself changes at 45 mi/h."},
                {"label": "320 ft: the same", "correct": False, "why": "Higher speed always needs a longer taper, here 540 ft."},
            ],
            "hint": "Which formula applies at 45 mi/h?",
            "explanation": """
::

    40 mi/h:  L = 12 × 40² / 60 = 320 ft
    45 mi/h:  L = 12 × 45      = 540 ft

The jump is real: crossing into the higher-speed range lengthens the taper by about two-thirds. Always pick the formula by speed **first**. As written here, the two formulas cover 40 mi/h and below and 45 mi/h and above. They don't say what to do for a speed in between, so check the MUTCD if one comes up.
""",
            "widget": CLOSURE,
            "config": {"values": {"kind": "merging", "S": 45, "W": 12}},
        },
        {
            "kind": "example",
            "title": "A low-speed lane closure (core)",
            "prompt": "A utility crew closes one **12-ft** lane on an urban street posted at **35 mi/h**. Find the minimum merging taper length.",
            "steps": [
                {"think": "Which formula, at 35 mi/h?", "text": "35 ≤ 40, so **L = WS² / 60**."},
                {"text": "L = 12 × 35² / 60 = 12 × 1,225 / 60 = **245 ft**."},
                {"text": "A merging taper uses the full L: **245 ft**."},
            ],
            "explanation": "Using WS here would give 420 ft, longer than needed. Not unsafe, but it's the wrong formula, and exam answer choices are built to catch exactly that slip.",
            "widget": CLOSURE,
            "config": {"values": {"kind": "merging", "S": 35, "W": 12}},
        },
        {
            "kind": "check",
            "title": "Your turn: highway speed",
            "prompt": "A freeway work zone closes an **11-ft** lane. The posted speed is **55 mi/h**. What is the minimum merging taper length, in feet?",
            "answer": 605,
            "tolerance": 0.5,
            "unit": "ft",
            "hint": "Above 40 mi/h, so the linear formula.",
            "explanation": """
::

    S = 55 ≥ 45, so L = W·S = 11 × 55 = 605 ft

The common slip is WS²/60 = 11 × 55² / 60 = 555 ft, which is the wrong formula for this speed and too short.
""",
            "widget": CLOSURE,
            "config": {"values": {"kind": "merging", "S": 55, "W": 11}},
        },
        {
            "kind": "text",
            "title": "Merging, shifting and shoulder tapers",
            "body": """
Not every taper asks drivers to do the same thing, so the length needed differs:

* **Merging taper**, at least **L**. A lane ends and its drivers must find a gap and merge into the next lane. That takes the most distance.
* **Shifting taper**, at least **L/2**. Lanes move sideways but every lane keeps flowing, so no one has to merge.
* **Shoulder taper**, at least **L/3**. Only the shoulder is closed, and through traffic barely changes its path. W here is the shoulder width.

Always compute the base L first, using the speed and the W for that taper, and then apply the share.
""",
        },
        {
            "kind": "check",
            "title": "A shifting taper",
            "prompt": "On a **50 mi/h** road, both lanes shift **12 ft** to the right onto a widened shoulder. What is the minimum shifting taper length, in feet?",
            "answer": 300,
            "tolerance": 0.5,
            "unit": "ft",
            "hint": "Base L first (which formula at 50 mi/h?), then the shifting share.",
            "explanation": """
::

    L = W·S = 12 × 50 = 600 ft
    shifting taper ≥ L/2 = 300 ft

A frequent wrong answer is 600 ft, which uses the full L for a taper that only shifts traffic.
""",
            "widget": CLOSURE,
            "config": {"values": {"kind": "shifting", "S": 50, "W": 12}},
        },
        {
            "kind": "check",
            "title": "Which taper type?",
            "prompt": "A crew closes the **right shoulder** of a 60 mi/h highway; the shoulder is 10 ft wide and no travel lane is affected. What is the minimum taper length?",
            "choices": [
                {"label": "200 ft", "correct": True, "why": "L = WS = 10 × 60 = 600 ft, and a shoulder taper needs at least L/3 = 200 ft."},
                {"label": "600 ft", "correct": False, "why": "That is the full L, the merging-taper length. A shoulder closure needs only a third of it."},
                {"label": "300 ft", "correct": False, "why": "That is L/2, the shifting-taper share."},
                {"label": "100 ft", "correct": False, "why": "That would be L/6. No taper type uses that share."},
            ],
            "hint": "Shoulder tapers use a third of L. Find L with W = 10 ft.",
            "explanation": """
::

    S = 60 ≥ 45:   L = 10 × 60 = 600 ft
    shoulder:      L/3 = 200 ft
""",
            "widget": CLOSURE,
            "config": {"values": {"kind": "shoulder", "S": 60, "W": 10}},
        },
        {
            "kind": "example",
            "title": "Choose the formula and the share (standard)",
            "prompt": "A residential street posted at **25 mi/h** closes a **10-ft** lane. Find the merging taper, then the taper if instead the lanes only shifted 10 ft.",
            "steps": [
                {"think": "Which formula at 25 mi/h?", "text": "25 ≤ 40, so L = WS² / 60 = 10 × 25² / 60 = 6,250 / 60 = **104.2 ft**."},
                {"text": "Merging taper: at least L = **104.2 ft** (round up to a practical layout, such as 105 ft)."},
                {"think": "And for a shift?", "text": "Shifting taper: at least L/2 = **52.1 ft** (lay out 53 ft or more)."},
            ],
            "explanation": "At low speeds tapers are short, because S² / 60 shrinks quickly as S drops. At 25 mi/h the merging taper is under half of what the same closure needs at 40 mi/h (267 ft).",
            "widget": CLOSURE,
            "config": {"values": {"kind": "merging", "S": 25, "W": 10}},
        },
        {
            "kind": "check",
            "title": "Spot the slip",
            "prompt": "For a 35 mi/h, 12-ft lane closure (correct merging taper 245 ft), a student writes **420 ft**. What did they do?",
            "choices": [
                {"label": "Used L = WS, the higher-speed formula", "correct": True, "why": "12 × 35 = 420 ft. At 35 mi/h the WS²/60 formula applies."},
                {"label": "Used half of L", "correct": False, "why": "Half of 245 is 122.5 ft."},
                {"label": "Left W out of WS²/60", "correct": False, "why": "35² / 60 = 20.4 ft."},
                {"label": "Divided by 6 instead of 60", "correct": False, "why": "12 × 35² / 6 = 2,450 ft."},
            ],
            "hint": "What is 12 × 35?",
            "explanation": """
The right answer is 245 ft, and each slip has its own number:

* WS at low speed: **420 ft**.
* Half of L: **122.5 ft**.
* W left out: **20.4 ft**.
* ÷ 6 instead of ÷ 60: **2,450 ft**.
""",
            "widget": CLOSURE,
            "config": {"values": {"kind": "merging", "S": 35, "W": 12}},
        },
        {
            "kind": "example",
            "title": "A work zone with two tapers (stretch)",
            "prompt": "On a **50 mi/h** two-lane-each-way highway, a crew first closes the **8-ft** right shoulder, then closes the **12-ft** right lane farther downstream. Find both minimum taper lengths.",
            "steps": [
                {"think": "The shoulder taper: what W and which formula?", "text": "W = 8 ft (the shoulder width). S = 50 ≥ 45: L = 8 × 50 = **400 ft**."},
                {"text": "Shoulder taper ≥ L/3 = 400 / 3 = **133.3 ft**, so lay out at least 134 ft."},
                {"think": "The lane closure: new W, same S.", "text": "W = 12 ft: L = 12 × 50 = **600 ft**. A merging taper uses the full L: **600 ft**."},
            ],
            "explanation": "Each taper gets its own W. Using 12 ft for the shoulder taper (giving 200 ft) is a common slip: it's safe, but not what the question asked. Using 8 ft for the lane taper (400 ft) is unsafe.",
            "widget": CLOSURE,
            "config": {"values": {"kind": "shoulder", "S": 50, "W": 8}},
        },
        {
            "kind": "text",
            "title": "Common mistakes",
            "body": """
* Using **WS** at 40 mi/h or below, or **WS²/60** at 45 mi/h or above.
* Using the **full L** for a shifting or shoulder taper, or a share for a merging taper.
* Using the **wrong W**. W is the width of the shift for *that* taper: a lane width for a lane closure, the shoulder width for a shoulder taper.
* Forgetting that these are **minimums**. Field layouts round up.
""",
        },
        {
            "kind": "check",
            "title": "Last check",
            "prompt": "A **12-ft** lane is closed on a road posted at **40 mi/h**. What is the minimum merging taper length, in feet?",
            "answer": 320,
            "tolerance": 0.5,
            "unit": "ft",
            "hint": "40 mi/h is the top of the low-speed range.",
            "explanation": """
::

    S = 40 ≤ 40:  L = 12 × 40² / 60 = 19,200 / 60 = 320 ft

At exactly 40 mi/h, the low-speed formula still applies.
""",
            "widget": CLOSURE,
            "config": {"values": {"kind": "merging", "S": 40, "W": 12}},
        },
        {
            "kind": "text",
            "title": "On exam day",
            "body": """
Taper criteria and typical layouts for temporary traffic control are in **MUTCD Part 6** (Temporary Traffic Control). The MUTCD is published free by FHWA, so you can study it ahead of time at mutcd.fhwa.dot.gov. Search **taper length** or **merging taper**.

Write three things before computing: the speed (to pick the formula), W for this taper, and the taper type (to pick the share).
""",
        },
    ],
}
