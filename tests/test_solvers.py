"""Solver answers checked against hand-worked values."""

import math
import random
from types import SimpleNamespace

from django.test import SimpleTestCase

from curriculum import content
from curriculum.generation import draw, units_question
from curriculum.solvers import REGISTRY, station


def solve(name, **p):
    return REGISTRY[name](p)


class KnownValues(SimpleTestCase):
    def test_flow_rate(self):
        self.assertEqual(solve("flow_rate", k=30, v=50, lanes=3).answer, 4500)

    def test_yellow_interval_level(self):
        # 1.0 + 1.47×45 / (2×10) = 4.3075 s
        self.assertAlmostEqual(solve("yellow_interval", V=45, G=0).answer, 1 + 1.47 * 45 / 20, places=6)

    def test_downgrade_lengthens_yellow(self):
        self.assertGreater(solve("yellow_interval", V=45, G=-3).answer, solve("yellow_interval", V=45, G=3).answer)

    def test_webster(self):
        # (1.5×12 + 5) / (1 − 0.6) = 57.5
        s = solve("webster_cycle", L=12, y1=0.3, y2=0.2, y3=0.1)
        self.assertAlmostEqual(s.answer, 57.5)

    def test_crash_rates(self):
        self.assertAlmostEqual(solve("crash_rate_intersection", C=20, N=4, V=25000).answer, 20e6 / (365 * 4 * 25000))
        self.assertAlmostEqual(solve("crash_rate_segment", C=30, N=3, V=10000, L=2.0).answer, 30e8 / (365 * 3 * 10000 * 2))

    def test_curve_length_and_pt(self):
        self.assertAlmostEqual(solve("hcurve_length", R=1000, delta=30).answer, 1000 * math.pi / 6)
        T = 1000 * math.tan(math.radians(15))
        self.assertAlmostEqual(solve("hcurve_pt_station", R=1000, delta=30, PI=20000).answer, 20000 - T + 1000 * math.pi / 6)

    def test_min_radius(self):
        # 60 mi/h, e = 0.08, f = 0.12: 3600 / (15 × 0.20) = 1200 ft
        self.assertAlmostEqual(solve("min_radius", V=60, e=0.08).answer, 1200)

    def test_sightline_offset(self):
        m = solve("hsd_offset", R=1000, S=400).answer
        self.assertAlmostEqual(m, 1000 * (1 - math.cos(math.radians(28.65 * 400 / 1000))))
        self.assertAlmostEqual(m, 400**2 / (8 * 1000), delta=0.5)  # close to the S²/8R approximation

    def test_vertical_curve_elevation(self):
        # PVI 10+00 at 500.00, g1 +2%, g2 −2%, L 400: PVC 8+00 at 496.00.
        # At x = 100: 496 + 2 − 0.04/800 × 10,000 = 497.50
        s = solve("vcurve_elevation", g1=2, g2=-2, L=400, PVI=1000, E_PVI=500, x_frac=0.25)
        self.assertAlmostEqual(s.answer, 497.5)

    def test_turning_point(self):
        # g1 +3, g2 −2, L 500: x = 300 from PVC at 7+50 → 10+50
        self.assertAlmostEqual(solve("vcurve_turning_point", g1=3, g2=-2, L=500, PVI=1000).answer, 1050)

    def test_crest_length_cases(self):
        self.assertAlmostEqual(solve("crest_length", g1=3, g2=-3, S=500).answer, 6 * 500**2 / 2158)  # S < L
        self.assertAlmostEqual(solve("crest_length", g1=1, g2=-2, S=500).answer, 1000 - 2158 / 3)  # S > L

    def test_ssd_level(self):
        # 60 mi/h: 1.47×60×2.5 + 3600/(30×0.3478) ≈ 220.5 + 345.0
        s = solve("ssd", V=60, G=0)
        self.assertAlmostEqual(s.answer, 1.47 * 60 * 2.5 + 3600 / (30 * 11.2 / 32.2))

    def test_earthwork(self):
        self.assertAlmostEqual(solve("avg_end_area", A1=300, A2=500, L=100).answer, 100 * 400 / 27)
        b = solve("borrow_volume", Vf=30000, Vc=20000, s=20).answer
        self.assertAlmostEqual(b, (30000 - 16000) / 0.8)

    def test_structural_number(self):
        sn = solve("structural_number", a1=0.44, D1=4, a2=0.14, D2=10, m2=1.0, a3=0.11, D3=8, m3=1.0).answer
        self.assertAlmostEqual(sn, 1.76 + 1.4 + 0.88)

    def test_ttc_taper(self):
        self.assertAlmostEqual(solve("ttc_taper", W=12, S=40, kind="merging").answer, 12 * 1600 / 60)
        self.assertAlmostEqual(solve("ttc_taper", W=12, S=55, kind="shifting").answer, 12 * 55 / 2)

    def test_station_format(self):
        self.assertEqual(station(12345.678), "123+45.68")
        self.assertEqual(station(1005), "10+05.00")


class EveryTemplateDraws(SimpleTestCase):
    """Every seeded template draws valid, distinct, well-labelled choices."""

    def test_draws(self):
        rng = random.Random(3)
        for area in content.AREAS:
            for item in area["items"]:
                for t in item["templates"]:
                    tpl = SimpleNamespace(**{"min_gap": None, **t})
                    for _ in range(50):
                        d = draw(tpl, rng)
                        self.assertEqual(len(d["choices"]), 4, t["slug"])
                        self.assertEqual(sum(1 for c in d["choices"] if not c["cause"]), 1, t["slug"])
                        self.assertTrue(all(c["note"] for c in d["choices"] if c["cause"]), t["slug"])
                        self.assertNotIn("{", d["stem"], t["slug"])
                        self.assertTrue(any(s.get("wrong") for s in d["steps"]), f"{t['slug']} has no flawed step")

    def test_units(self):
        q = units_question(random.Random(1))
        self.assertIn("answer", q)
