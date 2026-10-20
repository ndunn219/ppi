"""SD1 Stopping sight distance.

Constants match curriculum/solvers.py: t = 2.5 s, a = 11.2 ft/s², g = 32.2
ft/s², 1.47 to convert mi/h to ft/s. Every number was checked in Python.
"""

BARS = "ssd-bars"
SPEED = "ssd-speed"

TUTORIAL = {
    "minutes": 25,
    "blocks": [
        {
            "kind": "text",
            "title": "Two distances add up to one",
            "body": """
A driver sees an object in the road. Before the car stops, two things happen:

1. **Reaction.** The driver perceives the object and moves a foot to the brake. The car keeps going at full speed for the brake reaction time t, usually **2.5 s** for design.
2. **Braking.** The car decelerates to a stop at a comfortable rate a, usually **11.2 ft/s²** for design.

Stopping sight distance (SSD) is the sum: how far ahead the driver must be able to see to stop in time.

::

    SSD = 1.47·V·t + V² / (30 × ((a / 32.2) ± G))
    V = design speed (mi/h),  t = 2.5 s,  a = 11.2 ft/s²
    G = grade as a decimal: + uphill, − downhill
""",
        },
        {
            "kind": "explorer",
            "title": "Build the stopping distance",
            "widget": BARS,
            "body": """
Change the speed, the reaction time and the grade. The amber part is reaction distance, the green part braking distance. The grey bar underneath is the same speed on level ground, so you can see what the grade does.
""",
        },
        {
            "kind": "check",
            "title": "Reaction distance",
            "prompt": "At **50 mi/h** with a brake reaction time of **2.5 s**, how far does the car travel before the brakes are applied, in feet?",
            "answer": 183.75,
            "tolerance": 0.1,
            "unit": "ft",
            "hint": "1.47 converts mi/h to ft/s. Distance = speed × time.",
            "explanation": """
::

    Reaction distance = 1.47 × 50 × 2.5 = 73.5 ft/s × 2.5 s = 183.75 ft

That is more than half a football field travelled before braking even starts.
""",
            "widget": BARS,
            "config": {"values": {"V": 50, "t": 2.5, "G": 0}},
        },
        {
            "kind": "check",
            "title": "Braking distance",
            "prompt": "Still at **50 mi/h** on level ground with a = 11.2 ft/s², what is the braking distance, in feet? Give one decimal place.",
            "answer": 239.6,
            "tolerance": 0.06,
            "unit": "ft",
            "hint": "a / 32.2 = 0.348. On level ground G = 0.",
            "explanation": """
::

    a / 32.2 = 11.2 / 32.2 = 0.3478
    Braking = 50² / (30 × 0.3478) = 2,500 / 10.435 = 239.6 ft
    SSD = 183.75 + 239.6 = 423.3 ft
""",
            "widget": BARS,
            "config": {"values": {"V": 50, "t": 2.5, "G": 0}},
        },
        {
            "kind": "text",
            "title": "Where the 30 comes from",
            "body": """
Braking distance from physics is v² / (2·d), with v in ft/s and d the deceleration. Write v = 1.47V and d = 32.2 × (a/32.2 ± G):

::

    d_b = (1.47V)² / (2 × 32.2 × (a/32.2 ± G))
        = V² / ((2 × 32.2 / 1.47²) × (a/32.2 ± G))
        = V² / (29.8 × (a/32.2 ± G))  ≈  V² / (30 × (a/32.2 ± G))

So the 30 already converts mi/h to ft/s. Keep V in mi/h in the braking term. The term a/32.2 is the deceleration as a fraction of gravity, about 0.35. The grade adds to it uphill and subtracts from it downhill.
""",
        },
        {
            "kind": "explorer",
            "title": "Speed squared",
            "widget": SPEED,
            "body": """
The amber line is reaction distance alone. It grows in a straight line with speed. The green line is the full SSD, which bends upward because braking grows with V². Move the speed to 30 and compare the readout for 60 mi/h.
""",
        },
        {
            "kind": "check",
            "title": "Predict: double the speed",
            "prompt": "If the design speed doubles from 30 to 60 mi/h on level ground, what happens to the **braking** distance? Predict, then check with the explorer.",
            "choices": [
                {"label": "It becomes 4 times as long", "correct": True, "why": "Braking distance goes with V². Twice the speed means 2² = 4 times the distance: 86 ft becomes 345 ft."},
                {"label": "It doubles", "correct": False, "why": "That is what happens to the reaction distance, which is proportional to V. Braking is proportional to V²."},
                {"label": "It stays the same, because deceleration doesn't change", "correct": False, "why": "The deceleration is the same, but there is four times as much kinetic energy to shed."},
                {"label": "It grows by 30 ft, one foot per mi/h", "correct": False, "why": "The relationship isn't linear: braking grows with the square of speed."},
            ],
            "explanation": """
::

    30 mi/h: braking = 900 / 10.435 = 86.3 ft
    60 mi/h: braking = 3,600 / 10.435 = 345.0 ft  (4 times)

The reaction distance only doubles, from 110.3 ft to 220.5 ft. At highway speeds braking dominates SSD, which is why small increases in design speed need much longer sight distance.
""",
            "widget": SPEED,
            "config": {"values": {"V": 30, "t": 2.5, "G": 0}},
        },
        {
            "kind": "example",
            "title": "SSD on level ground (core)",
            "prompt": "Find the stopping sight distance for a design speed of **45 mi/h** on level ground, using t = 2.5 s and a = 11.2 ft/s².",
            "steps": [
                {"think": "Which part needs the 1.47?", "text": "The reaction term: 1.47 × 45 × 2.5 = **165.4 ft**."},
                {"text": "Braking: 45² / (30 × 0.3478) = 2,025 / 10.435 = **194.1 ft**."},
                {"text": "SSD = 165.4 + 194.1 = **359.4 ft**, or about **360 ft**."},
            ],
            "explanation": "At 45 mi/h the two parts are close to equal. At higher speeds braking pulls ahead.",
            "widget": BARS,
            "config": {"values": {"V": 45, "t": 2.5, "G": 0}},
        },
        {
            "kind": "text",
            "title": "Grades",
            "body": """
On a grade, gravity helps or hurts braking:

* **Uphill (+G)** adds to the effective deceleration, so braking distance is shorter.
* **Downhill (−G)** subtracts from it, so braking distance is longer.

Only the braking term changes. The reaction distance is the same, because the car is still at full speed during reaction.

On a two-way road both directions use the same pavement. The downhill direction needs the longer SSD, so it usually governs the design.
""",
        },
        {
            "kind": "check",
            "title": "A downgrade",
            "prompt": "Find the SSD for **60 mi/h** on a **4% downgrade**, with t = 2.5 s and a = 11.2 ft/s². Answer to the nearest foot.",
            "answer": 610.0,
            "tolerance": 0.6,
            "unit": "ft",
            "hint": "Downgrade means G = −0.04, so the denominator is 30 × (0.3478 − 0.04).",
            "explanation": """
::

    Reaction = 1.47 × 60 × 2.5 = 220.5 ft
    Braking  = 3,600 / (30 × (0.3478 − 0.04)) = 3,600 / 9.235 = 389.8 ft
    SSD      = 220.5 + 389.8 = 610.3 ft → 610 ft

On level ground the same speed needs 565.5 ft, so the downgrade adds about 45 ft.
""",
            "widget": BARS,
            "config": {"values": {"V": 60, "t": 2.5, "G": -4}},
        },
        {
            "kind": "check",
            "title": "Spot the slip",
            "prompt": "For the same 60 mi/h, 4% downgrade case, a student gets **530 ft**. Which slip gives that?",
            "choices": [
                {"label": "They used +0.04 for the grade", "correct": True, "why": "With +0.04, braking = 3,600 / (30 × 0.3878) = 309.4 ft and SSD = 529.9 ft. That is the uphill answer."},
                {"label": "They left out the 1.47 in the reaction term", "correct": False, "why": "That gives 60 × 2.5 + 389.8 = 539.8 ft, close but not 530."},
                {"label": "They gave only the braking distance", "correct": False, "why": "Braking alone is 389.8 ft."},
                {"label": "They used t = 2.0 s", "correct": False, "why": "That gives 176.4 + 389.8 = 566.2 ft."},
            ],
            "explanation": """
The correct SSD is 610 ft. Fingerprints of the usual slips:

* Wrong grade sign (uphill): **530 ft**.
* No 1.47 in the reaction term: **540 ft**.
* Braking only: **390 ft**.

Wrong answers that land near the right one are the dangerous ones. Writing "downhill → subtract" beside the formula prevents the first.
""",
            "widget": BARS,
            "config": {"values": {"V": 60, "t": 2.5, "G": 4}},
        },
        {
            "kind": "example",
            "title": "SSD on an upgrade (standard)",
            "prompt": "Find the SSD for a design speed of **55 mi/h** on a **3% upgrade**, with t = 2.5 s and a = 11.2 ft/s².",
            "steps": [
                {"text": "Reaction = 1.47 × 55 × 2.5 = **202.1 ft**."},
                {"think": "Does the upgrade add to or subtract from a/32.2?", "text": "It adds: 0.3478 + 0.03 = **0.3778**."},
                {"text": "Braking = 55² / (30 × 0.3778) = 3,025 / 11.335 = **266.9 ft**."},
                {"text": "SSD = 202.1 + 266.9 = **469.0 ft**. On level ground it would be 492.0 ft."},
            ],
            "explanation": "The upgrade saves about 23 ft, all of it in the braking distance.",
            "widget": BARS,
            "config": {"values": {"V": 55, "t": 2.5, "G": 3}},
        },
        {
            "kind": "example",
            "title": "Which direction governs? (stretch)",
            "prompt": "A two-lane highway runs on a **5% grade** with a design speed of **65 mi/h**. Find the SSD for each direction and say which one the design must provide.",
            "steps": [
                {"text": "Reaction (same both ways) = 1.47 × 65 × 2.5 = **238.9 ft**."},
                {"think": "Downhill: is G added or subtracted?", "text": "Subtracted: 0.3478 − 0.05 = 0.2978. Braking = 4,225 / (30 × 0.2978) = 4,225 / 8.935 = **472.9 ft**. SSD = **711.7 ft**."},
                {"text": "Uphill: 0.3478 + 0.05 = 0.3978. Braking = 4,225 / 11.935 = **354.0 ft**. SSD = **592.9 ft**."},
                {"think": "Which one controls the design?", "text": "The **downhill** direction, at about **712 ft**, because both directions share the road and the longer requirement governs."},
            ],
            "explanation": "The two directions differ by about 119 ft on the same pavement. On divided highways each direction can be designed separately; on a two-lane road the downhill SSD controls.",
            "widget": BARS,
            "config": {"values": {"V": 65, "t": 2.5, "G": -5}},
        },
        {
            "kind": "text",
            "title": "Common mistakes",
            "body": """
* **Forgetting 1.47** in the reaction term. Time in seconds needs speed in ft/s.
* **Adding 1.47** to the braking term. The 30 already handles the conversion.
* **Flipping the grade sign.** Downhill subtracts G and lengthens SSD.
* **Reporting braking distance alone.** SSD includes the reaction distance.
* **Using percent for G.** A 4% grade is 0.04.
""",
        },
        {
            "kind": "text",
            "title": "On exam day",
            "body": """
The SSD equation is in the NCEES Handbook's transportation chapter. Design SSD values by speed are tabulated in the Green Book, Chapter 3 (sight distance). Search **stopping sight distance**.

SSD feeds directly into vertical curve length (VD2) and horizontal sightline offset (HD3) problems. If a later question gives you a design speed but no SSD, this is the first calculation.
""",
        },
    ],
}
