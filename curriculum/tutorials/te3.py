"""TE3 Crash rates for intersections and roadway segments.

Formulas match curriculum/solvers.py. Every number was checked in Python.
"""

RATE = "crash-rate"

TUTORIAL = {
    "minutes": 25,
    "blocks": [
        {
            "kind": "text",
            "title": "Why counts aren't enough",
            "body": """
An intersection with 30 crashes a year sounds worse than one with 10. But if the first carries five times the traffic, each driver there is actually *safer*. To compare locations fairly, divide crashes by **exposure**: how much traffic had the chance to crash.

::

    crash rate = crashes / exposure

Exposure is measured differently for the two kinds of location:

* **Intersections:** vehicles entering, counted in millions of entering vehicles (MEV).
* **Segments:** vehicle-miles travelled, counted in units of 100 million vehicle-miles (100 MVMT).
""",
        },
        {
            "kind": "text",
            "title": "The two formulas",
            "body": """
For an intersection:

::

    R = C × 10⁶ / (365 × N × V)
    C = crashes in the study period
    N = years in the study period
    V = total entering ADT (all approaches, veh/day)

For a segment:

::

    R = C × 10⁸ / (365 × N × V × L)
    V = ADT on the segment (veh/day)
    L = segment length (mi)

The denominator is just exposure counted in vehicles: 365 days × N years × V vehicles per day, times L for vehicle-miles. The 10⁶ or 10⁸ turns the answer into crashes per million, or per hundred million.
""",
        },
        {
            "kind": "explorer",
            "title": "Crashes against exposure",
            "widget": RATE,
            "body": """
The blue bar is exposure and the red dots are crashes. Double the ADT and the bar doubles while the dots stay the same, so the rate halves. Switch to a segment and change its length to see why longer roads need vehicle-miles.
""",
        },
        {
            "kind": "check",
            "title": "An intersection rate",
            "prompt": "An intersection had **20 crashes in 3 years**. The total entering volume is **20,000 veh/day**. What is the crash rate per million entering vehicles? Give two decimal places.",
            "answer": 0.91,
            "tolerance": 0.006,
            "unit": "per MEV",
            "hint": "R = C × 10⁶ / (365 × N × V).",
            "explanation": """
::

    Exposure = 365 × 3 × 20,000 = 21,900,000 = 21.9 MEV
    R = 20 / 21.9 = 0.91 crashes per MEV

Or in one line: 20 × 10⁶ / (365 × 3 × 20,000) = 0.91.
""",
            "widget": RATE,
            "config": {"values": {"mode": "intersection", "C": 20, "N": 3, "V": 20000}},
        },
        {
            "kind": "check",
            "title": "What goes into V?",
            "prompt": "Four approaches enter an intersection with ADTs of **8,000, 6,500, 4,200 and 3,300 veh/day**. What value of V belongs in the intersection rate formula?",
            "choices": [
                {"label": "22,000 veh/day, the sum of all entering approaches", "correct": True, "why": "Exposure at an intersection is every vehicle that enters it, so add every approach."},
                {"label": "8,000 veh/day, the busiest approach", "correct": False, "why": "The quieter approaches carry vehicles that can crash too, so they belong in the exposure."},
                {"label": "5,500 veh/day, the average approach", "correct": False, "why": "Averaging undercounts exposure by a factor of four here."},
                {"label": "11,000 veh/day, half the total, because each vehicle also leaves", "correct": False, "why": "Counting entering vehicles already counts each vehicle once. Don't halve it."},
            ],
            "explanation": """
::

    V = 8,000 + 6,500 + 4,200 + 3,300 = 22,000 veh/day

If the problem gives two-way ADTs on the cross streets instead of entering volumes, read carefully: the formula wants vehicles **entering** the intersection.
""",
        },
        {
            "kind": "example",
            "title": "Intersection rate from approach volumes (core)",
            "prompt": "An intersection's approaches carry **9,000, 7,000, 3,500 and 2,500 veh/day** entering. It had **18 crashes in 3 years**. Find the crash rate per MEV.",
            "steps": [
                {"think": "What is V?", "text": "V = 9,000 + 7,000 + 3,500 + 2,500 = **22,000 veh/day** entering."},
                {"text": "Exposure = 365 × 3 × 22,000 = 24,090,000 = **24.09 MEV**."},
                {"text": "R = 18 / 24.09 = **0.75 crashes per MEV**."},
            ],
            "explanation": "Write exposure out as a separate step. It makes the units obvious and lets you check the order of magnitude: tens of millions of vehicles is typical for a few years at a busy intersection.",
            "widget": RATE,
            "config": {"values": {"mode": "intersection", "C": 18, "N": 3, "V": 22000}},
        },
        {
            "kind": "check",
            "title": "A segment rate",
            "prompt": "A **2-mile** segment with an ADT of **10,000 veh/day** had **30 crashes in 3 years**. What is the crash rate per 100 million vehicle-miles? Give one decimal place.",
            "answer": 137.0,
            "tolerance": 0.06,
            "unit": "per 100 MVMT",
            "hint": "R = C × 10⁸ / (365 × N × V × L). Don't forget the length.",
            "explanation": """
::

    Vehicle-miles = 365 × 3 × 10,000 × 2 = 21,900,000 = 0.219 × 100 MVMT
    R = 30 / 0.219 = 137.0 crashes per 100 MVMT
""",
            "widget": RATE,
            "config": {"values": {"mode": "segment", "C": 30, "N": 3, "V": 10000, "Lmi": 2}},
        },
        {
            "kind": "check",
            "title": "Spot the slip",
            "prompt": "For that segment (30 crashes, 3 years, 10,000 veh/day, 2 miles), a student reports **1.37**. Which slip gives that number?",
            "choices": [
                {"label": "They used 10⁶ instead of 10⁸", "correct": True, "why": "30 × 10⁶ / 21,900,000 = 1.37. That is the intersection multiplier; segments use 100 million vehicle-miles."},
                {"label": "They left out the segment length", "correct": False, "why": "Without L the rate doubles to 274.0, not 1.37."},
                {"label": "They forgot the 365", "correct": False, "why": "Without 365 the rate becomes enormous (about 50,000), not 1.37."},
                {"label": "They used the number of years in the numerator", "correct": False, "why": "That would give 3 × 137 = 411, not 1.37."},
            ],
            "explanation": """
The correct rate is 137.0 per 100 MVMT. Fingerprints of common slips:

* 10⁶ instead of 10⁸: **1.37**, 100 times too small.
* Left out L: **274.0**, too big by the length.
* Left out N: **411**, too big by the years.

An answer far from the typical range for that kind of location is a sign to recheck the multiplier.
""",
        },
        {
            "kind": "example",
            "title": "A rural segment rate (standard)",
            "prompt": "A **4.5-mile** rural highway carries **12,500 veh/day**. Over **5 years** it had **42 crashes**. Find the crash rate per 100 MVMT.",
            "steps": [
                {"think": "Which formula: intersection or segment?", "text": "A length of road, so the segment formula with vehicle-miles."},
                {"text": "Vehicle-miles = 365 × 5 × 12,500 × 4.5 = **102,656,250**, or 1.027 × 100 MVMT."},
                {"text": "R = 42 / 1.027 = **40.9 crashes per 100 MVMT**."},
            ],
            "explanation": "One hundred million vehicle-miles is a lot: this road needed five years to reach it. That is why segment rates are scaled to 10⁸.",
            "widget": RATE,
            "config": {"values": {"mode": "segment", "C": 42, "N": 5, "V": 12500, "Lmi": 4.5}},
        },
        {
            "kind": "check",
            "title": "Which is riskier?",
            "prompt": "Intersection A had **12 crashes in 3 years** with **10,000** entering veh/day. Intersection B had **20 crashes in 3 years** with **30,000** entering veh/day. Which has the higher crash rate?",
            "choices": [
                {"label": "A, at about 1.10 per MEV", "correct": True, "why": "A: 12 / 10.95 = 1.10. B: 20 / 32.85 = 0.61. B has more crashes but three times the traffic."},
                {"label": "B, because it had more crashes", "correct": False, "why": "B's exposure is three times A's, so per vehicle it is safer: 0.61 versus 1.10 per MEV."},
                {"label": "They are the same", "correct": False, "why": "Compute both: 1.10 and 0.61 per MEV."},
                {"label": "It can't be compared without severity data", "correct": False, "why": "Severity matters for prioritizing, but the rate comparison only needs crashes and exposure."},
            ],
            "explanation": """
::

    A: exposure = 365 × 3 × 10,000 = 10.95 MEV,  R = 12 / 10.95 = 1.10
    B: exposure = 365 × 3 × 30,000 = 32.85 MEV,  R = 20 / 32.85 = 0.61

The location with fewer crashes has the higher rate. Ranking by count alone would send safety money to the wrong place.
""",
            "widget": RATE,
            "config": {"values": {"mode": "intersection", "C": 12, "N": 3, "V": 10000}},
        },
        {
            "kind": "example",
            "title": "Counts versus rates on two segments (stretch)",
            "prompt": "Segment 1 is **3.0 mi** long, carries **8,000 veh/day** and had **21 crashes in 3 years**. Segment 2 is **1.2 mi** long, carries **6,000 veh/day** and had **14 crashes in 3 years**. Which has the higher rate, and by how much?",
            "steps": [
                {"text": "Segment 1 vehicle-miles = 365 × 3 × 8,000 × 3.0 = 26,280,000 = **0.2628 × 100 MVMT**."},
                {"text": "R₁ = 21 / 0.2628 = **79.9 per 100 MVMT**."},
                {"think": "Segment 2 has fewer crashes. Do you expect a lower rate?", "text": "Segment 2 vehicle-miles = 365 × 3 × 6,000 × 1.2 = 7,884,000 = **0.07884 × 100 MVMT**."},
                {"text": "R₂ = 14 / 0.07884 = **177.6 per 100 MVMT**, about 2.2 times segment 1's rate."},
            ],
            "explanation": "Segment 2 has two thirds of the crashes but less than a third of the exposure. Its rate is more than double. Short, lightly used roads with a cluster of crashes are exactly what rates are meant to reveal.",
            "widget": RATE,
            "config": {"values": {"mode": "segment", "C": 14, "N": 3, "V": 6000, "Lmi": 1.2}},
        },
        {
            "kind": "check",
            "title": "Put it together",
            "prompt": "Using the four approaches from earlier (total entering **22,000 veh/day**), the intersection had **15 crashes in 4 years**. What is its crash rate per MEV? Give two decimal places.",
            "answer": 0.47,
            "tolerance": 0.006,
            "unit": "per MEV",
            "hint": "Exposure = 365 × 4 × 22,000.",
            "explanation": """
::

    Exposure = 365 × 4 × 22,000 = 32,120,000 = 32.12 MEV
    R = 15 / 32.12 = 0.47 crashes per MEV
""",
            "widget": RATE,
            "config": {"values": {"mode": "intersection", "C": 15, "N": 4, "V": 22000}},
        },
        {
            "kind": "text",
            "title": "Common mistakes",
            "body": """
* **Using the segment multiplier at an intersection**, or the reverse. Intersections: 10⁶, no length. Segments: 10⁸, with length.
* **Using one approach's ADT** at an intersection. Add every entering approach.
* **Forgetting N or 365.** V is a daily volume and the crashes span N years.
* **Ranking by crash counts.** Rates account for exposure; counts don't.

Rates are a first screen. The HSM's predictive methods go further, comparing observed crashes with what similar sites are expected to have.
""",
        },
        {
            "kind": "text",
            "title": "On exam day",
            "body": """
Both rate formulas are in the NCEES Handbook's transportation chapter. Search **crash rate**. For predicted crashes and crash modification factors, the HSM is the reference (Part C for predictive methods, Part D for CMFs).

Before you calculate, circle whether the question is about a point (an intersection) or a length of road (a segment). That one decision picks the formula.
""",
        },
    ],
}
