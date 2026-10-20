"""HD2 Superelevation and side friction.

Every number below was worked by hand and checked in Python. Side friction
factors are the ones the course's problems use (the min_radius solver):
40 mi/h 0.16, 45 0.15, 50 0.14, 55 0.13, 60 0.12, 65 0.11, 70 0.10.
"""

BANK = "banked-curve"
CHART = "rmin-chart"

TUTORIAL = {
    "minutes": 25,
    "blocks": [
        {
            "kind": "text",
            "title": "What holds a car on a curve",
            "body": """
A vehicle on a curve needs a sideways force pushing it **toward the center**, or it carries straight on. Two things supply that force:

* **Superelevation e**: the road is tilted, so part of the vehicle's weight pushes it toward the inside. e is the cross slope in ft/ft (6% is 0.06).
* **Side friction f**: the tires grip the pavement sideways. f is the share of the vehicle's weight that friction supplies.

The faster the vehicle and the tighter the curve, the more force is needed. Design keeps the friction demand comfortably below what tires can actually deliver. The design f values fall as speed rises, because drivers tolerate less sideways push at speed.
""",
        },
        {
            "kind": "text",
            "title": "The point-mass equation",
            "body": """
Balancing the forces on a vehicle treated as a single point gives:

::

    e + f = V² / (15 R)
    V in mi/h, R in ft, e and f as decimals

Rearranged for the two things you are usually asked:

::

    R_min = V² / (15 (e_max + f_max))      the sharpest curve allowed
    e     = V² / (15 R) − f                the superelevation a curve needs

The right-hand side, V²/(15R), is the **demand**. The left-hand side is the **supply**.
""",
        },
        {
            "kind": "explorer",
            "title": "Balance the curve",
            "widget": BANK,
            "body": "Change speed, radius and superelevation. The red bar is what the turn needs; the stacked bar is what the slope (green) and friction (amber) supply. When the amber part would have to rise past the dashed line, the curve is too sharp for that speed.",
        },
        {
            "kind": "check",
            "title": "Where does the 15 come from?",
            "prompt": "Starting from e + f = v² / (gR), with v in ft/s and g = 32.2 ft/s², convert v to mi/h using 1 mi/h = 1.4667 ft/s. The equation becomes e + f = V² / (k R). What is k, to two decimals?",
            "answer": 14.97,
            "tolerance": 0.01,
            "unit": "",
            "hint": "v² = (1.4667 V)². Divide 32.2 by 1.4667².",
            "explanation": """
::

    v² / (gR) = (1.4667 V)² / (32.2 R) = 2.1512 V² / (32.2 R) = V² / (14.97 R)

So the 15 is just 14.97, rounded. It already converts mi/h to ft/s, which is why **V stays in mi/h**. Converting V to ft/s yourself and still dividing by 15 gives an answer 2.15 times too big.
""",
        },
        {
            "kind": "check",
            "title": "Predict first",
            "prompt": "With e = 0.06, the minimum radius at 40 mi/h is 485 ft. Predict the minimum radius at **60 mi/h**, using the design friction values (0.16 at 40 mi/h, 0.12 at 60 mi/h). Then check with the chart explorer further down.",
            "choices": [
                {"label": "About 1,333 ft, nearly 2.75 times as large", "correct": True, "why": "3,600 / (15 × 0.18) = 1,333 ft. Speed rose 1.5 times, so V² rose 2.25 times, and the allowed friction fell from 0.16 to 0.12 too."},
                {"label": "About 727 ft, 1.5 times as large", "correct": False, "why": "Radius grows with V², not V."},
                {"label": "About 1,091 ft, 2.25 times as large", "correct": False, "why": "That accounts for V² but not for the drop in allowed friction at higher speed."},
                {"label": "About 485 ft: the radius depends on e, not speed", "correct": False, "why": "Speed is the biggest driver: it enters squared."},
            ],
            "explanation": """
::

    40 mi/h:  R = 1,600 / (15 × (0.06 + 0.16)) = 1,600 / 3.30 = 484.8 ft
    60 mi/h:  R = 3,600 / (15 × (0.06 + 0.12)) = 3,600 / 2.70 = 1,333.3 ft

Ratio = 2.75. Two effects compound: V² grows, and the design friction shrinks. That's why high-speed roads need such gentle curves.
""",
            "widget": CHART,
            "config": {"values": {"e": 0.06, "V": 60}},
        },
        {
            "kind": "example",
            "title": "Minimum radius (core)",
            "prompt": "A highway has a design speed of **60 mi/h** and a maximum superelevation of **0.08**. The design side friction factor at 60 mi/h is **0.12**. What is the minimum radius?",
            "steps": [
                {"think": "Which form of the equation answers \"sharpest allowed\"?", "text": "R_min = V² / (15 (e_max + f_max))."},
                {"text": "e_max + f_max = 0.08 + 0.12 = **0.20**."},
                {"think": "Does V need converting?", "text": "No: the 15 already handles mi/h. R_min = 60² / (15 × 0.20) = 3,600 / 3.0 = **1,200 ft**."},
            ],
            "explanation": "Any radius of 1,200 ft or more works at 60 mi/h with e up to 0.08. A smaller radius would need more friction than the design allows.",
            "widget": BANK,
            "config": {"values": {"V": 60, "R": 1200, "e": 0.08}},
        },
        {
            "kind": "check",
            "title": "Minimum radius at 50 mi/h",
            "prompt": "Design speed 50 mi/h, e_max = 0.06, f = 0.14. What is the minimum radius, in feet?",
            "answer": 833.33,
            "tolerance": 0.5,
            "unit": "ft",
            "hint": "Add e and f first, then multiply by 15.",
            "explanation": """
::

    R_min = 50² / (15 × (0.06 + 0.14)) = 2,500 / 3.0 = 833.3 ft

In practice a designer would round up to a convenient radius, never down.
""",
            "widget": BANK,
            "config": {"values": {"V": 50, "R": 850, "e": 0.06}},
        },
        {
            "kind": "check",
            "title": "Spot the slip",
            "prompt": "For the same problem (V = 50 mi/h, e = 0.06, f = 0.14), a student gets **2,404 ft**. What did they do?",
            "choices": [
                {"label": "Left out the parentheses: V² / (15e + f)", "correct": True, "why": "2,500 / (15 × 0.06 + 0.14) = 2,500 / 1.04 = 2,404 ft. The 15 must multiply the whole sum."},
                {"label": "Converted V to ft/s", "correct": False, "why": "That gives (73.3)² / 3.0 = 1,793 ft."},
                {"label": "Left out the friction", "correct": False, "why": "2,500 / (15 × 0.06) = 2,778 ft."},
                {"label": "Used e as a percent", "correct": False, "why": "2,500 / (15 × 6.14) = 27 ft, absurdly small."},
            ],
            "explanation": """
Each slip has a fingerprint, so a wrong answer tells you which step to recheck:

* No parentheses: **2,404 ft**.
* V in ft/s: **1,793 ft**.
* Friction left out: **2,778 ft**.
* e in percent: about **27 ft**.

The correct answer is 833 ft.
""",
        },
        {
            "kind": "text",
            "title": "Solving for superelevation",
            "body": """
When the radius is fixed (by terrain or right of way), the question becomes: how much superelevation does the curve need?

::

    e = V² / (15 R) − f

Friction is **subtracted** because it already supplies part of the force. The slope only has to provide the rest. If the result exceeds e_max, the curve can't be built for that speed: lower the speed or flatten the curve.

This is the **minimum** e, with friction at its design limit. Agencies' superelevation distribution tables usually assign more than this minimum, so drivers use less friction. If the result is negative, friction alone could hold the curve; whether normal cross slope (crown) is kept then depends on the agency's distribution table.
""",
        },
        {
            "kind": "check",
            "title": "Superelevation needed",
            "prompt": "A curve with R = 700 ft carries traffic at 45 mi/h. Using f = 0.15, what superelevation does it need? Give a decimal (for example 0.052).",
            "answer": 0.0429,
            "tolerance": 0.0006,
            "unit": "ft/ft",
            "hint": "Compute the demand V²/(15R) first, then subtract f.",
            "explanation": """
::

    V² / (15 R) = 2,025 / 10,500 = 0.1929
    e = 0.1929 − 0.15 = 0.043 ft/ft  (4.3%)

If you got 0.343, you added f instead of subtracting it.
""",
            "widget": BANK,
            "config": {"values": {"V": 45, "R": 700, "e": 0.043}},
        },
        {
            "kind": "example",
            "title": "Superelevation for a given curve (standard)",
            "prompt": "A curve has a radius of **1,100 ft** and a design speed of **55 mi/h**. The design friction factor is **0.13**. What superelevation is required, and is it within e_max = 0.08?",
            "steps": [
                {"think": "What is the demand, V²/(15R)?", "text": "55² / (15 × 1,100) = 3,025 / 16,500 = **0.1833**."},
                {"text": "e = 0.1833 − 0.13 = **0.0533 ft/ft**, about 5.3%."},
                {"text": "0.053 ≤ 0.08, so the curve works. This is the minimum e with friction at its design limit; the agency's superelevation distribution table usually assigns somewhat more."},
            ],
            "explanation": "In the figure, the green part of the supply bar is the 0.053 from the slope and the amber part is the 0.13 from friction, together matching the 0.183 demand.",
            "widget": BANK,
            "config": {"values": {"V": 55, "R": 1100, "e": 0.0533}},
        },
        {
            "kind": "explorer",
            "title": "Minimum radius across speeds",
            "widget": CHART,
            "body": "Change e_max and watch the whole curve move. Compare it with the dashed line for no superelevation: every bit of e buys a tighter allowable curve.",
        },
        {
            "kind": "example",
            "title": "What speed can this curve carry? (stretch)",
            "prompt": "An existing curve has R = **900 ft** and e_max = **0.08**. Using the design friction factors (0.14 at 50 mi/h, 0.13 at 55 mi/h), what is the highest design speed, in 5 mi/h steps, the curve supports?",
            "steps": [
                {"think": "Why can't you just solve for V directly?", "text": "f depends on V, so test speeds one at a time: at each one, compute the e the curve would need and compare it with 0.08."},
                {"text": "At 55 mi/h: e = 3,025 / (15 × 900) − 0.13 = 0.2241 − 0.13 = **0.094**. More than 0.08: too fast."},
                {"text": "At 50 mi/h: e = 2,500 / 13,500 − 0.14 = 0.1852 − 0.14 = **0.045**. Within 0.08: works."},
                {"text": "The highest design speed is **50 mi/h**. (Solving with f = 0.13 fixed would give about 53 mi/h, which isn't a design speed step.)"},
            ],
            "explanation": "This trial approach checks an existing curve against design criteria: the friction value moves with the speed being tested.",
            "widget": BANK,
            "config": {"values": {"V": 55, "R": 900, "e": 0.08}},
        },
        {
            "kind": "check",
            "title": "Why cap superelevation?",
            "prompt": "Why don't designers simply use a very large e (say 0.20) on every sharp curve?",
            "choices": [
                {"label": "Slow or stopped vehicles would slide toward the inside, especially on ice", "correct": True, "why": "A steep cross slope that suits fast traffic is too steep for slow traffic, so slow vehicles need friction pointing outward to stay put. On ice they would slide down the slope."},
                {"label": "The equation stops working above 0.12", "correct": False, "why": "The point-mass equation still balances forces at any e. The limit is practical, not mathematical."},
                {"label": "Superelevation only helps at low speeds", "correct": False, "why": "It helps most at high speed, where friction alone wouldn't be enough."},
                {"label": "Friction is always larger than e", "correct": False, "why": "Not necessarily; the explorer shows cases where e supplies most of the force."},
            ],
            "explanation": """
Set the explorer to 40 mi/h, R = 2,000 ft and e = 0.12. The demand is only 0.053, less than e, so the friction needed is **negative**: friction must push outward to keep a slow vehicle from sliding in.

Agencies cap e (commonly in the 0.04 to 0.12 range, set by climate and setting) to keep that safe for slow traffic and in icy weather.
""",
            "widget": BANK,
            "config": {"values": {"V": 40, "R": 2000, "e": 0.12}},
        },
        {
            "kind": "text",
            "title": "Common mistakes, and exam day",
            "body": """
* **V in ft/s.** The 15 assumes mi/h.
* **Missing parentheses.** The 15 multiplies (e + f).
* **e in percent.** Use 0.06, not 6.
* **Adding f** when solving for e. Friction is subtracted.
* **Using one f for every speed.** The design f falls as speed rises.

The design side friction factors and minimum radius tables are in the Green Book, Chapter 3, under horizontal alignment; search **side friction** or **minimum radius**. The point-mass equation itself is in the NCEES Handbook's transportation chapter.
""",
        },
    ],
}
