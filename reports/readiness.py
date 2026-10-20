"""The readiness estimate, phase gates and study priorities.

Predicted score = Σ wᵢ pᵢ over specification areas, where wᵢ is the area's
share of exam questions and pᵢ the student's estimated accuracy there.
Each item's accuracy weights recent work most (a 21-day half-life), gives
half credit for hinted or very slow correct answers, and is pulled toward
the student's overall accuracy when evidence is thin. An unstudied item
scores 0.25, the rate of guessing among four choices. Full simulations
are blended in and count for more as they accumulate.

The working target (settings.COURSE["WORKING_TARGET"]) is an assumption:
NCEES does not publish a fixed passing percentage.
"""

import math
import statistics
from dataclasses import dataclass, field
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from curriculum.models import SpecArea, SpecItem
from learning import mastery as mastery_rules
from learning.models import Attempt, LevelChoices, PracticeSession, StudentProfile

from .models import ReadinessSnapshot, Zone

HALF_LIFE_DAYS = 21
SHRINK_K = 4
GUESS = 0.25


def course():
    return settings.COURSE


@dataclass
class ItemEstimate:
    item: SpecItem
    weight: float  # share of the exam
    p: float
    n: float
    level: int
    median_seconds: float | None


@dataclass
class Estimate:
    zone: str
    zone_reason: str
    low: float | None
    mid: float | None
    high: float | None
    topic_score: float
    sim_scores: list = field(default_factory=list)
    coverage_practicing: float = 0
    coverage_introduced: float = 0
    coverage_proficient: float = 0
    evidence: int = 0
    items: list = field(default_factory=list)
    areas: list = field(default_factory=list)
    median_pace: float | None = None
    diagnostic_done: bool = False

    @property
    def target(self):
        return course()["WORKING_TARGET"]

    @property
    def zone_label(self):
        return Zone(self.zone).label


def item_weights():
    """{item_id: share of exam}, splitting each area's weight across its items."""
    out = {}
    for area in SpecArea.objects.prefetch_related("items"):
        items = list(area.items.all())
        for it in items:
            out[it.id] = float(area.weight) / len(items)
    return out


def session_score(session):
    attempts = list(session.attempts.filter(kind=Attempt.Kind.PROBLEM))
    total = len(session.items)
    if not total:
        return None
    return sum(1 for a in attempts if a.is_correct) / total


def finished_sims(student, kind=PracticeSession.Kind.FULL_EXAM, before=None):
    qs = PracticeSession.objects.filter(student=student, kind=kind, finished_at__isnull=False)
    if before:
        qs = qs.filter(finished_at__lte=before)
    return list(qs.order_by("-finished_at"))


