"""Report contents as plain data, so a shared link can keep a snapshot.

Everything here comes from attempts the student made in the course. The
study record (hours, streaks) is context only and is listed last.
"""

import statistics
from datetime import timedelta

from django.conf import settings
from django.db.models import Count
from django.utils import timezone

from curriculum.models import ErrorCause, SpecArea
from learning import mastery, sessions
from learning.models import Attempt, CardReview, LessonProgress, PracticeSession

from . import readiness
from .models import ReadinessSnapshot

LEVEL_NAMES = ["Not started", "Introduced", "Practicing", "Proficient", "Exam-ready"]


def _r(x, d=3):
    return None if x is None else round(float(x), d)


def trend(student, days=90):
    since = timezone.localdate() - timedelta(days=days)
    snaps = ReadinessSnapshot.objects.filter(student=student, taken_on__gte=since).order_by("taken_on")
    return [
        {"date": s.taken_on.isoformat(), "low": s.low, "mid": s.mid, "high": s.high, "coverage": s.coverage}
        for s in snaps
    ]


def readiness_report(student):
    levels = mastery.recompute(student)
    est = readiness.estimate(student, levels)
    readiness.snapshot(student, est)
    attempts = list(Attempt.objects.filter(student=student, kind=Attempt.Kind.PROBLEM, counts_for_mastery=True))

    coverage = []
    for a in est.areas:
        coverage.append(
            {
                "area": a["area"].name,
                "weight": a["weight"],
                "items": [
                    {
                        "code": e.item.code,
                        "name": e.item.name,
                        "level": e.level,
                        "level_name": LEVEL_NAMES[e.level],
                        "decayed": bool(levels.get(e.item.id) and levels[e.item.id].decayed),
                    }
                    for e in a["items"]
                ],
            }
        )

    cited = [a.cited_correct for a in attempts if a.cited_correct is not None]
    drills = list(Attempt.objects.filter(student=student, kind=Attempt.Kind.LOOKUP))
    now = timezone.now()
    recent_cut = now - timedelta(days=14)
    errors = []
    for cause, label in ErrorCause.choices:
        recent = sum(1 for a in attempts if a.cause == cause and a.created_at >= recent_cut)
        earlier = sum(1 for a in attempts if a.cause == cause and a.created_at < recent_cut)
        if recent or earlier:
            errors.append({"cause": label, "recent": recent, "earlier": earlier})

    sims = []
    for s, score in est.sim_scores:
        sims.append({"date": s.finished_at.date().isoformat(), "kind": "Full", "score": _r(score), "questions": len(s.items), "id": s.id})
    for s in readiness.finished_sims(student, PracticeSession.Kind.HALF_EXAM):
        sims.append({"date": s.finished_at.date().isoformat(), "kind": "Half", "score": _r(readiness.session_score(s)), "questions": len(s.items), "id": s.id})
    sims.sort(key=lambda r: r["date"], reverse=True)

    all_attempts = Attempt.objects.filter(student=student)
    days = sorted({timezone.localtime(t).date() for t in all_attempts.values_list("created_at", flat=True)})
    streak = 0
    day = timezone.localdate()
    dayset = set(days)
    while day in dayset:
        streak += 1
        day -= timedelta(days=1)
    lessons = LessonProgress.objects.filter(student=student, stage=LessonProgress.Stage.DONE)
    lesson_minutes = sum(lp.spec_item.lesson.minutes for lp in lessons.select_related("spec_item__lesson") if hasattr(lp.spec_item, "lesson"))
    seconds = sum(all_attempts.values_list("seconds", flat=True))

    return {
        "generated": now.isoformat(),
        "student": student.get_full_name() or student.get_username(),
        "estimate": {
            "zone": est.zone,
            "zone_label": est.zone_label,
            "reason": est.zone_reason,
            "low": _r(est.low),
            "mid": _r(est.mid),
            "high": _r(est.high),
            "target": est.target,
            "evidence": est.evidence,
            "full_sims": len(est.sim_scores),
            "topic_score": _r(est.topic_score),
        },
        "coverage": coverage,
        "coverage_practicing": _r(est.coverage_practicing),
        "coverage_proficient": _r(est.coverage_proficient),
        "accuracy": [{"area": a["area"].name, "n": a["n"], "accuracy": _r(a["accuracy"])} for a in est.areas],
        "pace": [{"area": a["area"].name, "minutes": _r(a["median_minutes"], 1), "n": a["n"]} for a in est.areas],
        "pace_target": settings.COURSE["PACE_TARGET_MINUTES"],
        "lookup": {
            "cited_rate": _r(sum(cited) / len(cited)) if cited else None,
            "cited_n": len(cited),
            "drill_rate": _r(sum(a.is_correct for a in drills) / len(drills)) if drills else None,
            "drill_n": len(drills),
            "drill_seconds": _r(statistics.median(a.seconds for a in drills), 0) if drills else None,
        },
        "errors": errors,
        "simulations": sims,
        "study": {
            "active_days": len(days),
            "streak": streak,
            "hours": _r((seconds / 60 + lesson_minutes) / 60, 1),
            "attempts": all_attempts.count(),
            "lessons_done": lessons.count(),
            "cards_learned": CardReview.objects.filter(student=student, reps__gte=2).count(),
        },
        "focus": [
            {"code": e.item.code, "name": e.item.name, "p": _r(e.p), "weight": _r(e.weight)} for e in readiness.focus(est)
        ],
        "trend": trend(student),
    }


