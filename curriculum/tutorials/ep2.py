"""EP2 Flexible pavement structural number.

Every number below was checked in Python. SN = a₁D₁ + a₂D₂m₂ + a₃D₃m₃ with
thicknesses in inches, as in curriculum/solvers.py. Layer coefficients and
required SNs are given in each problem; none are looked up here.
"""

SECTION = "pavement-section"

TUTORIAL = {
    "minutes": 25,
    "blocks": [
        {
            "kind": "text",
            "title": "What the structural number measures",
            "body": """
A flexible pavement is a stack of layers: an **asphalt** surface, a granular **base**, often a **subbase**, all on the natural **subgrade**. Traffic loads spread out as they pass down through the layers, so the subgrade feels a gentler load than the tire puts on the surface.

The **structural number (SN)** expresses how much load-spreading strength the layers provide. It is an index, not a thickness. The 1993 AASHTO design method gives a required SN for the traffic and the subgrade, and the designer chooses layers that add up to it:

::

    SN = a₁·D₁ + a₂·D₂·m₂ + a₃·D₃·m₃

* **D** is each layer's thickness, in **inches**.
* **a** is the layer coefficient: how strong one inch of that material is. Asphalt is strongest per inch.
* **m** is the drainage coefficient for the base and subbase. Good drainage gives m above 1, and poor drainage, which leaves the layer wet longer, gives m below 1. The asphalt surface has no m.
""",
        },
        {
            "kind": "explorer",
            "title": "Build a pavement section",
            "widget": SECTION,
            "config": {"values": {"D1": 4, "a1": 0.44, "D2": 10, "a2": 0.14, "m2": 1.0, "D3": 8, "a3": 0.11, "m3": 1.0, "SNreq": 4.0}},
            "body": """
Change the thicknesses and coefficients and watch each layer's share of SN in the bar at the bottom. Try lowering the base drainage coefficient from 1.0 to 0.8: the same 10 inches of base suddenly counts for less.
""",
        },
        {
            "kind": "check",
            "title": "Predict the drainage effect",
            "prompt": "In a section with 10 in of base (a₂ = 0.14), the base drainage improves from m₂ = **0.8** to m₂ = **1.2**. By how much does SN increase?",
            "answer": 0.56,
            "tolerance": 0.005,
            "unit": "",
            "hint": "Only the base term changes: a₂ × D₂ × (new m₂ − old m₂).",
            "explanation": """
::

    base term at m₂ = 0.8:  0.14 × 10 × 0.8 = 1.12
    base term at m₂ = 1.2:  0.14 × 10 × 1.2 = 1.68
    increase = 1.68 − 1.12 = 0.56

That is as much as adding 1.3 in of asphalt (0.56 / 0.44). Drainage is cheap structure: a well-drained base does more work.
""",
            "widget": SECTION,
            "config": {"values": {"D1": 4, "a1": 0.44, "D2": 10, "a2": 0.14, "m2": 1.2, "D3": 8, "a3": 0.11, "m3": 1.0, "SNreq": 4.0}},
        },
        {
            "kind": "example",
            "title": "Structural number of a section (core)",
            "prompt": "A pavement has **4 in** of asphalt (a₁ = 0.44), **10 in** of granular base (a₂ = 0.14, m₂ = 1.0) and **8 in** of subbase (a₃ = 0.11, m₃ = 1.0). Find its structural number.",
            "steps": [
                {"think": "Which term has no drainage coefficient?", "text": "Asphalt: a₁D₁ = 0.44 × 4 = **1.76**."},
                {"text": "Base: a₂D₂m₂ = 0.14 × 10 × 1.0 = **1.40**."},
                {"text": "Subbase: a₃D₃m₃ = 0.11 × 8 × 1.0 = **0.88**."},
                {"text": "SN = 1.76 + 1.40 + 0.88 = **4.04**."},
            ],
            "explanation": "The asphalt is the thinnest layer, yet it contributes the most, because its coefficient is about three times the base's. One inch of asphalt here is worth 0.44 / 0.14 ≈ 3.1 in of base.",
            "widget": SECTION,
            "config": {"values": {"D1": 4, "a1": 0.44, "D2": 10, "a2": 0.14, "m2": 1.0, "D3": 8, "a3": 0.11, "m3": 1.0, "SNreq": 4.0}},
        },
        {
            "kind": "check",
            "title": "Your turn",
            "prompt": "A section has **5 in** of asphalt (a₁ = 0.42), **8 in** of base (a₂ = 0.14, m₂ = 1.1) and **10 in** of subbase (a₃ = 0.10, m₃ = 0.9). What is its SN?",
            "answer": 4.23,
            "tolerance": 0.006,
            "unit": "",
            "hint": "Three terms. Only the base and subbase take their m.",
            "explanation": """
::

    asphalt:  0.42 × 5         = 2.100
    base:     0.14 × 8 × 1.1   = 1.232
    subbase:  0.10 × 10 × 0.9  = 0.900
    SN = 4.232 ≈ 4.23
""",
            "widget": SECTION,
            "config": {"values": {"D1": 5, "a1": 0.42, "D2": 8, "a2": 0.14, "m2": 1.1, "D3": 10, "a3": 0.10, "m3": 0.9, "SNreq": 4.2}},
        },
        {
            "kind": "check",
            "title": "Spot the slip",
            "prompt": "For the core example (true SN = 4.04), a student reports **SN = 0.34**. What went wrong?",
            "choices": [
                {"label": "Thicknesses were entered in feet", "correct": True, "why": "4.04 / 12 = 0.34. The layer coefficients are per inch, so thicknesses must be in inches."},
                {"label": "The drainage coefficients were left out", "correct": False, "why": "With m = 1.0 here, leaving them out changes nothing: SN would still be 4.04."},
                {"label": "A drainage coefficient was applied to the asphalt", "correct": False, "why": "With m = 1.0 that also changes nothing. With other m values it would shift SN slightly, not divide it by 12."},
                {"label": "The layers were added in the wrong order", "correct": False, "why": "Addition doesn't depend on order: the sum is 4.04 either way."},
            ],
            "hint": "What is 4.04 divided by 0.34?",
            "explanation": """
A ratio of 12 between the true and reported answer almost always means feet versus inches. Write the units next to every D on your scratch sheet.
""",
        },
        {
            "kind": "text",
            "title": "Designing a layer: solve for a thickness",
            "body": """
Design runs the equation backward. Given the required SN and the other layers, solve for the unknown thickness:

::

    D₂ = (SN_required − a₁D₁ − a₃D₃m₃) / (a₂·m₂)

Then **round up** to a buildable thickness, often the next half inch or inch. Rounding down leaves the pavement short of the required SN.
""",
        },
        {
            "kind": "example",
            "title": "Base thickness for a required SN (standard)",
            "prompt": "A design requires **SN = 4.5**. The section will have **4 in** of asphalt (a₁ = 0.44) and **8 in** of subbase (a₃ = 0.11, m₃ = 1.0). The base has a₂ = 0.14 and m₂ = 1.0. What base thickness is needed, rounded up to the next half inch?",
            "steps": [
                {"think": "How much SN do the asphalt and subbase supply?", "text": "0.44 × 4 + 0.11 × 8 × 1.0 = 1.76 + 0.88 = **2.64**."},
                {"text": "The base must supply 4.5 − 2.64 = **1.86**."},
                {"think": "Divide by what?", "text": "D₂ = 1.86 / (0.14 × 1.0) = **13.29 in**."},
                {"text": "Round up: **13.5 in**. Check: 1.76 + 0.14 × 13.5 + 0.88 = 4.53 ≥ 4.5."},
            ],
            "explanation": "Dividing by a₂ alone (forgetting m₂) only works here because m₂ = 1.0. With m₂ = 0.8 the base would need 16.6 in. Always divide by the product a₂·m₂.",
            "widget": SECTION,
            "config": {"values": {"D1": 4, "a1": 0.44, "D2": 13.5, "a2": 0.14, "m2": 1.0, "D3": 8, "a3": 0.11, "m3": 1.0, "SNreq": 4.5}},
        },
        {
            "kind": "check",
            "title": "Round which way?",
            "prompt": "A computed base thickness is **9.2 in**, and the agency builds in half-inch steps. What do you specify?",
            "choices": [
                {"label": "9.5 in", "correct": True, "why": "Round up to the next buildable step, so the section still meets the required SN."},
                {"label": "9.0 in", "correct": False, "why": "Rounding down leaves the base, and so the pavement, below the required SN."},
                {"label": "9.2 in", "correct": False, "why": "Not a buildable thickness in half-inch steps."},
                {"label": "10.0 in", "correct": False, "why": "Safe, but more than needed. The next half-inch step, 9.5 in, already meets the requirement."},
            ],
            "hint": "Which choice still meets the required SN with the least material?",
            "explanation": "Design thicknesses are minimums. Round up to the next practical increment, then recheck that the total SN still meets the requirement.",
        },
        {
            "kind": "text",
            "title": "Layered design: protect each layer",
            "body": """
The 1993 AASHTO method also checks that each layer is thick enough to protect the layer below. The design gives a required SN measured **over** each layer: SN₁ over the base, SN₂ over the subbase, and SN₃ over the subgrade. Work from the top down:

1. D₁ ≥ SN₁ / a₁. Round up, then compute the asphalt's actual contribution SN₁* = a₁D₁.
2. D₂ ≥ (SN₂ − SN₁*) / (a₂m₂). Round up, then compute SN₂* = a₂D₂m₂.
3. D₃ ≥ (SN₃ − SN₁* − SN₂*) / (a₃m₃). Round up.

Using the rounded, actual contributions at each step stops rounding errors from piling up.
""",
        },
        {
            "kind": "example",
            "title": "Three-layer design from the top down (stretch)",
            "prompt": "The required structural numbers are **SN₁ = 2.6** over the base, **SN₂ = 3.8** over the subbase and **SN₃ = 4.9** over the subgrade. Use a₁ = 0.44, a₂ = 0.14 (m₂ = 1.0) and a₃ = 0.11 (m₃ = 1.0). Round each thickness up to the next half inch.",
            "steps": [
                {"think": "Asphalt first: what thickness covers SN₁?", "text": "D₁ = 2.6 / 0.44 = 5.91 → **6.0 in**. Actual SN₁* = 0.44 × 6.0 = **2.64**."},
                {"think": "What must the base add to reach SN₂?", "text": "D₂ = (3.8 − 2.64) / (0.14 × 1.0) = 8.29 → **8.5 in**. Actual SN₂* = 0.14 × 8.5 = **1.19**."},
                {"think": "What must the subbase add to reach SN₃?", "text": "D₃ = (4.9 − 2.64 − 1.19) / (0.11 × 1.0) = 9.73 → **10.0 in**. Actual SN₃* = 0.11 × 10 = **1.10**."},
                {"text": "Total SN = 2.64 + 1.19 + 1.10 = **4.93 ≥ 4.9**. Section: 6.0 in asphalt, 8.5 in base, 10.0 in subbase."},
            ],
            "explanation": "Each step uses the *rounded* thickness above it. Had you used the unrounded 5.91 in of asphalt, the base and subbase would come out slightly thicker than needed, or thinner if you rounded down.",
            "widget": SECTION,
            "config": {"values": {"D1": 6, "a1": 0.44, "D2": 8.5, "a2": 0.14, "m2": 1.0, "D3": 10, "a3": 0.11, "m3": 1.0, "SNreq": 4.9}},
        },
        {
            "kind": "check",
            "title": "Last check: the base step",
            "prompt": "In that layered design, suppose the base drains poorly and **m₂ = 0.8**. With D₁ = 6.0 in (SN₁* = 2.64) and SN₂ = 3.8, what base thickness does the formula give before rounding, in inches?",
            "answer": 10.36,
            "tolerance": 0.01,
            "unit": "in",
            "hint": "D₂ = (SN₂ − SN₁*) / (a₂·m₂).",
            "explanation": """
::

    D₂ = (3.8 − 2.64) / (0.14 × 0.8) = 1.16 / 0.112 = 10.36 in → 10.5 in

Poor drainage added about 2 in of base (8.5 in → 10.5 in) for the same protection.
""",
            "widget": SECTION,
            "config": {"values": {"D1": 6, "a1": 0.44, "D2": 10.5, "a2": 0.14, "m2": 0.8, "D3": 10, "a3": 0.11, "m3": 1.0, "SNreq": 4.9}},
        },
        {
            "kind": "text",
            "title": "Common mistakes",
            "body": """
* Thicknesses in **feet** instead of inches (answer 12 times too small).
* Applying a **drainage coefficient to the asphalt**.
* Dividing by **a₂ alone** instead of a₂·m₂ when solving for a thickness.
* **Rounding down** a design thickness.
* Treating SN as a thickness. It is a strength index with no units.
""",
        },
        {
            "kind": "text",
            "title": "On exam day",
            "body": """
The flexible design procedure, with layer and drainage coefficients, is in the AASHTO 1993 Guide, Part II. The NCEES Handbook's transportation chapter has the SN equation. Search **structural number**, **layer coefficient** or **drainage coefficient**.

Problems usually give the coefficients. If one gives a required SN for each layer, work from the top down and carry the rounded thicknesses forward.
""",
        },
    ],
}