def estimate(student, levels=None, now=None):
    now = now or timezone.now()
    levels = levels or mastery_rules.levels(student)
    pace = mastery_rules.pace_seconds()
    weights = item_weights()
    items = list(SpecItem.objects.select_related("area"))

    attempts = list(Attempt.objects.filter(student=student, kind=Attempt.Kind.PROBLEM, counts_for_mastery=True))
    if attempts:
        prior = sum(a.is_correct for a in attempts) / len(attempts)
    else:
        prior = 0.5
    by_item = {}
    for a in attempts:
        by_item.setdefault(a.spec_item_id, []).append(a)

    item_est = []
    for it in items:
        rows = by_item.get(it.id, [])
        lvl = levels[it.id].level if it.id in levels else 0
        if not rows:
            item_est.append(ItemEstimate(it, weights[it.id], GUESS, 0, lvl, None))
            continue
        num = den = 0.0
        for a in rows:
            age = (now - a.created_at).total_seconds() / 86400
            w = 0.5 ** (age / HALF_LIFE_DAYS)
            credit = 1.0 if a.is_correct else 0.0
            if a.is_correct and (a.hint_used or a.seconds > 2 * pace):
                credit = 0.5
            num += w * credit
            den += w
        p = (num + SHRINK_K * prior) / (den + SHRINK_K)
        item_est.append(ItemEstimate(it, weights[it.id], p, den, lvl, statistics.median(a.seconds for a in rows)))

    total_w = sum(e.weight for e in item_est) or 1
    topic = sum(e.weight * e.p for e in item_est) / total_w

    sims = finished_sims(student, before=now)
    sim_scores = [(s, session_score(s)) for s in sims]
    recent = [sc for _, sc in sim_scores[:2] if sc is not None]
    b = min(0.6, 0.3 * len(recent))
    mid = (1 - b) * topic + b * (sum(recent) / len(recent) if recent else 0)

    evidence = len(attempts)
    n_eff = evidence + 80 * len(recent)
    half = 1.96 * math.sqrt(mid * (1 - mid) / max(n_eff, 1))
    half = min(max(half, 0.03), 0.25)
    low, high = max(0.0, mid - half), min(1.0, mid + half)

    def cover(min_level):
        return sum(e.weight for e in item_est if e.level >= min_level) / total_w

    cov_intro, cov_prac, cov_prof = cover(LevelChoices.INTRODUCED), cover(LevelChoices.PRACTICING), cover(LevelChoices.PROFICIENT)
    diagnostic_done = PracticeSession.objects.filter(
        student=student, kind=PracticeSession.Kind.DIAGNOSTIC, finished_at__isnull=False
    ).exists()
    recent_times = [a.seconds for a in sorted(attempts, key=lambda a: a.created_at, reverse=True)[:30]]
    median_pace = statistics.median(recent_times) if recent_times else None

    target = course()["WORKING_TARGET"]
    if not diagnostic_done:
        zone, reason = Zone.NONE, "The estimate appears after the baseline diagnostic."
    elif cov_intro < course()["MIN_COVERAGE_FOR_ZONE"]:
        zone, reason = Zone.NONE, f"The estimate appears once {course()['MIN_COVERAGE_FOR_ZONE']:.0%} of exam weight has been studied."
    elif cov_prac < 0.4:
        zone, reason = Zone.NOT_YET, "Less than 40% of exam weight is at Practicing or above."
    elif high < target:
        zone, reason = Zone.BUILDING, "The likely range sits below the target line."
    else:
        window = now - timedelta(days=21)
        strong_sims = [s for s, sc in sim_scores if sc is not None and sc >= target and s.finished_at >= window]
        on_pace = median_pace is not None and median_pace <= mastery_rules.pace_seconds()
        if low >= target and len(strong_sims) >= 2 and on_pace:
            zone, reason = Zone.READY, "The whole range is above the target, with two strong simulations in the last 3 weeks."
        elif low >= target and len(strong_sims) < 2:
            zone, reason = Zone.APPROACHING, "Topic work is above the target; two full simulations at the target are still needed."
        else:
            zone, reason = Zone.APPROACHING, "The likely range overlaps the target line."

    areas = []
    for area in SpecArea.objects.order_by("order"):
        rows = [e for e in item_est if e.item.area_id == area.id]
        n = sum(len(by_item.get(e.item.id, [])) for e in rows)
        correct = sum(sum(a.is_correct for a in by_item.get(e.item.id, [])) for e in rows)
        times = [a.seconds for e in rows for a in by_item.get(e.item.id, [])]
        areas.append(
            {
                "area": area,
                "weight": float(area.weight),
                "p": sum(e.p for e in rows) / len(rows) if rows else GUESS,
                "n": n,
                "accuracy": correct / n if n else None,
                "median_minutes": statistics.median(times) / 60 if times else None,
                "items": rows,
            }
        )

    return Estimate(
        zone=zone,
        zone_reason=reason,
        low=low if zone != Zone.NONE else None,
        mid=mid if zone != Zone.NONE else None,
        high=high if zone != Zone.NONE else None,
        topic_score=topic,
        sim_scores=sim_scores,
        coverage_practicing=cov_prac,
        coverage_introduced=cov_intro,
        coverage_proficient=cov_prof,
        evidence=evidence,
        items=item_est,
        areas=areas,
        median_pace=median_pace,
        diagnostic_done=diagnostic_done,
    )


def snapshot(student, est):
    """Store today's estimate, with item levels for week-over-week changes."""
    snap, _ = ReadinessSnapshot.objects.update_or_create(
        student=student,
        taken_on=timezone.localdate(),
        defaults={
            "zone": est.zone,
            "low": est.low,
            "mid": est.mid,
            "high": est.high,
            "coverage": est.coverage_practicing,
            "evidence": est.evidence,
            "details": {
                "topic_score": est.topic_score,
                "levels": {e.item.code: e.level for e in est.items},
            },
        },
    )
    return snap


# --- Priorities and phases ----------------------------------------------------


def priorities(est):
    """Items ordered by what studying them would add: exam weight × room to grow."""
    return sorted(est.items, key=lambda e: e.weight * (1 - e.p), reverse=True)


def focus(est, n=3):
    return [e for e in priorities(est) if e.p < 0.9][:n]


PHASES = [
    ("diagnose", "Diagnose", "Week 1", "Baseline done and personal plan accepted"),
    ("build", "Build", "Weeks 2 to 7", "Every specification item at Practicing or above"),
    ("strengthen", "Strengthen", "Weeks 8 to 10", "80% of exam weight at Proficient, with pace on target"),
    ("simulate", "Simulate", "Weeks 11 to 12", "Readiness estimate in the Ready zone after two simulations"),
    ("taper", "Taper", "Final week", ""),
]


def gates(student, est):
    profile = StudentProfile.objects.filter(user=student).first()
    pace_ok = est.median_pace is not None and est.median_pace <= mastery_rules.pace_seconds()
    return [
        est.diagnostic_done and bool(profile and profile.plan_accepted_at),
        all(e.level >= LevelChoices.PRACTICING for e in est.items),
        est.coverage_proficient >= 0.8 and pace_ok,
        est.zone == Zone.READY,
    ]


def phase_status(student, est):
    """The five phases with their gates, and which one the student is in."""
    met = gates(student, est)
    current = next((i for i, ok in enumerate(met) if not ok), len(met))
    out = []
    for i, (key, name, weeks, gate) in enumerate(PHASES):
        out.append(
            {
                "key": key,
                "name": name,
                "weeks": weeks,
                "gate": gate,
                "gate_met": met[i] if i < len(met) else None,
                "state": "done" if i < current else ("current" if i == current else "upcoming"),
                "number": i + 1,
            }
        )
    return out, PHASES[current][0]
