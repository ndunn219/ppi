"""TE1 Traffic flow and peak hour factor.

Every number below was worked by hand and checked in Python. Greenshields
is used as the classic teaching model of the speed-density relationship.
"""

FLOW = "flow-density"
PHF = "phf-counts"

TUTORIAL = {
    "minutes": 30,
    "blocks": [
        {
            "kind": "text",
            "title": "Three numbers describe a traffic stream",
            "body": """
Stand beside a freeway lane and you can measure three things:

* **Flow q**: vehicles passing a point per hour (veh/h, or veh/h/ln per lane).
* **Density k**: vehicles on a length of road at one instant (veh/mi, or veh/mi/ln).
* **Speed v**: the space mean speed of those vehicles (mi/h).

They are tied together by one identity:

::

    q = k × v
    veh/h = veh/mi × mi/h

This holds for any traffic stream, by definition. The units do the work: miles cancel, leaving vehicles per hour. That is why speed stays in mi/h here. Converting it to ft/s would mix feet and miles.
""",
        },
        {
            "kind": "check",
            "title": "Use the identity",
            "prompt": "A lane carries a density of **40 veh/mi/ln** at a space mean speed of **50 mi/h**. What is the flow in that lane, in veh/h/ln?",
            "answer": 2000.0,
            "tolerance": 0.5,
            "unit": "veh/h/ln",
            "hint": "q = k × v. No unit conversion is needed: veh/mi × mi/h = veh/h.",
            "explanation": """
::

    q = k × v = 40 veh/mi × 50 mi/h = 2,000 veh/h/ln

That is a busy lane, near the upper range of what freeways carry. Use the explorer below to see where this point sits relative to capacity.
""",
            "widget": FLOW,
            "config": {"values": {"vf": 60, "kj": 200, "k": 40}},
        },
        {
            "kind": "text",
            "title": "Speed falls as density rises",
            "body": """
With few vehicles, drivers travel at the **free-flow speed v_f**. As density rises they slow down, until at the **jam density k_j** traffic stops. The classic Greenshields model assumes speed falls in a straight line:

::

    v = v_f × (1 − k / k_j)

Multiply by k and flow becomes a parabola in density:

::

    q = v_f × k × (1 − k / k_j)

Flow is zero at both ends: no vehicles, or vehicles that can't move. In between it peaks at **capacity**. Greenshields is a simplification, and real speed-density data curve, but it captures the shape and is the model exam questions use.
""",
        },
        {
            "kind": "explorer",
            "title": "Flow, density and speed together",
            "widget": FLOW,
            "body": """
Slide the density from zero to jam density. Watch the flow rise, peak and fall. The **slope of the dashed line** from the origin to your point is the speed, because v = q / k. Then change free-flow speed and jam density and see how capacity moves.
""",
        },
        {
            "kind": "check",
            "title": "Predict before you slide",
            "prompt": "With v_f = 60 mi/h and k_j = 200 veh/mi/ln, at what density is flow highest? Decide first, then check it in the explorer.",
            "choices": [
                {"label": "100 veh/mi/ln, half of jam density", "correct": True, "why": "The parabola q = v_f k (1 − k/k_j) is symmetric, so its peak is at k_j / 2."},
                {"label": "200 veh/mi/ln, at jam density", "correct": False, "why": "At jam density traffic is stopped, so flow is zero, not a maximum."},
                {"label": "As low as possible, where speed is highest", "correct": False, "why": "At very low density speed is high but there are hardly any vehicles, so flow is small."},
                {"label": "60 veh/mi/ln, matching the free-flow speed", "correct": False, "why": "Free-flow speed has no direct link to the density at capacity; the peak depends only on jam density."},
            ],
            "explanation": """
Set dq/dk = 0:

::

    q = v_f·k − (v_f / k_j)·k²
    dq/dk = v_f − 2(v_f / k_j)·k = 0  →  k = k_j / 2

At that density the speed is v_f / 2, and capacity is:

::

    q_max = v_f × k_j / 4 = 60 × 200 / 4 = 3,000 veh/h/ln

Three facts to remember at capacity: half of jam density, half of free-flow speed, and q_max = v_f·k_j / 4.
""",
            "widget": FLOW,
            "config": {"values": {"vf": 60, "kj": 200, "k": 100}},
        },
        {
            "kind": "check",
            "title": "Compute a capacity",
            "prompt": "A freeway lane follows Greenshields with free-flow speed **65 mi/h** and jam density **190 veh/mi/ln**. What is its capacity, in veh/h/ln?",
            "answer": 3087.5,
            "tolerance": 0.6,
            "unit": "veh/h/ln",
            "hint": "q_max = v_f × k_j / 4.",
            "explanation": """
::

    q_max = 65 × 190 / 4 = 12,350 / 4 = 3,087.5 veh/h/ln

It occurs at k = 190 / 2 = 95 veh/mi/ln and v = 65 / 2 = 32.5 mi/h.
""",
            "widget": FLOW,
            "config": {"values": {"vf": 65, "kj": 190, "k": 95}},
        },
        {
            "kind": "check",
            "title": "Same flow, two very different roads",
            "prompt": "With v_f = 60 mi/h and k_j = 200 veh/mi/ln, two detectors both report **2,000 veh/h/ln**. One reads 42 veh/mi/ln and the other 158 veh/mi/ln. Which statement is true?",
            "choices": [
                {"label": "The 158 veh/mi/ln lane is congested and moving at about 13 mi/h", "correct": True, "why": "Above k_j/2 = 100 you are on the congested side. v = 60(1 − 158/200) ≈ 12.7 mi/h."},
                {"label": "Both lanes are operating the same way, since flow is the same", "correct": False, "why": "Flow alone doesn't tell you the state: one lane moves at about 47 mi/h and the other at about 13 mi/h."},
                {"label": "The 42 veh/mi/ln lane is congested", "correct": False, "why": "42 is below k_j/2 = 100, so it is on the uncongested side, moving at about 47 mi/h."},
                {"label": "Neither, because 2,000 veh/h/ln is above capacity", "correct": False, "why": "Capacity here is 60 × 200 / 4 = 3,000 veh/h/ln, so 2,000 is below it."},
            ],
            "explanation": """
Every flow below capacity happens at **two** densities, one on each side of the peak. Solve q = 2,000:

::

    60k(1 − k/200) = 2,000  →  0.3k² − 60k + 2,000 = 0
    k = 42.3 or 157.7 veh/mi/ln
    v = 47.3 mi/h or 12.7 mi/h

That is why traffic engineers describe operations by density or speed, not by flow alone.
""",
            "widget": FLOW,
            "config": {"values": {"vf": 60, "kj": 200, "k": 158}},
        },
        {
            "kind": "example",
            "title": "Total flow on a multilane freeway (core)",
            "prompt": "A three-lane freeway direction has a density of **35 veh/mi/ln** and a space mean speed of **55 mi/h**. What is the total flow in that direction?",
            "steps": [
                {"think": "Is the density per lane or for all lanes?", "text": "Per lane (veh/mi/ln). So compute the per-lane flow first."},
                {"text": "q per lane = 35 × 55 = **1,925 veh/h/ln**."},
                {"think": "How do you get the direction total?", "text": "Multiply by the number of lanes: 1,925 × 3 = **5,775 veh/h**."},
            ],
            "explanation": "The most common slip is stopping at the per-lane flow. Read the question's units: veh/h for the direction, veh/h/ln for one lane.",
        },
        {
            "kind": "text",
            "title": "The peak hour factor",
            "body": """
Traffic isn't uniform within an hour. A road can carry 1,800 vehicles in an hour but 510 of them in the busiest 15 minutes, a rate of 2,040 veh/h. Capacity analysis designs for that **peak rate**, not the hourly average.

The **peak hour factor** measures how peaked the hour is:

::

    PHF = V / (4 × V15)
    V   = hourly volume
    V15 = volume in the busiest 15 minutes

Then the peak flow rate used in analysis is:

::

    v = V / PHF

A PHF is never greater than 1.0. A value of 1.0 means a perfectly even hour. Lower values, like 0.80, mean a sharp peak.
""",
        },
        {
            "kind": "explorer",
            "title": "Shape the peak hour",
            "widget": PHF,
            "body": """
Change the four counts. Make them all equal and PHF becomes 1.00. Make one period much busier than the others and watch PHF fall while the peak flow rate rises above the hourly volume.
""",
        },
        {
            "kind": "check",
            "title": "PHF from counts",
            "prompt": "The four 15-minute counts in the peak hour are **420, 510, 480 and 390** vehicles. What is the peak hour factor? Give two decimal places.",
            "answer": 0.88,
            "tolerance": 0.005,
            "hint": "Add the counts for V. The busiest count is V15. Then PHF = V / (4 × V15).",
            "explanation": """
::

    V   = 420 + 510 + 480 + 390 = 1,800 veh
    V15 = 510 veh
    PHF = 1,800 / (4 × 510) = 1,800 / 2,040 = 0.88

The peak flow rate is V / PHF = 4 × 510 = **2,040 veh/h**, about 13% above the hourly volume.
""",
            "widget": PHF,
            "config": {"values": {"c1": 420, "c2": 510, "c3": 480, "c4": 390}},
        },
        {
            "kind": "check",
            "title": "Spot the slip",
            "prompt": "For the same counts, a student reports **PHF = 1.13**. What went wrong?",
            "choices": [
                {"label": "They inverted the ratio, computing (4 × V15) / V", "correct": True, "why": "2,040 / 1,800 = 1.13. A PHF can never exceed 1.0, which is the quick check that catches this."},
                {"label": "They used the average count instead of the peak", "correct": False, "why": "Using the average (450) gives 1,800 / 1,800 = 1.00, not 1.13."},
                {"label": "They forgot the factor of 4", "correct": False, "why": "1,800 / 510 = 3.53, not 1.13."},
                {"label": "They added the counts wrong", "correct": False, "why": "The arithmetic of the sum isn't the issue; 1.13 is exactly the inverted ratio."},
            ],
            "explanation": """
Sanity checks for any PHF answer:

* It must be between 0.25 and 1.00. It equals 0.25 only if all the hour's traffic arrives in one 15-minute period.
* The peak flow rate V / PHF must be **at least** the hourly volume.

If your PHF is above 1, flip it. If your peak rate is below V, you multiplied by PHF instead of dividing.
""",
        },
        {
            "kind": "example",
            "title": "Capacity from a speed-density model (standard)",
            "prompt": "Field data fit Greenshields with v_f = **65 mi/h** and k_j = **190 veh/mi/ln**. Find the capacity per lane and the speed and density at which it occurs.",
            "steps": [
                {"think": "Where does a Greenshields parabola peak?", "text": "At half of jam density: k_c = 190 / 2 = **95 veh/mi/ln**."},
                {"text": "Speed there is half of free-flow speed: v_c = 65 / 2 = **32.5 mi/h**."},
                {"text": "Capacity = k_c × v_c = 95 × 32.5 = **3,087.5 veh/h/ln**. Check: v_f k_j / 4 = 65 × 190 / 4 = 3,087.5."},
            ],
            "explanation": "Two routes to the same answer: the identity q = kv at the peak, or the shortcut v_f k_j / 4. Doing both takes seconds and confirms the result.",
            "widget": FLOW,
            "config": {"values": {"vf": 65, "kj": 190, "k": 95}},
        },
        {
            "kind": "example",
            "title": "From an hourly count to operating conditions (stretch)",
            "prompt": "A two-lane freeway direction carries **3,600 veh** in the peak hour with **PHF = 0.90**. The lanes follow Greenshields with v_f = 60 mi/h and k_j = 200 veh/mi/ln. Find the peak flow rate per lane, its ratio to capacity, and the density and speed of the uncongested traffic.",
            "steps": [
                {"think": "Which flow do you analyze, the hourly volume or the peak rate?", "text": "The peak rate: v = V / PHF = 3,600 / 0.90 = **4,000 veh/h**, or **2,000 veh/h/ln** over two lanes."},
                {"text": "Capacity = 60 × 200 / 4 = 3,000 veh/h/ln, so the volume to capacity ratio is 2,000 / 3,000 = **0.67**."},
                {"think": "Set up q = 2,000 in the Greenshields equation.", "text": "60k(1 − k/200) = 2,000 gives 0.3k² − 60k + 2,000 = 0, so k = 42.3 or 157.7 veh/mi/ln."},
                {"text": "Uncongested traffic is the lower root: **k = 42.3 veh/mi/ln**, and v = 60(1 − 42.3/200) = **47.3 mi/h**."},
            ],
            "explanation": "The quadratic always has two roots below capacity. Pick the one the question describes: free-moving traffic is the lower density, a queue is the higher one.",
            "widget": FLOW,
            "config": {"values": {"vf": 60, "kj": 200, "k": 42}},
        },
        {
            "kind": "text",
            "title": "Common mistakes",
            "body": """
* **Converting mi/h to ft/s** in q = kv. Density is per mile, so speed stays in mi/h.
* **Stopping at per-lane flow** when the question asks for the direction, or the reverse.
* **Inverting PHF.** It is never above 1.0.
* **Multiplying by PHF** to get the peak rate. Divide: the peak rate is higher than the hourly volume.
* **Picking the wrong root** of the Greenshields quadratic. Decide first whether the traffic is moving freely or queued.
""",
        },
        {
            "kind": "text",
            "title": "On exam day",
            "body": """
The flow-density-speed relationships are in the NCEES Handbook's transportation chapter. Search **density** or **space mean speed**. PHF and peak flow rates appear throughout the HCM's freeway and highway chapters.

Before computing, write down the units of every number in the question. Most traffic flow mistakes are unit mistakes.
""",
        },
    ],
}
