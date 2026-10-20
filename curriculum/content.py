"""Seed content for the PE Civil: Transportation proof of concept.

`python manage.py seed_course` loads this into the database. Area weights
are placeholders, and reference locators are written from general
knowledge of each document's organization: both need checking against
the current NCEES specification and the editions the exam supplies. No
item here has been reviewed by a licensed PE.
"""

MODULE = {
    "slug": "pe-civil-transportation",
    "name": "PE Civil: Transportation",
    "description": "Proof-of-concept course for the PE Civil exam, Transportation depth module.",
}

REFERENCES = [
    {
        "short_name": "NCEES Handbook",
        "title": "NCEES PE Civil Reference Handbook",
        "publisher": "NCEES",
        "is_public_domain": False,
        "notes": "Free to registered examinees through MyNCEES. Students open their own copy.",
    },
    {
        "short_name": "Green Book",
        "title": "A Policy on Geometric Design of Highways and Streets",
        "publisher": "AASHTO",
        "is_public_domain": False,
        "notes": "AASHTO terms bar use of its content with AI tools. Point to locations only.",
    },
    {
        "short_name": "HCM",
        "title": "Highway Capacity Manual",
        "publisher": "Transportation Research Board",
        "is_public_domain": False,
    },
    {
        "short_name": "HSM",
        "title": "Highway Safety Manual",
        "publisher": "AASHTO",
        "is_public_domain": False,
    },
    {
        "short_name": "AASHTO 93",
        "title": "AASHTO Guide for Design of Pavement Structures (1993)",
        "publisher": "AASHTO",
        "is_public_domain": False,
    },
    {
        "short_name": "MUTCD",
        "title": "Manual on Uniform Traffic Control Devices",
        "publisher": "FHWA",
        "is_public_domain": True,
        "url": "https://mutcd.fhwa.dot.gov/",
        "notes": "Public domain. Free to link and use.",
    },
]

