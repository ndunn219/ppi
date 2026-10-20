"""TE2 Signal timing: yellow change interval and Webster's cycle length.

Constants match curriculum/solvers.py: t = 1.0 s, a = 10 ft/s², g = 32.2
ft/s², 1.47 to convert mi/h to ft/s. Every number was checked in Python.
"""

YELLOW = "yellow-interval"
WEBSTER = "webster-cycle"

TUTORIAL = {
    "minutes": 30,
    "blocks": [
        {
            "kind": "text",
            "title": "What the yellow is for",
            "body": """
When a signal turns yellow, every approaching driver makes a choice: stop, or keep going. The yellow change interval is sized so that **either choice is safe**:

* A driver far enough back can perceive the yellow, react and brake to a stop at the stop bar.
* A driver too close to stop comfortably can keep going at the approach speed and reach the stop bar before the red.

The kinematic formula:

::

    Y = t + v / (2a + 2Gg)
    t = perception-reaction time (s), usually 1.0
    v = approach speed (ft/s) = 1.47 × V (mi/h)
    a = comfortable deceleration (ft/s²), usually 10
    G = grade as a decimal (+ uphill, − downhill)
    g = 32.2 ft/s²

The first term covers the reaction time. The second is the time it takes to cover the braking distance at the approach speed.
""",
        },
        {
            "kind": "explorer",
            "title": "Why the yellow and the stopping distance match",
            "widget": YELLOW,
            "body": """
Move the speed and the grade. The top bar is the distance a driver needs to stop. The bottom bar is how far a driver who keeps going travels during the yellow. They are **always the same length**: the yellow lasts exactly as long as it takes to cover the stopping distance at the approach speed.
""",
        },
        {
            "kind": "check",
            "title": "Compute a yellow",
            "prompt": "An approach on level ground has a speed of **40 mi/h**. Using t = 1.0 s and a = 10 ft/s², what yellow change interval is needed, in seconds? Give one decimal place.",
            "answer": 3.9,
            "tolerance": 0.05,
            "unit": "s",
            "hint": "Convert 40 mi/h to ft/s first. On level ground the grade term is zero.",
            "explanation": """
::

    v = 1.47 × 40 = 58.8 ft/s
    Y = 1.0 + 58.8 / (2 × 10 + 0) = 1.0 + 2.94 = 3.94 s → 3.9 s
""",
            "widget": YELLOW,
            "config": {"values": {"V": 40, "G": 0, "t": 1}},
        },
        {
            "kind": "check",
            "title": "Predict the effect of a downgrade",
            "prompt": "The same 40 mi/h approach is moved to a **4% downgrade**. Before you calculate, what happens to the yellow? Then try it in the explorer.",
            "choices": [
                {"label": "It gets longer", "correct": True, "why": "Going downhill, gravity works against braking, so stopping takes longer and the yellow must cover a longer stopping distance."},
                {"label": "It gets shorter", "correct": False, "why": "That is what an upgrade does: gravity helps you stop. A downgrade does the opposite."},
                {"label": "It stays the same, because grade only affects trucks", "correct": False, "why": "Grade changes the effective deceleration of every vehicle, so it enters the formula through 2Gg."},
                {"label": "It can't be computed without the cross slope", "correct": False, "why": "Cross slope doesn't enter the yellow formula; only the longitudinal grade does."},
            ],
            "explanation": """
On a downgrade G is **negative**, which shrinks the denominator:

::

    2a + 2Gg = 20 + 2(−0.04)(32.2) = 20 − 2.576 = 17.424 ft/s²
    Y = 1.0 + 58.8 / 17.424 = 1.0 + 3.37 = 4.37 s

About 0.4 s longer than on level ground. The sign convention is the whole trick: + uphill, − downhill.
""",
            "widget": YELLOW,
            "config": {"values": {"V": 40, "G": -4, "t": 1}},
        },
        {
            "kind": "check",
            "title": "Speed and grade together",
            "prompt": "An approach has a speed of **45 mi/h** on a **3% downgrade**. Using t = 1.0 s, a = 10 ft/s² and 1.47 to convert mi/h to ft/s, what yellow interval is needed, in seconds? Give two decimal places.",
            "answer": 4.66,
            "tolerance": 0.006,
            "unit": "s",
            "hint": "v = 1.47 × 45. For a 3% downgrade, G = −0.03.",
            "explanation": """
::

    v = 1.47 × 45 = 66.15 ft/s
    2a + 2Gg = 20 + 2(−0.03)(32.2) = 20 − 1.932 = 18.068 ft/s²
    Y = 1.0 + 66.15 / 18.068 = 1.0 + 3.661 = 4.66 s

Many agencies round up to the next 0.1 s, so this would be posted as 4.7 s.
""",
            "widget": YELLOW,
            "config": {"values": {"V": 45, "G": -3, "t": 1}},
        },
        {
            "kind": "example",
            "title": "Yellow on an upgrade (core)",
            "prompt": "Find the yellow change interval for a **35 mi/h** approach on a **2% upgrade**, with t = 1.0 s and a = 10 ft/s².",
            "steps": [
                {"think": "What unit does v need to be in?", "text": "ft/s: v = 1.47 × 35 = **51.45 ft/s**."},
                {"think": "Is G positive or negative here?", "text": "Upgrade, so G = +0.02. Denominator = 20 + 2(0.02)(32.2) = 20 + 1.288 = **21.288 ft/s²**."},
                {"text": "Y = 1.0 + 51.45 / 21.288 = 1.0 + 2.417 = **3.42 s**."},
            ],
            "explanation": "On an upgrade the yellow is a little shorter than on level ground (3.57 s at 35 mi/h), because gravity helps the driver stop.",
            "widget": YELLOW,
            "config": {"values": {"V": 35, "G": 2, "t": 1}},
        },
        {
            "kind": "text",
            "title": "How long should the whole cycle be?",
            "body": """
Every phase change wastes a few seconds: drivers react slowly at the start of green, and the yellow and all-red are only partly used. That **lost time L** is fixed per cycle. Short cycles waste a larger share of each hour in lost time. Long cycles make vehicles wait longer. Webster found the cycle that minimizes delay:

::

    C₀ = (1.5L + 5) / (1 − Y)
    L = total lost time per cycle (s)
    Y = sum of the critical flow ratios (v/s), one per phase

Each flow ratio y = v/s is the share of time a movement needs green: its arrival flow divided by its saturation flow. Y adds the critical ones. If Y = 0.6, the critical movements need 60% of the time just to clear their traffic.
""",
        },
        {
            "kind": "explorer",
            "title": "Watch the cycle blow up",
            "widget": WEBSTER,
            "body": """
Slide Y from 0.3 toward 0.9. At low Y the cycle barely changes. Near 1 it shoots up, because almost all the time is needed to serve the critical flows and almost nothing is left over. More lost time raises the whole curve.
""",
        },
        {
            "kind": "check",
            "title": "Compute Webster's cycle",
            "prompt": "A signal has **12 s** of total lost time per cycle and a sum of critical flow ratios **Y = 0.60**. What is Webster's optimum cycle length, in seconds? Give one decimal place.",
            "answer": 57.5,
            "tolerance": 0.05,
            "unit": "s",
            "hint": "C₀ = (1.5L + 5) / (1 − Y). The denominator is 1 − Y, not Y.",
            "explanation": """
::

    C₀ = (1.5 × 12 + 5) / (1 − 0.60) = 23 / 0.40 = 57.5 s

In practice you'd round to a convenient length such as 60 s.
""",
            "widget": WEBSTER,
            "config": {"values": {"L": 12, "Y": 0.6}},
        },
        {
            "kind": "check",
            "title": "Predict the jump",
            "prompt": "With L = 12 s, the critical flow ratios grow from **Y = 0.80** to **Y = 0.90**. Roughly what happens to Webster's cycle? Predict, then check with the explorer.",
            "choices": [
                {"label": "It doubles, from 115 s to 230 s", "correct": True, "why": "1 − Y halves from 0.20 to 0.10, so C₀ = 23 / (1 − Y) doubles."},
                {"label": "It grows by about 10%, since Y grew by 0.1", "correct": False, "why": "C₀ depends on 1 / (1 − Y), not on Y directly, so equal steps in Y give bigger and bigger jumps."},
                {"label": "It stays about the same", "correct": False, "why": "Near Y = 1 the cycle is extremely sensitive. Here it doubles."},
                {"label": "It gets shorter, because traffic flows better", "correct": False, "why": "Higher flow ratios mean more demand, which always lengthens the cycle."},
            ],
            "explanation": """
::

    Y = 0.80:  C₀ = 23 / 0.20 = 115 s
    Y = 0.90:  C₀ = 23 / 0.10 = 230 s

This is why intersections near capacity are so hard to time: small growth in demand calls for very long cycles. When Y approaches 1, the answer is more capacity, not a longer cycle.
""",
            "widget": WEBSTER,
            "config": {"values": {"L": 12, "Y": 0.9}},
        },
        {
            "kind": "check",
            "title": "Spot the slip",
            "prompt": "For L = 12 s and Y = 0.60, a student reports **C₀ = 38 s**. What did they do?",
            "choices": [
                {"label": "Divided by Y instead of 1 − Y", "correct": True, "why": "23 / 0.60 = 38.3 s. The denominator must be the share of time left over, 1 − Y."},
                {"label": "Left out the 1.5 multiplier", "correct": False, "why": "(12 + 5) / 0.40 = 42.5 s, not 38 s."},
                {"label": "Divided only the 5 by 1 − Y", "correct": False, "why": "1.5 × 12 + 5 / 0.40 = 18 + 12.5 = 30.5 s."},
                {"label": "Nothing: 38 s is right", "correct": False, "why": "The correct cycle is 23 / 0.40 = 57.5 s."},
            ],
            "explanation": """
Each slip has a fingerprint:

* Divided by Y: **38.3 s**.
* Dropped the 1.5: **42.5 s**.
* Divided only the 5: **30.5 s**.
* Correct: **57.5 s**.

A useful check: C₀ must exceed the minimum cycle L / (1 − Y), the shortest cycle that clears the critical flows. Here that is 30 s.
""",
        },
        {
            "kind": "example",
            "title": "Cycle length and green splits (standard)",
            "prompt": "A three-phase signal loses **4 s per phase**. The critical flow ratios are **0.25, 0.20 and 0.15**. Find Webster's cycle and split the effective green in proportion to the flow ratios.",
            "steps": [
                {"think": "What is the total lost time per cycle?", "text": "L = 3 × 4 = **12 s**."},
                {"text": "Y = 0.25 + 0.20 + 0.15 = **0.60**."},
                {"text": "C₀ = (1.5 × 12 + 5) / (1 − 0.60) = 23 / 0.40 = **57.5 s**."},
                {"think": "How much of the cycle is effective green?", "text": "Effective green = C₀ − L = 57.5 − 12 = **45.5 s**."},
                {"text": "Split in proportion to y: phase 1 gets 45.5 × 0.25/0.60 = **19.0 s**, phase 2 gets 45.5 × 0.20/0.60 = **15.2 s**, phase 3 gets 45.5 × 0.15/0.60 = **11.4 s**."},
            ],
            "explanation": "The three greens add to 45.5 s before rounding, and with 12 s of lost time make the 57.5-s cycle. Giving each phase green in proportion to its flow ratio equalizes how saturated the phases are.",
            "widget": WEBSTER,
            "config": {"values": {"L": 12, "Y": 0.6}},
        },
        {
            "kind": "example",
            "title": "A steep downhill approach (stretch)",
            "prompt": "A **55 mi/h** approach comes down a **5% grade**. Using t = 1.0 s and a = 10 ft/s², find the yellow interval, then confirm that a driver who keeps going covers exactly the stopping distance during it.",
            "steps": [
                {"text": "v = 1.47 × 55 = **80.85 ft/s**."},
                {"think": "Sign of G?", "text": "Downgrade, so G = −0.05. Denominator = 20 + 2(−0.05)(32.2) = 20 − 3.22 = **16.78 ft/s²**."},
                {"text": "Y = 1.0 + 80.85 / 16.78 = 1.0 + 4.818 = **5.82 s**."},
                {"think": "What is the stopping distance with this deceleration?", "text": "Reaction 80.85 × 1.0 = 80.85 ft, plus braking 80.85² / 16.78 = 389.55 ft, for **470.4 ft**."},
                {"text": "Distance covered during the yellow: 80.85 × 5.818 = **470.4 ft**. The same."},
            ],
            "explanation": "Multiply the yellow formula by v and you get v·t + v²/(2a + 2Gg), the stopping distance. That identity is the reason the formula looks the way it does.",
            "widget": YELLOW,
            "config": {"values": {"V": 55, "G": -5, "t": 1}},
        },
        {
            "kind": "text",
            "title": "Common mistakes",
            "body": """
* **Leaving speed in mi/h** in the yellow formula. It needs ft/s: multiply by 1.47.
* **Using percent for G.** A 3% grade is 0.03.
* **Flipping the grade sign.** Uphill is +, downhill is −. Downhill lengthens the yellow.
* **Dividing by Y** in Webster's formula. It is 1 − Y.
* **Forgetting that L is per cycle.** Add up the lost time of every phase.
""",
        },
        {
            "kind": "text",
            "title": "On exam day",
            "body": """
The yellow change and cycle length formulas are in the NCEES Handbook's transportation chapter. Search **yellow** or **cycle length**. The MUTCD, Part 4, governs how yellow and red clearance intervals are displayed. The HCM's signalized intersection chapter covers flow ratios and capacity in depth.

Write the sign of the grade next to the problem before you start. It is the most common slip in signal timing questions.
""",
        },
    ],
}