def weekly_report(student, today=None):
    today = today or timezone.localdate()
    start = today - timedelta(days=6)
    prev_start = start - timedelta(days=7)

    def window(a, b):
        qs = Attempt.objects.filter(student=student, created_at__date__gte=a, created_at__date__lte=b)
        problems = qs.filter(kind=Attempt.Kind.PROBLEM)
        n = problems.count()
        return {
            "attempts": qs.count(),
            "problems": n,
            "accuracy": _r(problems.filter(is_correct=True).count() / n) if n else None,
            "minutes": round(sum(qs.values_list("seconds", flat=True)) / 60),
            "days": len({timezone.localtime(t).date() for t in qs.values_list("created_at", flat=True)}),
        }

    this_week = window(start, today)
    last_week = window(prev_start, start - timedelta(days=1))
    report = readiness_report(student)
    now_levels = {i["code"]: (i["level"], i["name"]) for area in report["coverage"] for i in area["items"]}
    then = ReadinessSnapshot.objects.filter(student=student, taken_on__lte=start).order_by("-taken_on").first()
    then_levels = then.details.get("levels", {}) if then else {}
    moved, slipped = [], []
    for code, (lvl, name) in now_levels.items():
        before = then_levels.get(code, 0)
        if lvl > before:
            moved.append({"code": code, "name": name, "from": LEVEL_NAMES[before], "to": LEVEL_NAMES[lvl]})
        elif lvl < before:
            slipped.append({"code": code, "name": name, "from": LEVEL_NAMES[before], "to": LEVEL_NAMES[lvl]})
    causes = (
        Attempt.objects.filter(student=student, created_at__date__gte=start).exclude(cause="").values("cause").annotate(n=Count("id")).order_by("-n")
    )
    return {
        "generated": timezone.now().isoformat(),
        "student": report["student"],
        "start": start.isoformat(),
        "end": today.isoformat(),
        "this_week": this_week,
        "last_week": last_week,
        "moved": moved,
        "slipped": slipped,
        "causes": [{"cause": ErrorCause(c["cause"]).label, "n": c["n"]} for c in causes],
        "estimate": report["estimate"],
        "focus": report["focus"],
        "cards_reviewed": CardReview.objects.filter(student=student, last_reviewed__date__gte=start).count(),
    }


def simulation_report(session):
    r = sessions.results(session)
    pace = settings.COURSE["PACE_TARGET_MINUTES"]
    cumulative, total = [], 0
    for a in r["attempts"]:
        total += a.seconds / 60
        cumulative.append(round(total, 1))
    return {
        "generated": timezone.now().isoformat(),
        "student": session.student.get_full_name() or session.student.get_username(),
        "kind": session.get_kind_display(),
        "date": (session.finished_at or session.started_at).date().isoformat(),
        "score": _r(r["score"]),
        "correct": r["correct"],
        "total": r["total"],
        "minutes": round(r["seconds"] / 60),
        "limit_minutes": round((session.time_limit_seconds or 0) / 60),
        "pace_target": pace,
        "by_area": [
            {"area": row["area"].name, "n": row["n"], "accuracy": _r(row["accuracy"]), "minutes": _r(row["minutes"], 1)}
            for row in r["by_area"]
        ],
        "by_cause": [{"cause": c["cause"], "n": c["n"]} for c in r["by_cause"]],
        "cumulative": cumulative,
        "unanswered": sum(1 for a in r["attempts"] if not a.response),
    }


def areas():
    return list(SpecArea.objects.order_by("order"))
