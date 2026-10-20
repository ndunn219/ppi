"""EP1 Earthwork quantities.

Every number below was checked in Python. Conventions match
curriculum/solvers.py: compacted = bank × (1 − shrinkage); bank needed for
a compacted volume = compacted / (1 − shrinkage); loose = bank × (1 + swell).
"""

AREAS = "end-areas"
BALANCE = "borrow-balance"

TUTORIAL = {
    "minutes": 25,
    "blocks": [
        {
            "kind": "text",
            "title": "From cross-sections to cubic yards",
            "body": """
A road design gives a **cross-section** at each station: the shape of the cut (earth removed) or fill (earth added) across the road. Its **end area** A is in square feet.

Between two stations the earth forms a solid. The **average end area** method treats it as a prism with the mean of the two areas:

::

    V = L × (A₁ + A₂) / 2        (ft³)
    V / 27                        (yd³)

L is the distance between the stations, often 100 ft or 50 ft. Earthwork is bought and sold in **cubic yards**, so divide by 27 (3 ft × 3 ft × 3 ft).
""",
        },
        {
            "kind": "explorer",
            "title": "Two sections and the earth between them",
            "widget": AREAS,
            "config": {"values": {"A1": 300, "A2": 500, "L": 100}},
            "body": """
Change the two areas and the spacing. Notice that the volume depends only on their **average**, not on which end is bigger. Then set one area to zero, as at the point where a cut runs out, and compare with the pyramid volume.
""",
        },
        {
            "kind": "check",
            "title": "Your first volume",
            "prompt": "Cut sections **50 ft** apart have end areas of **240 ft²** and **360 ft²**. What is the volume of cut between them, in cubic yards?",
            "answer": 555.6,
            "tolerance": 0.2,
            "unit": "yd³",
            "hint": "Average the areas, multiply by the distance, then divide by 27.",
            "explanation": """
::

    V = 50 × (240 + 360) / 2 = 50 × 300 = 15,000 ft³
    15,000 / 27 = 555.6 yd³

Notice the units: square feet times feet gives cubic feet, and 27 cubic feet make a cubic yard.
""",
            "widget": AREAS,
            "config": {"values": {"A1": 240, "A2": 360, "L": 50}},
        },
        {
            "kind": "example",
            "title": "Volume by average end area (core)",
            "prompt": "Cut cross-sections at stations 20+00 and 21+00 have end areas of **300 ft²** and **500 ft²**. Find the volume of cut.",
            "steps": [
                {"think": "What is L?", "text": "21+00 − 20+00 = **100 ft**."},
                {"text": "Average area = (300 + 500) / 2 = **400 ft²**."},
                {"text": "V = 100 × 400 = **40,000 ft³**."},
                {"think": "What unit does the answer need?", "text": "40,000 / 27 = **1,481.5 yd³**."},
            ],
            "explanation": "On the exam, check the answer's units before you choose. Both 40,000 (cubic feet) and 1,481 (cubic yards) are likely to appear as choices.",
            "widget": AREAS,
            "config": {"values": {"A1": 300, "A2": 500, "L": 100}},
        },
        {
            "kind": "check",
            "title": "Spot the slip",
            "prompt": "For the 300 ft² and 500 ft² sections 100 ft apart, a student reports **2,963 yd³**. Which mistake gives that number?",
            "choices": [
                {"label": "Forgot to divide the sum of the areas by 2", "correct": True, "why": "100 × (300 + 500) / 27 = 2,963 yd³, exactly twice the right answer of 1,481.5."},
                {"label": "Forgot to divide by 27", "correct": False, "why": "That gives 40,000, a cubic-foot answer, not 2,963."},
                {"label": "Divided by 9 instead of 27", "correct": False, "why": "40,000 / 9 = 4,444. Nine converts square feet to square yards, not volumes."},
                {"label": "Used only the larger area", "correct": False, "why": "100 × 500 / 27 = 1,852 yd³."},
            ],
            "hint": "The right answer is 1,481.5 yd³. What is 2,963 compared with it?",
            "explanation": """
Each slip leaves its own number. The correct answer is **1,481.5 yd³**, and:

* No ÷ 2: **2,963 yd³** (double).
* No ÷ 27: **40,000** (cubic feet).
* ÷ 9 instead of ÷ 27: **4,444**.
* Larger area only: **1,852 yd³**.
""",
            "widget": AREAS,
            "config": {"values": {"A1": 300, "A2": 500, "L": 100}},
        },
        {
            "kind": "text",
            "title": "Several stations, and where a cut runs out",
            "body": """
For a run of stations, compute each segment and add them. Keep cut and fill separate: they are different materials headed in different directions.

Where a cut runs out (the end area goes to zero), the solid between the sections is closer to a **pyramid** or wedge than a prism. Average end area then **overestimates**: a pyramid's volume is A·L/3, not A·L/2. Average end area is the usual method unless a question asks for the prismoidal formula or a pyramid correction, but knowing it overestimates helps you judge answer choices.
""",
        },
        {
            "kind": "example",
            "title": "A run of three stations (standard)",
            "prompt": "Cut end areas are **0 ft²** at 10+00, **180 ft²** at 11+00 and **260 ft²** at 12+00. Find the total cut by average end area, then compare the first segment with a pyramid.",
            "steps": [
                {"think": "Volume from 10+00 to 11+00?", "text": "100 × (0 + 180) / 2 = 9,000 ft³ = **333.3 yd³**."},
                {"text": "From 11+00 to 12+00: 100 × (180 + 260) / 2 = 22,000 ft³ = **814.8 yd³**."},
                {"text": "Total = 333.3 + 814.8 = **1,148.1 yd³**."},
                {"think": "If the first segment is really a pyramid, what is its volume?", "text": "180 × 100 / 3 = 6,000 ft³ = **222.2 yd³**, about a third less than average end area's 333.3."},
            ],
            "explanation": "Unless a question tells you to correct for it, the average end area total (1,148 yd³) is the expected answer. The pyramid comparison shows why it is a conservative estimate where sections taper to zero.",
            "widget": AREAS,
            "config": {"values": {"A1": 0, "A2": 180, "L": 100}},
        },
        {
            "kind": "text",
            "title": "Bank, loose and compacted",
            "body": """
The same soil takes up different space depending on its state:

* **Bank**: in the ground before digging. Cut is measured this way.
* **Loose**: dug and in a truck. It fluffs up, by the **swell**: loose = bank × (1 + swell).
* **Compacted**: placed and rolled in a fill. It ends up denser than the bank, by the **shrinkage**: compacted = bank × (1 − shrinkage).

So 1,000 bank yd³ with 25% swell fills trucks with 1,250 yd³, and with 15% shrinkage it makes 850 yd³ of compacted fill. Hauling is priced on loose volume, excavation and borrow on bank, and fill on compacted.
""",
        },
        {
            "kind": "check",
            "title": "How much fill does a cut make?",
            "prompt": "A cut yields **10,000 bank yd³** of suitable soil. The shrinkage factor is **15%**. How many compacted cubic yards of fill can it build?",
            "answer": 8500,
            "tolerance": 1,
            "unit": "yd³",
            "hint": "Compacted = bank × (1 − shrinkage).",
            "explanation": """
::

    10,000 × (1 − 0.15) = 8,500 compacted yd³

The cut shrinks when compacted, so it builds *less* fill than its bank volume. A common slip is multiplying by 1.15, which treats shrinkage as swell.
""",
            "widget": BALANCE,
            "config": {"values": {"Vc": 10000, "Vf": 8500, "s": 15, "w": 25}},
        },
        {
            "kind": "check",
            "title": "Trucks, not yards",
            "prompt": "The same **10,000 bank yd³** swells **25%** when dug. How many loads does it take in 12 yd³ trucks?",
            "answer": 1042,
            "tolerance": 0.4,
            "unit": "loads",
            "hint": "Trucks carry loose soil. Find the loose volume first, then round the loads up.",
            "explanation": """
::

    loose = 10,000 × 1.25 = 12,500 yd³
    loads = 12,500 / 12 = 1,041.7 → 1,042 loads

Round up: a partial load is still a trip. Using bank volume (834 loads) underestimates hauling by a fifth.
""",
        },
        {
            "kind": "explorer",
            "title": "Balance cut against fill",
            "widget": BALANCE,
            "config": {"values": {"Vc": 20000, "Vf": 30000, "s": 20, "w": 25}},
            "body": """
Set the usable cut, the fill needed and the factors. Watch the shortfall turn into **borrow**, and see why the borrow bar is longer than the shortfall bar. Push the cut up until it covers the fill, and the shortfall becomes **waste**.
""",
        },
        {
            "kind": "example",
            "title": "Borrow with shrinkage and swell (stretch)",
            "prompt": "A project needs **30,000 compacted yd³** of fill. The cut yields **20,000 bank yd³** of suitable material. Shrinkage is **20%** and swell is **25%**. How many bank yd³ of borrow are needed, and how many 14-yd³ truckloads will haul it?",
            "steps": [
                {"think": "How much fill does the cut make?", "text": "20,000 × (1 − 0.20) = **16,000 compacted yd³**."},
                {"text": "Compacted shortfall = 30,000 − 16,000 = **14,000 yd³**."},
                {"think": "The borrow pit soil shrinks too. How much bank volume makes 14,000 compacted?", "text": "14,000 / (1 − 0.20) = **17,500 bank yd³** of borrow."},
                {"text": "Loose for hauling: 17,500 × 1.25 = **21,875 yd³**. Loads: 21,875 / 14 = 1,562.5 → **1,563 loads**."},
            ],
            "explanation": "The three answers a question might want here are 14,000 (compacted shortfall), 17,500 (bank borrow) and 21,875 (loose haul). Read which state the question asks for: that choice is the whole problem.",
            "widget": BALANCE,
            "config": {"values": {"Vc": 20000, "Vf": 30000, "s": 20, "w": 25}},
        },
        {
            "kind": "check",
            "title": "Which state?",
            "prompt": "In the last example, a contractor bids borrow excavation per **bank** cubic yard. Which quantity goes on the bid?",
            "choices": [
                {"label": "17,500 yd³", "correct": True, "why": "Borrow excavation is measured in the pit, as bank volume: the 14,000 compacted shortfall divided by 0.80."},
                {"label": "14,000 yd³", "correct": False, "why": "That is the compacted shortfall. Digging only 14,000 bank yd³ would leave the fill 2,800 compacted yd³ short."},
                {"label": "21,875 yd³", "correct": False, "why": "That is the loose volume in the trucks, used for hauling, not for bank excavation."},
                {"label": "10,000 yd³", "correct": False, "why": "That is the difference between the fill and the bank cut (30,000 − 20,000), which ignores shrinkage entirely."},
            ],
            "hint": "Bank means in the ground, before digging.",
            "explanation": """
Match each number to its state:

* 16,000 compacted: what the cut builds.
* 14,000 compacted: the shortfall.
* **17,500 bank**: borrow dug from the pit.
* 21,875 loose: what the trucks carry.

Ignoring shrinkage (30,000 − 20,000 = 10,000) is the most common wrong answer.
""",
            "widget": BALANCE,
            "config": {"values": {"Vc": 20000, "Vf": 30000, "s": 20, "w": 25}},
        },
        {
            "kind": "text",
            "title": "Common mistakes",
            "body": """
* Leaving the answer in **cubic feet**, or dividing by 9.
* Forgetting to **average** the two end areas.
* Adding **cut and fill** together in one total.
* Treating **shrinkage as swell**: multiplying by (1 + s) instead of (1 − s).
* Reporting the compacted shortfall when the question asks for **bank** borrow.
* Rounding truckloads **down**.
""",
        },
        {
            "kind": "text",
            "title": "On exam day",
            "body": """
The earthwork formulas, including average end area and the prismoidal formula, are in the NCEES Handbook. Search **average end area** or **prismoidal**.

Before you calculate, write the three states on your scratch sheet (bank, loose, compacted) and label every number with its state as you go.
""",
        },
    ],
}