# Each area: code, name, weight, items. Each item carries its lesson,
# cards, lookup drills, reference locations and problem templates.
AREAS = [
    {
        "code": "TE",
        "name": "Traffic engineering",
        "weight": "0.250",
        "items": [
            {
                "code": "TE1",
                "name": "Traffic flow and peak hour factor",
                "method_name": "Flow–density–speed relationship and PHF",
                "summary": "Relate flow, density and speed, and convert hourly volumes to peak flow rates.",
                "cues": "density\nveh/mi/ln\nspace mean speed\npeak 15 minutes\npeak hour factor\nflow rate",
                "lesson": {
                    "title": "Flow, density, speed and the peak hour factor",
                    "minutes": 8,
                    "body": """
When it applies
---------------

Any question that gives two of flow, density and speed and asks for the third, or gives an hourly volume and a peak 15-minute count.

The method
----------

The fundamental relationship ties the three together::

    q = k × v
    q = flow (veh/h), k = density (veh/mi), v = space mean speed (mi/h)

Work per lane first, then multiply by the number of lanes. Density is per mile, so speed stays in mi/h.

The peak hour factor (PHF) measures how peaked the hour is::

    PHF = V / (4 × V15)
    v   = V / PHF

V is the hourly volume, V15 the busiest 15-minute volume, and v the peak flow rate used in capacity analysis.

Watch out
---------

* A PHF is never greater than 1.0. If you get 1.2, you inverted it.
* The peak flow rate is always *higher* than the hourly volume.
* Check whether density is per lane or for all lanes.

Where it lives
--------------

The Handbook's transportation chapter has the flow relationships. The HCM uses PHF throughout its freeway and highway chapters.
""",
                },
                "cards": [
                    ("formula", "Flow, density and speed: the relationship", "q = k × v (veh/h = veh/mi × mi/h)"),
                    ("formula", "Peak hour factor", "PHF = V / (4 × V15)"),
                    ("method", "You know the hourly volume and the PHF. What is the peak flow rate?", "v = V / PHF, always higher than V"),
                    ("variables", "In q = k × v, what kind of speed is v?", "Space mean speed, in mi/h"),
                    ("where", "Where do you find the flow–density–speed relationship?", "NCEES Handbook, transportation chapter: traffic flow"),
                ],
                "lookups": [
                    {
                        "prompt": "You need the definition of PHF used in freeway capacity analysis.",
                        "answer": "HCM, freeway and multilane highway chapters",
                        "wrong": ["MUTCD, Part 4", "Green Book, Chapter 3", "HSM, Part C"],
                        "explanation": "PHF is a capacity concept; the HCM applies it to demand volumes.",
                    },
                ],
                "locations": [
                    ("NCEES Handbook", "Transportation chapter: traffic flow", "q = kv and related definitions", "flow, density, space mean speed"),
                    ("HCM", "Freeway and highway capacity chapters", "Peak hour factor and demand flow rate", "peak hour factor, PHF, demand flow rate"),
                ],
                "templates": [
                    {
                        "slug": "flow-rate-from-density",
                        "title": "Flow rate from density and speed",
                        "stem": "A freeway segment with {lanes} lanes in one direction operates at a density of {k} veh/mi/ln and a space mean speed of {v} mi/h. What is the total flow rate in that direction?",
                        "solver": "flow_rate",
                        "params": {"k": [18, 45, 1], "v": [35, 65, 1], "lanes": [2, 4, 1]},
                        "answer_unit": "veh/h",
                        "decimals": 0,
                        "est_minutes": "3",
                        "difficulty": 1,
                        "explain_prompt": "Why does speed stay in mi/h here rather than being converted to ft/s?",
                        "explain_answer": "Density is in vehicles per mile, so mi/h × veh/mi gives veh/h directly. Converting speed would mix feet and miles.",
                    },
                    {
                        "slug": "peak-hour-factor",
                        "title": "Peak hour factor from counts",
                        "stem": "An approach carries {V} veh in the peak hour. The busiest 15-minute count in that hour is {V15} veh. What is the peak hour factor?",
                        "solver": "phf",
                        "params": {"V": [800, 2400, 50], "phf": {"choices": [0.78, 0.82, 0.85, 0.88, 0.91, 0.94]}},
                        "answer_unit": "",
                        "decimals": 2,
                        "est_minutes": "2",
                        "difficulty": 1,
                        "explain_prompt": "Why is the 15-minute count multiplied by 4?",
                        "explain_answer": "Four 15-minute periods make an hour; 4 × V15 is the hourly volume the road would carry if the whole hour were as busy as its peak.",
                    },
                    {
                        "slug": "design-flow-rate",
                        "title": "Peak flow rate from PHF",
                        "stem": "A two-lane highway carries a peak-hour volume of {V} veh/h with a peak hour factor of {phf}. What peak 15-minute flow rate should be used for analysis?",
                        "solver": "design_flow_rate",
                        "params": {"V": [600, 2200, 50], "phf": {"choices": [0.80, 0.84, 0.88, 0.90, 0.92, 0.95]}},
                        "answer_unit": "veh/h",
                        "decimals": 0,
                        "est_minutes": "2",
                        "difficulty": 1,
                    },
                ],
            },
            {
                "code": "TE2",
                "name": "Signal timing",
                "method_name": "Yellow change interval and Webster cycle length",
                "summary": "Size the yellow change interval and estimate an optimum cycle length.",
                "cues": "yellow change interval\nperception-reaction time\ndeceleration rate\noptimum cycle\nlost time\ncritical flow ratio",
                "lesson": {
                    "title": "Yellow intervals and cycle length",
                    "minutes": 10,
                    "body": """
When it applies
---------------

Questions about the yellow (change) interval for an approach, or the cycle length for a pretimed signal given lost time and flow ratios.

Yellow change interval
----------------------

The kinematic formula::

    Y = t + v / (2a + 2Gg)
    t = perception-reaction time (s), usually 1.0
    v = approach speed (ft/s) = 1.47 × mi/h
    a = deceleration rate (ft/s²), usually 10
    G = grade as a decimal (+ upgrade, − downgrade)
    g = 32.2 ft/s²

An upgrade helps the driver stop, so it shortens the interval. A downgrade lengthens it.

Webster's optimum cycle
-----------------------

::

    C0 = (1.5L + 5) / (1 − Y)
    L = total lost time per cycle (s)
    Y = sum of the critical flow ratios (v/s) of each phase

As Y approaches 1, the cycle grows very fast. A Y over about 0.9 means the intersection is near capacity.

Watch out
---------

* Speed must be in ft/s in the yellow formula.
* The grade is a decimal, and its sign matters.
* Webster's denominator is 1 − Y, not Y.

Where it lives
--------------

The Handbook covers both formulas. The MUTCD, Part 4, sets the rules for using yellow and red clearance intervals.
""",
                },
                "cards": [
                    ("formula", "Yellow change interval", "Y = t + v / (2a + 2Gg), v in ft/s, G as a decimal"),
                    ("variables", "Typical t and a in the yellow change formula", "t = 1.0 s, a = 10 ft/s²"),
                    ("formula", "Webster's optimum cycle length", "C0 = (1.5L + 5) / (1 − Y)"),
                    ("method", "Does a downgrade lengthen or shorten the yellow interval?", "Lengthen: gravity reduces the effective deceleration"),
                    ("where", "Where are the rules for applying yellow change and red clearance intervals?", "MUTCD, Part 4 (Highway Traffic Signals)"),
                ],
                "lookups": [
                    {
                        "prompt": "You need the standard for when a red clearance interval may be used.",
                        "answer": "MUTCD, Part 4 (Highway Traffic Signals)",
                        "wrong": ["MUTCD, Part 6", "HCM, signalized intersections", "Green Book, Chapter 9"],
                        "explanation": "Signal display rules, including change and clearance intervals, are in MUTCD Part 4.",
                    },
                    {
                        "prompt": "You need a method for signalized intersection level of service.",
                        "answer": "HCM, signalized intersections chapter",
                        "wrong": ["MUTCD, Part 4", "HSM, Part C", "NCEES Handbook, geotechnical chapter"],
                        "explanation": "Level of service is an HCM measure.",
                    },
                ],
                "locations": [
                    ("NCEES Handbook", "Transportation chapter: traffic signals", "Yellow change interval and cycle length formulas", "yellow change, cycle length, lost time"),
                    ("MUTCD", "Part 4: Highway Traffic Signals", "Signal display and timing standards", "yellow change interval, red clearance"),
                    ("HCM", "Signalized intersections chapter", "Capacity and level of service", "critical flow ratio, lost time"),
                ],
                "templates": [
                    {
                        "slug": "yellow-change-interval",
                        "title": "Yellow change interval on a grade",
                        "stem": "An approach has a speed of {V} mi/h on a {G}% grade. Using a perception-reaction time of 1.0 s and a deceleration rate of 10 ft/s², what yellow change interval is required?",
                        "solver": "yellow_interval",
                        "params": {"V": [30, 55, 5], "G": {"choices": [-4, -3, -2, 2, 3, 4]}},
                        "answer_unit": "s",
                        "decimals": 1,
                        "est_minutes": "3",
                        "difficulty": 2,
                        "explain_prompt": "Why does the grade's sign change the interval?",
                        "explain_answer": "On a downgrade gravity works against braking, so stopping takes longer and the yellow must be longer. On an upgrade it helps braking.",
                    },
                    {
                        "slug": "webster-cycle",
                        "title": "Webster optimum cycle length",
                        "stem": "A three-phase pretimed signal has a total lost time of {L} s per cycle. The critical flow ratios are {y1}, {y2} and {y3}. What is Webster's optimum cycle length?",
                        "solver": "webster_cycle",
                        "params": {
                            "L": [9, 15, 1],
                            "y1": {"choices": [0.18, 0.21, 0.24, 0.27, 0.30]},
                            "y2": {"choices": [0.15, 0.19, 0.22, 0.25]},
                            "y3": {"choices": [0.10, 0.13, 0.16, 0.20]},
                        },
                        "answer_unit": "s",
                        "decimals": 0,
                        "est_minutes": "3",
                        "difficulty": 2,
                    },
                ],
            },
            {
                "code": "TE3",
                "name": "Crash rates",
                "method_name": "Crash rate per million entering vehicles or per 100 MVMT",
                "summary": "Compute crash rates for intersections and roadway segments.",
                "cues": "crashes per year\ncrash rate\nmillion entering vehicles\n100 million vehicle-miles\nADT",
                "lesson": {
                    "title": "Crash rates for intersections and segments",
                    "minutes": 7,
                    "body": """
When it applies
---------------

A question gives a number of crashes over some years and a traffic volume, and asks for a rate.

The method
----------

Intersections use million entering vehicles (MEV)::

    R = C × 10^6 / (365 × N × V)
    C = crashes in the study period, N = years, V = total entering ADT

Segments use 100 million vehicle-miles (100 MVMT)::

    R = C × 10^8 / (365 × N × V × L)
    L = segment length (mi)

Watch out
---------

* Intersections: 10^6, no length. Segments: 10^8, with length.
* V is a daily volume, so 365 converts it to a yearly one.
* For an intersection, V is the sum of all entering approaches.

Where it lives
--------------

The Handbook gives both rate formulas. The HSM covers predictive methods, which go beyond simple rates.
""",
                },
                "cards": [
                    ("formula", "Intersection crash rate", "R = C × 10^6 / (365 × N × V), per MEV"),
                    ("formula", "Segment crash rate", "R = C × 10^8 / (365 × N × V × L), per 100 MVMT"),
                    ("method", "Which multiplier and which extra term for a road segment?", "10^8 and the length L in miles"),
                    ("where", "Where are predictive crash methods (SPFs and CMFs)?", "HSM, Part C"),
                ],
                "lookups": [
                    {
                        "prompt": "You need a crash modification factor for adding a left-turn lane.",
                        "answer": "HSM, Part D (crash modification factors)",
                        "wrong": ["MUTCD, Part 2", "HCM, signalized intersections", "Green Book, Chapter 3"],
                        "explanation": "CMFs are collected in the HSM's Part D.",
                    },
                ],
                "locations": [
                    ("NCEES Handbook", "Transportation chapter: safety", "Crash rate formulas", "crash rate, million entering vehicles"),
                    ("HSM", "Part C (predictive method) and Part D (CMFs)", "Safety performance functions and CMFs", "SPF, CMF, predicted crashes"),
                ],
                "templates": [
                    {
                        "slug": "crash-rate-intersection",
                        "title": "Intersection crash rate",
                        "stem": "An intersection had {C} crashes over {N} years. The total entering volume is {V:,} veh/day. What is the crash rate per million entering vehicles?",
                        "solver": "crash_rate_intersection",
                        "params": {"C": [8, 40, 1], "N": [3, 5, 1], "V": [12000, 42000, 1000]},
                        "answer_unit": "per MEV",
                        "decimals": 2,
                        "est_minutes": "2",
                        "difficulty": 1,
                    },
                    {
                        "slug": "crash-rate-segment",
                        "title": "Segment crash rate",
                        "stem": "A {L}-mile rural highway segment with an ADT of {V:,} veh/day had {C} crashes in {N} years. What is the crash rate per 100 million vehicle-miles?",
                        "solver": "crash_rate_segment",
                        "params": {"C": [10, 60, 1], "N": [3, 5, 1], "V": [4000, 22000, 500], "L": [1.5, 6.0, 0.5]},
                        "answer_unit": "per 100 MVMT",
                        "decimals": 1,
                        "est_minutes": "3",
                        "difficulty": 1,
                        "explain_prompt": "Why does the segment formula use 10^8 while the intersection formula uses 10^6?",
                        "explain_answer": "Segment exposure is vehicle-miles, a much larger number than entering vehicles, so rates are scaled to 100 million vehicle-miles to give convenient values.",
                    },
                ],
            },
        ],
    },
    {
        "code": "HD",
        "name": "Horizontal design",
        "weight": "0.200",
        "items": [
            {
                "code": "HD1",
                "name": "Horizontal curve geometry",
                "method_name": "Circular curve elements (T, L, PC, PT stations)",
                "summary": "Compute tangent length, curve length and stations of a simple circular curve.",
                "cues": "PI station\nintersection angle\ndeflection angle\nPC\nPT\ntangent length\ncurve length",
                "lesson": {
                    "title": "Simple circular curve geometry",
                    "minutes": 10,
                    "body": """
When it applies
---------------

A question gives a radius (or degree of curve) and an intersection angle Δ and asks for curve elements or stations.

The elements
------------

::

    T = R × tan(Δ/2)            tangent length
    L = R × Δ × π / 180         curve length (Δ in degrees)
    E = R × (1/cos(Δ/2) − 1)    external distance
    M = R × (1 − cos(Δ/2))      middle ordinate
    D = 5729.58 / R             degree of curve, arc definition

Stationing
----------

Stations follow the alignment, which runs around the curve::

    PC = PI − T
    PT = PC + L

Never compute PT as PI + T. The tangents are not on the alignment once the curve is built.

Watch out
---------

* Δ in degrees needs π/180 in the length formula.
* Give stations in the form 123+45.67.
* Check that L is less than 2T.

Where it lives
--------------

The Handbook has the curve formulas and a curve diagram. The Green Book, Chapter 3, covers design controls.
""",
                },
                "cards": [
                    ("formula", "Tangent length of a circular curve", "T = R tan(Δ/2)"),
                    ("formula", "Length of a circular curve", "L = RΔπ/180 (Δ in degrees)"),
                    ("method", "Station of the PT", "PT = PC + L, where PC = PI − T"),
                    ("formula", "Degree of curve, arc definition", "D = 5729.58 / R"),
                    ("where", "Where is the circular curve diagram with T, E, M and L?", "NCEES Handbook, transportation chapter: horizontal curves"),
                ],
                "lookups": [
                    {
                        "prompt": "You need the formula for the external distance E of a circular curve.",
                        "answer": "NCEES Handbook, transportation chapter: horizontal curves",
                        "wrong": ["HCM, two-lane highways", "MUTCD, Part 3", "AASHTO 93, Part II"],
                        "explanation": "Curve geometry formulas are in the Handbook.",
                    },
                ],
                "locations": [
                    ("NCEES Handbook", "Transportation chapter: horizontal curves", "Circular curve formulas and diagram", "circular curve, tangent length, external distance"),
                    ("Green Book", "Chapter 3: Elements of Design", "Horizontal alignment design controls", "horizontal alignment, curve"),
                ],
                "templates": [
                    {
                        "slug": "curve-length",
                        "title": "Length of a circular curve",
                        "stem": "A simple circular curve has a radius of {R:,} ft and an intersection angle of {delta}°. What is the length of the curve?",
                        "solver": "hcurve_length",
                        "params": {"R": [700, 3200, 50], "delta": [16, 64, 2]},
                        "answer_unit": "ft",
                        "decimals": 1,
                        "est_minutes": "2",
                        "difficulty": 1,
                    },
                    {
                        "slug": "pt-station",
                        "title": "Station of the PT",
                        "stem": "The PI of a simple curve is at station {PI_sta}. The radius is {R:,} ft and the intersection angle is {delta}°. What is the station of the PT?",
                        "solver": "hcurve_pt_station",
                        "params": {"R": [800, 2800, 100], "delta": [18, 56, 2], "PI": [10500, 48500, 7.25]},
                        "answer_unit": "station",
                        "decimals": 2,
                        "min_gap": "10",
                        "est_minutes": "4",
                        "difficulty": 2,
                        "explain_prompt": "Why is PT not equal to PI + T?",
                        "explain_answer": "Once the curve is built, the alignment follows the arc from PC to PT. Stationing runs along the alignment, so PT = PC + L, which is shorter than PI + T.",
                    },
                ],
            },
            {
                "code": "HD2",
                "name": "Superelevation and side friction",
                "method_name": "Point-mass equation e + f = V²/15R",
                "summary": "Relate design speed, radius, superelevation and side friction.",
                "cues": "superelevation\nside friction factor\nminimum radius\ndesign speed\nemax",
                "lesson": {
                    "title": "Superelevation and minimum radius",
                    "minutes": 8,
                    "body": """
When it applies
---------------

Questions about the minimum radius for a design speed, or the superelevation a curve needs.

The method
----------

The simplified point-mass equation::

    e + f = V² / (15R)
    e = superelevation (ft/ft), f = side friction factor
    V = design speed (mi/h), R = radius (ft)

Rearranged::

    R_min = V² / (15(e_max + f_max))
    e     = V² / (15R) − f

The 15 already converts mi/h, so keep V in mi/h.

Watch out
---------

* e and f are decimals: 6% is 0.06.
* The 15 multiplies the whole sum (e + f).
* Side friction factors fall as speed rises. Use the value the problem gives, or look it up.

Where it lives
--------------

The Green Book, Chapter 3, has side friction factors and minimum radius tables. The Handbook gives the equation.
""",
                },
                "cards": [
                    ("formula", "Point-mass equation for curves", "e + f = V² / (15R), V in mi/h, R in ft"),
                    ("method", "Find the minimum radius for a design speed", "R = V² / (15(e_max + f_max))"),
                    ("variables", "Units of e and f in the point-mass equation", "Both decimals (ft/ft); 6% = 0.06"),
                    ("where", "Where are side friction factors by design speed?", "Green Book, Chapter 3 (Elements of Design)"),
                ],
                "lookups": [
                    {
                        "prompt": "You need the maximum side friction factor for a 55 mi/h design speed.",
                        "answer": "Green Book, Chapter 3 (Elements of Design)",
                        "wrong": ["HCM, basic freeway segments", "MUTCD, Part 2", "HSM, Part C"],
                        "explanation": "Design side friction values are tabulated with horizontal alignment in the Green Book.",
                    },
                ],
                "locations": [
                    ("Green Book", "Chapter 3: Elements of Design, horizontal alignment", "Side friction factors and minimum radii", "side friction, superelevation, minimum radius"),
                    ("NCEES Handbook", "Transportation chapter: horizontal curves", "Point-mass equation", "superelevation, side friction"),
                ],
                "templates": [
                    {
                        "slug": "minimum-radius",
                        "title": "Minimum radius for a design speed",
                        "stem": "A highway has a design speed of {V} mi/h and a maximum superelevation of {e}. The side friction factor for this speed is {f}. What is the minimum radius?",
                        "solver": "min_radius",
                        "params": {"V": [40, 70, 5], "e": {"choices": [0.04, 0.06, 0.08]}},
                        "answer_unit": "ft",
                        "decimals": 0,
                        "est_minutes": "2",
                        "difficulty": 1,
                    },
                    {
                        "slug": "required-superelevation",
                        "title": "Required superelevation",
                        "stem": "A curve with a radius of {R:,} ft carries traffic at {V} mi/h. With a side friction factor of {f}, what superelevation is required?",
                        "solver": "required_superelevation",
                        "params": {"V": [45, 65, 5], "R": [700, 2400, 50], "f": {"choices": [0.11, 0.12, 0.13, 0.14]}},
                        "answer_unit": "ft/ft",
                        "decimals": 3,
                        "est_minutes": "3",
                        "difficulty": 2,
                        "explain_prompt": "Why is f subtracted when solving for e?",
                        "explain_answer": "Superelevation and friction share the job of holding the vehicle on the curve. The friction already provides f, so the slope only has to supply the rest.",
                    },
                ],
            },
            {
                "code": "HD3",
                "name": "Horizontal sight distance",
                "method_name": "Sightline offset M = R(1 − cos(28.65S/R))",
                "summary": "Find the clear offset needed on the inside of a curve for stopping sight distance.",
                "cues": "sight obstruction\ninside of the curve\nlateral clearance\nmiddle ordinate\nhorizontal sightline offset",
                "lesson": {
                    "title": "Horizontal sightline offset",
                    "minutes": 7,
                    "body": """
When it applies
---------------

A wall, cut slope or building sits on the inside of a horizontal curve, and the question asks how far back it must be for the required sight distance.

The method
----------

::

    M = R × (1 − cos(28.65 × S / R))     angle in degrees
    R = radius to the centerline of the inside lane (ft)
    S = sight distance (ft), for S less than the curve length

28.65 × S / R is the half-angle in degrees (it equals S/2R in radians).

Watch out
---------

* Use the radius of the inside lane's centerline, not the road centerline.
* Put your calculator in degree mode for this form.
* M is measured from the inside lane's centerline.

Where it lives
--------------

The Green Book, Chapter 3, has the sightline offset equation and design charts.
""",
                },
                "cards": [
                    ("formula", "Horizontal sightline offset", "M = R(1 − cos(28.65S/R)), degrees"),
                    ("variables", "Which radius goes into the sightline offset formula?", "The radius to the centerline of the inside lane"),
                    ("where", "Where are horizontal sight distance design charts?", "Green Book, Chapter 3 (Elements of Design)"),
                ],
                "lookups": [
                    {
                        "prompt": "You need a chart of sightline offset versus radius for stopping sight distance.",
                        "answer": "Green Book, Chapter 3 (Elements of Design)",
                        "wrong": ["MUTCD, Part 6", "HCM, freeway weaving", "AASHTO 93, Part II"],
                        "explanation": "Horizontal sight distance is part of horizontal alignment in the Green Book.",
                    },
                ],
                "locations": [
                    ("Green Book", "Chapter 3: sight distance on horizontal curves", "Sightline offset equation and charts", "horizontal sightline offset, HSO"),
                ],
                "templates": [
                    {
                        "slug": "sightline-offset",
                        "title": "Required sightline offset",
                        "stem": "A curve has a radius of {R:,} ft to the centerline of the inside lane. The required stopping sight distance is {S} ft. How far from the inside lane centerline must obstructions be cleared?",
                        "solver": "hsd_offset",
                        "params": {"R": [600, 2400, 50], "S": [250, 650, 25]},
                        "answer_unit": "ft",
                        "decimals": 1,
                        "est_minutes": "3",
                        "difficulty": 2,
                    },
                ],
            },
        ],
    },
    {
        "code": "VD",
        "name": "Vertical design",
        "weight": "0.200",
        "items": [
            {
                "code": "VD1",
                "name": "Vertical curve elevations",
                "method_name": "Parabolic vertical curve equation",
                "summary": "Find elevations and the high or low point on an equal-tangent vertical curve.",
                "cues": "PVI\nPVC\nPVT\nentering grade\nexiting grade\nhigh point\nlow point\nelevation at station",
                "lesson": {
                    "title": "Elevations on a vertical curve",
                    "minutes": 10,
                    "body": """
When it applies
---------------

A question gives grades, a curve length and the PVI, and asks for an elevation or the high or low point.

The method
----------

Start at the PVC, which is half the curve length before the PVI::

    PVC station   = PVI station − L/2
    PVC elevation = PVI elevation − g1 × L/2

Then use the parabola, with x in feet from the PVC and grades as decimals::

    y = E_PVC + g1·x + (g2 − g1)·x² / (2L)

The high or low point is where the grade is zero::

    x = −g1 × L / (g2 − g1)

Watch out
---------

* Always measure x from the PVC.
* Grades are decimals in the curve term.
* A turning point exists only when g1 and g2 have opposite signs.

Where it lives
--------------

The Handbook has the vertical curve equations and a diagram.
""",
                },
                "cards": [
                    ("formula", "Elevation on an equal-tangent vertical curve", "y = E_PVC + g1·x + (g2 − g1)x² / (2L)"),
                    ("formula", "Distance from the PVC to the high or low point", "x = −g1 L / (g2 − g1)"),
                    ("method", "First step in any vertical curve elevation problem", "Find the PVC: station PVI − L/2, elevation E_PVI − g1 L/2"),
                    ("where", "Where is the vertical curve diagram with PVC, PVI and PVT?", "NCEES Handbook, transportation chapter: vertical curves"),
                ],
                "lookups": [
                    {
                        "prompt": "You need the equation for elevation at a point on a vertical curve.",
                        "answer": "NCEES Handbook, transportation chapter: vertical curves",
                        "wrong": ["HCM, two-lane highways", "MUTCD, Part 3", "HSM, Part C"],
                        "explanation": "The parabola equation and curve diagram are in the Handbook.",
                    },
                ],
                "locations": [
                    ("NCEES Handbook", "Transportation chapter: vertical curves", "Equations and diagram", "vertical curve, PVC, PVI, high point"),
                    ("Green Book", "Chapter 3: vertical alignment", "Design controls for vertical curves", "vertical curve, K value"),
                ],
                "templates": [
                    {
                        "slug": "vertical-curve-elevation",
                        "title": "Elevation on a vertical curve",
                        "stem": "An equal-tangent vertical curve {L} ft long has its PVI at station {PVI_sta}, elevation {E_PVI} ft. The entering grade is {g1}% and the exiting grade is {g2}%. What is the elevation at station {sta}?",
                        "solver": "vcurve_elevation",
                        "params": {
                            "g1": {"choices": [-4, -3, -2, -1, 1, 2, 3, 4]},
                            "g2": {"choices": [-4, -3, -2, -1, 1, 2, 3, 4]},
                            "L": [400, 1200, 100],
                            "PVI": [10000, 40000, 50],
                            "E_PVI": [420, 880, 0.5],
                            "x_frac": {"choices": [0.2, 0.25, 0.3, 0.4, 0.6, 0.7, 0.75, 0.8]},
                        },
                        "answer_unit": "ft",
                        "decimals": 2,
                        "min_gap": "0.5",
                        "est_minutes": "5",
                        "difficulty": 2,
                        "explain_prompt": "Why must x be measured from the PVC and not from the PVI?",
                        "explain_answer": "The parabola's equation starts at the PVC with the entering grade. Measured from the PVI, the starting elevation and grade would both be wrong.",
                    },
                    {
                        "slug": "vertical-curve-turning-point",
                        "title": "Station of the high or low point",
                        "stem": "A {L}-ft vertical curve has its PVI at station {PVI_sta}. The entering grade is {g1}% and the exiting grade is {g2}%. At what station is the {kind} point?",
                        "solver": "vcurve_turning_point",
                        "params": {
                            "g1": {"choices": [-4, -3, -2, 2, 3, 4, 5]},
                            "g2": {"choices": [-5, -4, -3, -2, 2, 3, 4]},
                            "L": [400, 1200, 100],
                            "PVI": [10000, 40000, 50],
                        },
                        "answer_unit": "station",
                        "decimals": 2,
                        "min_gap": "10",
                        "est_minutes": "4",
                        "difficulty": 2,
                    },
                ],
            },
            {
                "code": "VD2",
                "name": "Vertical curve length for sight distance",
                "method_name": "Crest and sag curve length (S < L and S > L)",
                "summary": "Find the minimum curve length that provides stopping sight distance.",
                "cues": "crest curve\nsag curve\nheadlight sight distance\nminimum length\nalgebraic difference in grades",
                "lesson": {
                    "title": "Curve length for sight distance",
                    "minutes": 10,
                    "body": """
When it applies
---------------

A question asks for the minimum crest or sag curve length for a given stopping sight distance.

Crest curves
------------

With a 3.5 ft eye height and a 2.0 ft object height::

    S < L:  L = A·S² / 2158
    S > L:  L = 2S − 2158 / A
    A = |g1 − g2| in percent

Sag curves
----------

Headlight sight distance governs::

    S < L:  L = A·S² / (400 + 3.5S)
    S > L:  L = 2S − (400 + 3.5S) / A

The method
----------

1. Decide crest or sag from the grades.
2. Assume S < L and compute L.
3. Check the assumption. If S > L, use the other formula.

Watch out
---------

* A is in percent, not a decimal.
* Always check S against L.
* Many agencies use K = L/A tables instead. They give the same answer.

Where it lives
--------------

The Green Book, Chapter 3, has both pairs of equations and K-value tables.
""",
                },
                "cards": [
                    ("formula", "Crest curve length, S < L", "L = AS² / 2158 (3.5 ft eye, 2.0 ft object)"),
                    ("formula", "Sag curve length, S < L (headlights)", "L = AS² / (400 + 3.5S)"),
                    ("method", "After computing a curve length with the S < L formula, what must you do?", "Check that S < L; if not, use the S > L formula"),
                    ("variables", "Units of A in curve length formulas", "Percent: a change from +2% to −3% is A = 5"),
                    ("where", "Where are K values for crest and sag curves?", "Green Book, Chapter 3 (vertical alignment)"),
                ],
                "lookups": [
                    {
                        "prompt": "You need the design K value for a sag curve at 60 mi/h.",
                        "answer": "Green Book, Chapter 3 (vertical alignment)",
                        "wrong": ["NCEES Handbook, hydraulics chapter", "MUTCD, Part 2", "HCM, basic freeway segments"],
                        "explanation": "K-value design controls are tabulated with vertical alignment.",
                    },
                ],
                "locations": [
                    ("Green Book", "Chapter 3: vertical alignment", "Crest and sag length equations and K values", "K value, crest vertical curve, sag vertical curve"),
                    ("NCEES Handbook", "Transportation chapter: vertical curves", "Sight distance length equations", "crest, sag, sight distance"),
                ],
                "templates": [
                    {
                        "slug": "crest-curve-length",
                        "title": "Minimum crest curve length",
                        "stem": "A crest vertical curve joins a {g1}% grade to a {g2}% grade. The required stopping sight distance is {S} ft. What is the minimum curve length, using an eye height of 3.5 ft and an object height of 2.0 ft?",
                        "solver": "crest_length",
                        "params": {"g1": {"choices": [1, 2, 3, 4]}, "g2": {"choices": [-1, -2, -3, -4]}, "S": [250, 650, 25]},
                        "answer_unit": "ft",
                        "decimals": 0,
                        "est_minutes": "4",
                        "difficulty": 2,
                    },
                    {
                        "slug": "sag-curve-length",
                        "title": "Minimum sag curve length",
                        "stem": "A sag vertical curve joins a {g1}% grade to a {g2}% grade. Headlight sight distance must equal the stopping sight distance of {S} ft. What is the minimum curve length?",
                        "solver": "sag_length",
                        "params": {"g1": {"choices": [-1, -2, -3, -4]}, "g2": {"choices": [1, 2, 3, 4]}, "S": [250, 650, 25]},
                        "answer_unit": "ft",
                        "decimals": 0,
                        "est_minutes": "4",
                        "difficulty": 2,
                        "explain_prompt": "Why does headlight sight distance govern sag curves?",
                        "explain_answer": "In daylight you can see over a sag, but at night the headlight beam hits the upgrade ahead, so the beam's reach limits sight distance.",
                    },
                ],
            },
        ],
    },
    {
        "code": "SD",
        "name": "Sight distance",
        "weight": "0.100",
        "items": [
            {
                "code": "SD1",
                "name": "Stopping sight distance",
                "method_name": "SSD = reaction distance + braking distance",
                "summary": "Compute stopping sight distance on level roads and grades.",
                "cues": "stopping sight distance\nbrake reaction time\ndeceleration\ndowngrade\nupgrade",
                "lesson": {
                    "title": "Stopping sight distance",
                    "minutes": 8,
                    "body": """
When it applies
---------------

Any question about the distance needed to stop, or used as an input to curve design.

The method
----------

::

    SSD = 1.47·V·t + V² / (30 × ((a / 32.2) ± G))
    V = speed (mi/h), t = brake reaction time (s), usually 2.5
    a = deceleration (ft/s²), usually 11.2
    G = grade as a decimal: + upgrade, − downgrade

The first term is the reaction distance and the second the braking distance.

Watch out
---------

* The 1.47 converts mi/h to ft/s in the reaction term only.
* A downgrade makes G negative, which lengthens the braking distance.
* Give SSD as the sum of both terms.

Where it lives
--------------

The Green Book, Chapter 3, has the SSD equation and design tables. The Handbook gives the equation.
""",
                },
                "cards": [
                    ("formula", "Stopping sight distance", "SSD = 1.47Vt + V² / (30((a/32.2) ± G))"),
                    ("variables", "Design brake reaction time and deceleration rate", "t = 2.5 s, a = 11.2 ft/s²"),
                    ("method", "Sign of G on a downgrade", "Negative: it reduces the denominator and lengthens the braking distance"),
                    ("where", "Where are design SSD values by speed?", "Green Book, Chapter 3 (sight distance)"),
                ],
                "lookups": [
                    {
                        "prompt": "You need the design stopping sight distance for 50 mi/h on level ground.",
                        "answer": "Green Book, Chapter 3 (sight distance)",
                        "wrong": ["MUTCD, Part 4", "HCM, urban streets", "HSM, Part D"],
                        "explanation": "Design SSD values are tabulated in the Green Book's sight distance section.",
                    },
                ],
                "locations": [
                    ("Green Book", "Chapter 3: sight distance", "SSD equation and design values", "stopping sight distance, brake reaction"),
                    ("NCEES Handbook", "Transportation chapter: sight distance", "SSD equation", "stopping sight distance"),
                ],
                "templates": [
                    {
                        "slug": "ssd-on-grade",
                        "title": "Stopping sight distance on a grade",
                        "stem": "Find the stopping sight distance for a design speed of {V} mi/h on a {G_abs}% {G_word}. Use a brake reaction time of 2.5 s and a deceleration rate of 11.2 ft/s².",
                        "solver": "ssd",
                        "params": {"V": [35, 70, 5], "G": {"choices": [-6, -5, -4, -3, 3, 4, 5, 6]}},
                        "answer_unit": "ft",
                        "decimals": 0,
                        "est_minutes": "3",
                        "difficulty": 2,
                        "explain_prompt": "Why does a downgrade lengthen stopping distance?",
                        "explain_answer": "Gravity pulls the vehicle down the slope, so less of the braking force goes into slowing it. The effective deceleration drops and the distance grows.",
                    },
                    {
                        "slug": "ssd-level",
                        "title": "Stopping sight distance on level ground",
                        "stem": "A driver travelling at {V} mi/h on a level road has a brake reaction time of {t} s. Using a deceleration rate of 11.2 ft/s², what is the stopping sight distance?",
                        "solver": "ssd",
                        "params": {"V": [30, 70, 5], "G": {"choices": [0]}, "t": {"choices": [2.0, 2.5, 3.0]}},
                        "answer_unit": "ft",
                        "decimals": 0,
                        "est_minutes": "2",
                        "difficulty": 1,
                    },
                ],
            },
        ],
    },
    {
        "code": "EP",
        "name": "Earthwork and pavements",
        "weight": "0.150",
        "items": [
            {
                "code": "EP1",
                "name": "Earthwork quantities",
                "method_name": "Average end area and shrinkage",
                "summary": "Compute cut and fill volumes and borrow with shrinkage.",
                "cues": "cross-sectional area\nend area\ncut\nfill\nborrow\nshrinkage\nbank cubic yards",
                "lesson": {
                    "title": "Earthwork volumes",
                    "minutes": 8,
                    "body": """
When it applies
---------------

A question gives cross-section areas at stations, or cut and fill totals with a shrinkage factor.

Average end area
----------------

::

    V = L × (A1 + A2) / 2        ft³
    V / 27                       yd³

Shrinkage and borrow
--------------------

Soil excavated from the bank and compacted in a fill takes up less space::

    compacted volume = bank volume × (1 − shrinkage)
    bank volume      = compacted volume / (1 − shrinkage)

To size borrow, find the compacted shortfall, then convert it back to bank volume.

Watch out
---------

* 27 ft³ per yd³.
* Keep track of bank, loose and compacted volumes.
* Borrow is usually priced in bank cubic yards.

Where it lives
--------------

The Handbook has the earthwork formulas, including the prismoidal formula.
""",
                },
                "cards": [
                    ("formula", "Average end area volume", "V = L(A1 + A2)/2, then ÷ 27 for yd³"),
                    ("method", "Convert a compacted shortfall into bank cubic yards of borrow", "Divide by (1 − shrinkage)"),
                    ("variables", "Cubic feet in a cubic yard", "27"),
                    ("where", "Where are the earthwork volume formulas?", "NCEES Handbook, earthwork section"),
                ],
                "lookups": [
                    {
                        "prompt": "You need the prismoidal formula for earthwork volume.",
                        "answer": "NCEES Handbook, earthwork section",
                        "wrong": ["Green Book, Chapter 4", "HCM, two-lane highways", "MUTCD, Part 6"],
                        "explanation": "Earthwork formulas are in the Handbook.",
                    },
                ],
                "locations": [
                    ("NCEES Handbook", "Earthwork section", "Average end area, prismoidal formula, shrink and swell", "average end area, prismoidal, shrinkage"),
                ],
                "templates": [
                    {
                        "slug": "average-end-area",
                        "title": "Volume by average end area",
                        "stem": "Cut cross-sections {L} ft apart have areas of {A1} ft² and {A2} ft². What is the volume of cut between them?",
                        "solver": "avg_end_area",
                        "params": {"A1": [120, 640, 5], "A2": [120, 640, 5], "L": {"choices": [50, 100]}},
                        "answer_unit": "yd³",
                        "decimals": 0,
                        "est_minutes": "2",
                        "difficulty": 1,
                    },
                    {
                        "slug": "borrow-with-shrinkage",
                        "title": "Borrow volume with shrinkage",
                        "stem": "A project needs {Vf:,} yd³ of compacted fill. The cut yields {Vc:,} bank yd³ of suitable material, and the shrinkage factor is {s}%. How many bank cubic yards of borrow are needed?",
                        "solver": "borrow_volume",
                        "params": {"Vf": [18000, 60000, 500], "Vc": [10000, 48000, 500], "s": [10, 25, 1]},
                        "answer_unit": "yd³",
                        "decimals": 0,
                        "est_minutes": "4",
                        "difficulty": 2,
                        "explain_prompt": "Why is the compacted shortfall divided by (1 − shrinkage)?",
                        "explain_answer": "Borrow material shrinks when compacted, just like the cut. To end up with the shortfall in place, you must dig a larger bank volume.",
                    },
                ],
            },
            {
                "code": "EP2",
                "name": "Flexible pavement structural number",
                "method_name": "Structural number SN = Σ aᵢDᵢmᵢ",
                "summary": "Compute a flexible pavement's structural number and size a layer.",
                "cues": "structural number\nlayer coefficient\ndrainage coefficient\nasphalt surface\nbase course\nsubbase",
                "lesson": {
                    "title": "Structural number of a flexible pavement",
                    "minutes": 8,
                    "body": """
When it applies
---------------

A question gives layer coefficients, thicknesses and drainage coefficients, and asks for SN or a layer thickness.

The method
----------

::

    SN = a1·D1 + a2·D2·m2 + a3·D3·m3
    a = layer coefficient, D = thickness (in), m = drainage coefficient

The asphalt surface has no drainage coefficient. To size a layer, subtract what the other layers supply, then divide by that layer's a·m.

Watch out
---------

* Thicknesses in inches.
* Apply m to the base and subbase only.
* Agencies round layer thicknesses up to a practical increment.

Where it lives
--------------

The AASHTO 1993 Guide, Part II, covers flexible pavement design, layer coefficients and drainage coefficients.
""",
                },
                "cards": [
                    ("formula", "Structural number of a flexible pavement", "SN = a1D1 + a2D2m2 + a3D3m3"),
                    ("method", "Which layers get a drainage coefficient m?", "Base and subbase only, not the asphalt surface"),
                    ("variables", "Units of D in the SN equation", "Inches"),
                    ("where", "Where are drainage coefficients for untreated base and subbase?", "AASHTO 93 Guide, Part II"),
                ],
                "lookups": [
                    {
                        "prompt": "You need recommended drainage coefficients for an untreated base.",
                        "answer": "AASHTO 93 Guide, Part II (flexible pavement design)",
                        "wrong": ["Green Book, Chapter 4", "NCEES Handbook, hydrology chapter", "HCM, urban streets"],
                        "explanation": "Drainage coefficients are part of the 1993 Guide's flexible design procedure.",
                    },
                ],
                "locations": [
                    ("AASHTO 93", "Part II: flexible pavement design", "Layer and drainage coefficients, design equation", "structural number, layer coefficient, drainage coefficient"),
                    ("NCEES Handbook", "Transportation chapter: pavement design", "Structural number equation", "structural number"),
                ],
                "templates": [
                    {
                        "slug": "structural-number",
                        "title": "Structural number of a section",
                        "stem": "A flexible pavement has {D1} in of asphalt (a₁ = {a1}), {D2} in of granular base (a₂ = {a2}, m₂ = {m2}) and {D3} in of subbase (a₃ = {a3}, m₃ = {m3}). What is its structural number?",
                        "solver": "structural_number",
                        "params": {
                            "a1": {"choices": [0.40, 0.42, 0.44]},
                            "D1": [3, 6, 0.5],
                            "a2": {"choices": [0.12, 0.14]},
                            "D2": [6, 12, 1],
                            "m2": {"choices": [0.8, 1.0, 1.1]},
                            "a3": {"choices": [0.08, 0.10, 0.11]},
                            "D3": [6, 14, 1],
                            "m3": {"choices": [0.8, 1.0, 1.1]},
                        },
                        "answer_unit": "",
                        "decimals": 2,
                        "est_minutes": "3",
                        "difficulty": 1,
                    },
                    {
                        "slug": "base-thickness",
                        "title": "Base thickness for a required SN",
                        "stem": "A design requires SN = {SN}. The section has {D1} in of asphalt (a₁ = {a1}) and {D3} in of subbase (a₃ = {a3}, m₃ = {m3}). The base has a₂ = {a2} and m₂ = {m2}. What base thickness is required?",
                        "solver": "base_thickness",
                        "params": {
                            "SN": [3.6, 5.6, 0.1],
                            "a1": {"choices": [0.40, 0.42, 0.44]},
                            "D1": [3, 5, 0.5],
                            "a2": {"choices": [0.12, 0.14]},
                            "m2": {"choices": [0.8, 1.0, 1.1]},
                            "a3": {"choices": [0.08, 0.10, 0.11]},
                            "D3": [6, 12, 1],
                            "m3": {"choices": [0.8, 1.0]},
                        },
                        "answer_unit": "in",
                        "decimals": 1,
                        "est_minutes": "4",
                        "difficulty": 2,
                    },
                ],
            },
        ],
    },
    {
        "code": "TC",
        "name": "Traffic control devices",
        "weight": "0.100",
        "items": [
            {
                "code": "TC1",
                "name": "Temporary traffic control tapers",
                "method_name": "MUTCD taper length L = WS²/60 or WS",
                "summary": "Size merging, shifting and shoulder tapers in work zones.",
                "cues": "work zone\nlane closure\nmerging taper\nshifting taper\nshoulder taper\nposted speed",
                "lesson": {
                    "title": "Work zone taper lengths",
                    "minutes": 7,
                    "body": """
When it applies
---------------

A question about a lane closure or lane shift in a work zone, giving a speed and an offset width.

The method
----------

The base taper length L depends on the speed::

    S ≤ 40 mi/h:  L = W·S² / 60
    S ≥ 45 mi/h:  L = W·S
    W = width of offset (ft), S = posted speed or 85th-percentile speed (mi/h)

Then apply the taper type:

* Merging taper: at least L.
* Shifting taper: at least L/2.
* Shoulder taper: at least L/3.

Watch out
---------

* Pick the formula by speed first.
* W is the lateral offset, often one lane width.
* Check which taper the question describes.

Where it lives
--------------

The MUTCD, Part 6 (Temporary Traffic Control), has the taper formulas and typical applications. The MUTCD is public domain, so you can study it directly at mutcd.fhwa.dot.gov.
""",
                },
                "cards": [
                    ("formula", "Taper length at 40 mi/h or less", "L = WS² / 60"),
                    ("formula", "Taper length at 45 mi/h or more", "L = WS"),
                    ("method", "Share of L for shifting and shoulder tapers", "Shifting: L/2. Shoulder: L/3"),
                    ("where", "Where are work zone taper criteria?", "MUTCD, Part 6 (Temporary Traffic Control)"),
                ],
                "lookups": [
                    {
                        "prompt": "You need the typical application drawing for a lane closure on a two-lane road.",
                        "answer": "MUTCD, Part 6 (Temporary Traffic Control)",
                        "wrong": ["MUTCD, Part 3", "Green Book, Chapter 10", "HCM, work zones"],
                        "explanation": "Typical applications for temporary traffic control are in MUTCD Part 6.",
                    },
                    {
                        "prompt": "You need the standard shape and color for a STOP sign.",
                        "answer": "MUTCD, Part 2 (Signs)",
                        "wrong": ["MUTCD, Part 4", "Green Book, Chapter 9", "HSM, Part D"],
                        "explanation": "Sign design and placement standards are in MUTCD Part 2.",
                    },
                ],
                "locations": [
                    ("MUTCD", "Part 6: Temporary Traffic Control", "Taper length criteria and typical applications", "taper length, merging taper, lane closure"),
                    ("MUTCD", "Part 2: Signs", "Sign standards", "regulatory signs, warning signs"),
                ],
                "templates": [
                    {
                        "slug": "ttc-taper-length",
                        "title": "Work zone taper length",
                        "stem": "A work zone on a road with a posted speed of {S} mi/h requires a {kind} taper with a lateral offset of {W} ft. What is the minimum taper length?",
                        "solver": "ttc_taper",
                        "params": {"S": [25, 65, 5], "W": {"choices": [10, 11, 12]}, "kind": {"choices": ["merging", "shifting", "shoulder"]}},
                        "answer_unit": "ft",
                        "decimals": 0,
                        "est_minutes": "2",
                        "difficulty": 1,
                        "explain_prompt": "Why can a shifting taper be shorter than a merging taper?",
                        "explain_answer": "In a shift every lane keeps flowing and drivers only move sideways. In a merge, drivers must find a gap and change lanes, which needs more distance.",
                    },
                ],
            },
        ],
    },
]
