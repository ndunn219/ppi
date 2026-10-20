"""VD2 Vertical curve length for sight distance.

Every number below was checked in Python. A is in percent throughout.
Crest: 3.5 ft eye, 2.0 ft object (constant 2158). Sag: 2.0 ft headlight,
1 degree upward beam (400 + 3.5S).
"""

PROFILE = "sight-profile"
CHART = "length-chart"

TUTORIAL = {
    "minutes": 30,
    "blocks": [
        {
            "kind": "text",
            "title": "Why curve length depends on sight distance",
            "body": """
A driver must see far enough ahead to stop. Two kinds of vertical curves limit that view in different ways:

* On a **crest**, the hill itself blocks the view. A driver's eye, about **3.5 ft** above the road, must see an object **2.0 ft** high on the far side.
* On a **sag**, daylight sight distance is fine, since you can see across a dip. At **night**, though, the headlights matter. They sit about **2.0 ft** above the road and the beam spreads about **1°** upward. Through a sag, the beam hits the rising road ahead.

A longer curve is flatter. A flatter crest hides less, and a flatter sag lets the beam reach farther. So the minimum length L comes from the sight distance S the road must provide, usually the stopping sight distance.
""",
        },
        {
            "kind": "explorer",
            "title": "See the sightline",
            "widget": PROFILE,
            "config": {"values": {"kind": "crest", "A": 5, "S": 500}},
            "body": """
The curve shown is the *minimum* length for the S you choose. On a crest, the amber sightline just grazes the road. Switch to **Sag** to see the headlight beam land exactly S ahead. Try a small A on a short S: sometimes no curve is needed at all.
""",
        },
        {
            "kind": "check",
            "title": "Predict before you slide",
            "prompt": "On a crest with A = 5%, a stopping sight distance of **450 ft** needs L = 5 × 450² / 2158 = 469 ft, and S < L holds. Predict the length for **S = 900 ft**, then check with the explorer.",
            "choices": [
                {"label": "About 1,877 ft, four times as long", "correct": True, "why": "When S < L, L = AS² / 2158, so L grows with the square of S. Doubling S multiplies L by four: 5 × 900² / 2158 = 1,877 ft."},
                {"label": "About 938 ft, twice as long", "correct": False, "why": "L is not proportional to S. In the S < L formula S is squared, so doubling S quadruples L."},
                {"label": "About 469 ft, the same", "correct": False, "why": "A longer sight distance always needs a flatter crest, so L must grow."},
                {"label": "About 3,754 ft, eight times as long", "correct": False, "why": "That would be L proportional to S³. The formula has S², so the factor is 2² = 4."},
            ],
            "hint": "Look at the S < L formula, L = AS² / 2158. What happens to S² when S doubles?",
            "explanation": """
Both sight distances are in the S < L case, so the squared relationship applies directly:

::

    S = 450 ft:  L = 5 × 450² / 2158 = 469 ft     (469 > 450, so S < L holds)
    S = 900 ft:  L = 5 × 900² / 2158 = 1,877 ft   (1,877 > 900, so S < L holds)

Doubling S quadruples L. That is why high design speeds need such long crests. But the shortcut only works when **both** lengths are in the same case: always check S against L before scaling.
""",
            "widget": PROFILE,
            "config": {"values": {"kind": "crest", "A": 5, "S": 900}},
        },
        {
            "kind": "text",
            "title": "Two cases, two formulas",
            "body": """
Each curve type has two formulas, because the sightline can sit in two places:

* **S < L**: the driver and the object (or the headlight and the point the beam lands) are both *on* the curve.
* **S > L**: the sight distance is longer than the curve, so at least one end lies on a tangent beyond it.

Crest, with a 3.5 ft eye and a 2.0 ft object:

::

    S < L:  L = A·S² / 2158
    S > L:  L = 2S − 2158 / A

Sag, with headlight sight distance:

::

    S < L:  L = A·S² / (400 + 3.5S)
    S > L:  L = 2S − (400 + 3.5S) / A

A = \\|g₁ − g₂\\| in **percent**, and S and L are in feet. The method is always **assume S < L, compute, then check**. If the result is shorter than S, the assumption failed, so use the S > L formula. Where L = S, both formulas give the same answer, so the switch is smooth.
""",
        },
        {
            "kind": "explorer",
            "title": "Where the two formulas meet",
            "widget": CHART,
            "config": {"values": {"kind": "crest", "A": 4, "S": 400}},
            "body": """
The grey curves are each formula on its own. The green line is the length that actually governs. It follows the S > L formula below the dashed L = S line and the S < L formula above it. Change A and the curve type and watch the crossover move.
""",
        },
        {
            "kind": "check",
            "title": "Assume, then check",
            "prompt": "A crest curve joins **+1.5%** to **−2.5%**. The required stopping sight distance is **400 ft**. What is the minimum curve length, in feet?",
            "answer": 260.5,
            "tolerance": 0.6,
            "unit": "ft",
            "hint": "A = 4. Try S < L first: is the length you get longer than 400 ft?",
            "explanation": """
A = \\|1.5 − (−2.5)\\| = 4%.

Assume S < L:

::

    L = 4 × 400² / 2158 = 640,000 / 2158 = 296.6 ft

296.6 ft is **shorter** than S = 400 ft, so the assumption fails. Use S > L:

::

    L = 2 × 400 − 2158 / 4 = 800 − 539.5 = 260.5 ft

Check: 260.5 < 400, so S > L holds. The answer is **260.5 ft**. Answering 297 ft is the classic trap.
""",
            "widget": CHART,
            "config": {"values": {"kind": "crest", "A": 4, "S": 400}},
        },
        {
            "kind": "example",
            "title": "Crest length for stopping sight distance (core)",
            "prompt": "A crest curve joins **+2%** to **−3%**. The stopping sight distance is **500 ft**. Find the minimum length of curve and its K value.",
            "steps": [
                {"think": "What is A? Watch the signs.", "text": "A = \\|2 − (−3)\\| = **5%**. The grades go in opposite directions, so their magnitudes add."},
                {"think": "Which case do you assume first?", "text": "Assume S < L: L = 5 × 500² / 2158 = 1,250,000 / 2158 = **579.2 ft**."},
                {"text": "Check: 579.2 > 500, so S < L holds. **L = 579 ft.**"},
                {"text": "K = L / A = 579.2 / 5 = **115.8 ft per percent**. K is the length needed for each 1% change in grade."},
            ],
            "explanation": "Design tables often list K instead of L, so a designer multiplies K by A. Both come from the same equation, and table K values are rounded for design.",
            "widget": PROFILE,
            "config": {"values": {"kind": "crest", "A": 5, "S": 500}},
        },
        {
            "kind": "text",
            "title": "Sag curves: the headlight beam",
            "body": """
On a sag the road ahead rises into the headlight beam. The beam starts 2.0 ft above the road and angles up about 1°. The tan 1° ≈ 0.0175 slope is where the **3.5S** term comes from: 200 × 0.0175 ≈ 3.5. The **400** comes from the 2.0 ft headlight height (200 × 2.0).

Two habits prevent most sag errors:

* Don't use 2158 on a sag. That constant is for an eye and an object over a crest.
* Use the same assume-then-check routine as for crests.

Other controls, such as rider comfort, drainage and appearance, can also set a sag's length. This lesson covers the headlight criterion only.
""",
        },
        {
            "kind": "check",
            "title": "Which formula governs?",
            "prompt": "A sag curve joins **−3%** to **+3%**, and the headlight sight distance must be **450 ft**. Which result is the minimum length?",
            "choices": [
                {"label": "615 ft, from the S < L formula", "correct": True, "why": "6 × 450² / (400 + 1,575) = 1,215,000 / 1,975 = 615 ft, and 615 > 450, so the S < L assumption holds."},
                {"label": "571 ft, from the S > L formula", "correct": False, "why": "2 × 450 − 1,975 / 6 = 571 ft, but the S > L formula only applies when the result is shorter than S. 571 is longer than 450."},
                {"label": "563 ft, from the crest formula", "correct": False, "why": "6 × 450² / 2158 = 563 ft uses the crest constant. A sag uses 400 + 3.5S."},
                {"label": "6.2 ft, with A as 0.06", "correct": False, "why": "The formula takes A in percent (6), not as a decimal."},
            ],
            "hint": "A = 6. Compute the S < L result and compare it with 450 ft.",
            "explanation": """
::

    A = |−3 − 3| = 6%
    400 + 3.5 × 450 = 1,975
    L = 6 × 450² / 1,975 = 615.2 ft    (615 > 450: S < L holds)

The figure shows the beam leaving the headlight at the PVC and landing on the road 450 ft ahead, just inside the curve.
""",
            "widget": PROFILE,
            "config": {"values": {"kind": "sag", "A": 6, "S": 450}},
        },
        {
            "kind": "example",
            "title": "Sag length when the assumption fails (standard)",
            "prompt": "A sag curve joins **−2.5%** to **+1.5%**. The stopping sight distance is **400 ft**. Find the minimum length for headlight sight distance.",
            "steps": [
                {"text": "A = \\|−2.5 − 1.5\\| = **4%**. The term 400 + 3.5 × 400 = **1,800**."},
                {"think": "Assume S < L. What length do you get, and does it pass the check?", "text": "L = 4 × 400² / 1,800 = 640,000 / 1,800 = **355.6 ft**. That is *shorter* than 400 ft, so S < L fails."},
                {"think": "Which formula now, and what is its result?", "text": "S > L: L = 2 × 400 − 1,800 / 4 = 800 − 450 = **350 ft**."},
                {"text": "Check: 350 < 400, so S > L holds. **L = 350 ft.**"},
            ],
            "explanation": "The two results, 355.6 and 350 ft, are close because the resulting L (350 ft) is close to S (400 ft). Close to the crossover, picking the wrong formula costs little. Far from it, the error can be large.",
            "widget": PROFILE,
            "config": {"values": {"kind": "sag", "A": 4, "S": 400}},
        },
        {
            "kind": "check",
            "title": "Your turn: a sag",
            "prompt": "A sag curve joins **−2.5%** to **+1.5%** with S = **400 ft**. You found L = 350 ft. What **K value** does that give?",
            "answer": 87.5,
            "tolerance": 0.1,
            "unit": "ft per %",
            "hint": "K = L / A.",
            "explanation": """
::

    K = L / A = 350 / 4 = 87.5 ft per percent of grade change

A designer with a table of K values would multiply back: L = K × A. Keep the units straight: K is feet of curve per 1% of A.
""",
        },
        {
            "kind": "text",
            "title": "Common mistakes",
            "body": """
* **Computing A wrong.** From +2% to −3%, A = 5, not 1. Subtract the grades with their signs.
* **Using A as a decimal.** These formulas take A in percent, and a decimal makes L about 100 times too small.
* **Skipping the check.** Always compare the result with S and switch formulas if the assumption fails.
* **Mixing up the constants.** 2158 is for crests only, and 400 + 3.5S for sags only.
* **Forgetting to square S** in the S < L formulas.
""",
        },
        {
            "kind": "check",
            "title": "Spot the slip",
            "prompt": "For a crest from **+2%** to **−3%** with S = 500 ft, a student reports a minimum length of **5.8 ft**. Which mistake gives that?",
            "choices": [
                {"label": "Used A = 0.05 instead of 5", "correct": True, "why": "0.05 × 500² / 2158 = 5.79 ft, exactly 100 times too small."},
                {"label": "Used the sag formula", "correct": False, "why": "5 × 500² / (400 + 1,750) = 581 ft, close to the right answer, not 5.8."},
                {"label": "Used the S > L formula", "correct": False, "why": "2 × 500 − 2158 / 5 = 568 ft."},
                {"label": "Forgot to square S", "correct": False, "why": "5 × 500 / 2158 = 1.2 ft."},
            ],
            "hint": "The right answer is 579 ft. What would make it exactly 100 times smaller?",
            "explanation": """
The right answer is 579 ft (from the core example). Each slip leaves its own number:

* A as a decimal: **5.8 ft** (100 times too small).
* Forgot to square S: **1.2 ft**.
* Used the S > L formula without checking: **568 ft**.
* Used the sag formula on a crest: **581 ft**. This one is dangerous because it looks reasonable.

When an answer is wildly small, suspect the units of A first.
""",
            "widget": PROFILE,
            "config": {"values": {"kind": "crest", "A": 5, "S": 500}},
        },
        {
            "kind": "example",
            "title": "Is an existing crest long enough? (stretch)",
            "prompt": "An existing crest curve is **600 ft** long with A = **4%**. The design speed is 60 mi/h on essentially level grades. Using SSD = 1.47Vt + V² / (30(a/32.2)) with t = 2.5 s and a = 11.2 ft/s², is the curve long enough for stopping sight distance?",
            "steps": [
                {"think": "What sight distance is needed?", "text": "SSD = 1.47 × 60 × 2.5 + 60² / (30 × 11.2/32.2) = 220.5 + 345.0 = **565.5 ft**."},
                {"think": "Which formula for the required length, and does its check pass?", "text": "Assume S < L: L = 4 × 565.5² / 2158 = **592.8 ft**. Check: 565.5 < 592.8, so it holds."},
                {"text": "Required 593 ft ≤ existing 600 ft. **The curve is long enough**, with about 7 ft to spare."},
                {"think": "Work it the other way: how much sight distance does the 600-ft curve provide?", "text": "Solve 600 = 4S² / 2158 for S: S = √(2158 × 600 / 4) = **569 ft**, which is at least the 566 ft needed. Same conclusion."},
            ],
            "explanation": "Checking an existing curve can go either way: compute the required L from S, or the available S from L. The second is handy when a question asks for the highest safe speed. Note how small the margin is here: on a downgrade, or with a longer reaction time, this curve would fall short. The verdict also relies on the computed 565.5 ft; a rounded-up design SSD of 570 ft would need 4 × 570² / 2158 = 602 ft, slightly more than the curve provides.",
            "widget": PROFILE,
            "config": {"values": {"kind": "crest", "A": 4, "S": 565.5}},
        },
        {
            "kind": "check",
            "title": "Last check: a long sight distance on a gentle crest",
            "prompt": "A crest curve has A = **6%** and a required S of **300 ft**. What is the minimum length of curve, in feet?",
            "answer": 240.3,
            "tolerance": 0.5,
            "unit": "ft",
            "hint": "Try S < L, then compare the result with 300 ft.",
            "explanation": """
::

    S < L try: 6 × 300² / 2158 = 250.2 ft   (250 < 300: fails)
    S > L:     2 × 300 − 2158 / 6 = 600 − 359.7 = 240.3 ft   (240 < 300: holds)

The minimum length is **240.3 ft**. The S < L try was close, but its check failed, so it doesn't govern.
""",
            "widget": CHART,
            "config": {"values": {"kind": "crest", "A": 6, "S": 300}},
        },
        {
            "kind": "text",
            "title": "On exam day",
            "body": """
The crest and sag length equations and the K tables are in the Green Book, Chapter 3 (vertical alignment). The NCEES Handbook's transportation chapter has the equations too. Search **crest vertical curve**, **sag vertical curve** or **K value**.

Write "assume S < L" on your scratch sheet every time, then circle the check. It takes five seconds and catches the most common trap in this topic.
""",
        },
    ],
}
