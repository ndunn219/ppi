"""The personal plan: topics in priority order, scheduled into weeks.

A proposal is computed live from the readiness estimate. Accepting it
saves a schedule (StudentProfile.plan) with a target week for every topic
not yet done, so the student can see whether they are on track. Re-planning
rebuilds the schedule from today with the same rules; it never touches
mastery, attempts or reviews.

70% of weekly hours go to topics; the rest is for simulations, warm-ups
and review.
"""

import math
from datetime import timedelta

from django.utils import timezone

from reports import readiness

from .models import LessonProgress, LevelChoices

TOPIC_SHARE = 0.7
DEFAULT_WEEKS = 13


def weeks_left(profile, today=None):
    today = today or timezone.localdate()
    if profile.exam_date and profile.exam_date > today:
        return max(1, math.ceil((profile.exam_date - today).days / 7))
    return DEFAULT_WEEKS


def topic_done(level, lesson_done):
    return lesson_done and level >= LevelChoices.PRACTICING


def proposal(user, profile, est=None, today=None):
    """Rows in priority order with suggested hours and a target week."""
    today = today or timezone.localdate()
    est = est or readiness.estimate(user)
    ranked = readiness.priorities(est)
    lessons_done = set(
        LessonProgress.objects.filter(student=user, stage=LessonProgress.Stage.DONE).values_list("spec_item_id", flat=True)
    )
    weeks = weeks_left(profile, today)
    weekly_topic_hours = max(profile.hours_per_week * TOPIC_SHARE, 0.5)
    study_hours = weeks * weekly_topic_hours
    todo = [e for e in ranked if not topic_done(e.level, e.item.id in lessons_done)]
    score = sum(e.weight * (1 - e.p) for e in todo) or 1
    rows, cumulative = [], 0.0
    for i, e in enumerate(ranked):
        done = e not in todo
        exact = 0 if done else study_hours * e.weight * (1 - e.p) / score
        hours = round(exact, 1)
        week = None
        if not done:
            cumulative += exact
            week = min(weeks, max(1, math.ceil(cumulative / weekly_topic_hours - 1e-9)))
        rows.append({"e": e, "rank": i + 1, "hours": hours, "done": done, "week": week,
                     "due": today + timedelta(days=7 * week - 1) if week else None})
    return {
        "rows": rows,
        "weeks": weeks,
        "total_hours": weeks * profile.hours_per_week,
        "study_hours": round(study_hours),
        "est": est,
    }


def snapshot(prop, today=None):
    today = today or timezone.localdate()
    return {
        "start": today.isoformat(),
        "weeks": prop["weeks"],
        "rows": [
            {"code": r["e"].item.code, "hours": r["hours"], "week": r["week"], "due": r["due"].isoformat() if r["due"] else None}
            for r in prop["rows"]
        ],
    }


def save(profile, user, reason="accepted", today=None):
    prop = proposal(user, profile, today=today)
    profile.plan = snapshot(prop, today) | {"reason": reason}
    if not profile.plan_accepted_at:
        profile.plan_accepted_at = timezone.now()
    profile.save(update_fields=["plan", "plan_accepted_at"])
    return prop


def progress(user, profile, est=None, today=None):
    """The saved schedule with each topic's status, and an on-track summary."""
    from datetime import date

    today = today or timezone.localdate()
    plan = profile.plan or {}
    if not plan.get("rows"):
        return None
    est = est or readiness.estimate(user)
    by_code = {e.item.code: e for e in est.items}
    lessons_done = set(
        LessonProgress.objects.filter(student=user, stage=LessonProgress.Stage.DONE).values_list("spec_item__code", flat=True)
    )
    rows, overdue, due_so_far, done_count = [], 0, 0, 0
    for r in plan["rows"]:
        e = by_code.get(r["code"])
        if e is None:
            continue
        done = topic_done(e.level, r["code"] in lessons_done)
        due = date.fromisoformat(r["due"]) if r.get("due") else None
        if due and due < today:
            due_so_far += 1
        state = "done" if done else ("overdue" if due and due < today else ("this_week" if due and due <= today + timedelta(days=6) else "upcoming"))
        if state == "overdue":
            overdue += 1
        done_count += done
        rows.append({"e": e, "hours": r["hours"], "week": r["week"], "due": due, "state": state, "was_done": r.get("due") is None})
    start = date.fromisoformat(plan["start"])
    week_now = max(1, (today - start).days // 7 + 1)
    return {
        "rows": rows,
        "start": start,
        "week_now": week_now,
        "weeks": plan.get("weeks"),
        "overdue": overdue,
        "done": done_count,
        "on_track": overdue == 0,
        "reason": plan.get("reason", "accepted"),
    }
