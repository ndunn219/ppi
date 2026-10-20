"""Mastery levels, spaced review and error replay.

The rules are the design plan's, with its thresholds kept as constants so
they can be tuned once real results come in:

* Practicing: at least 4 recent attempts, at least 50% correct.
* Proficient: the last 5 attempts at least 80% correct, spread over two
  or more days, with no more than one hinted attempt.
* Exam-ready: Proficient, plus median time on pace, the right reference
  used, and the last 5 spanning 7 days or more with the latest correct.
* A level above Introduced drops one step while its spaced review is
  overdue.

Only problem attempts count. Watching and reading never raise a level.
"""

import statistics
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from curriculum.models import SpecItem

from .models import Attempt, CardReview, ErrorReplay, ItemReview, LessonProgress, LevelChoices, Mastery

PRACTICING_MIN, PRACTICING_ACC = 4, 0.5
PROFICIENT_N, PROFICIENT_ACC = 5, 0.8
READY_SPAN_DAYS = 7
LOOKUP_RATE = 0.8


def pace_seconds():
    return settings.COURSE["PACE_TARGET_MINUTES"] * 60


def weighted_accuracy(attempts):
    total = sum(a.weight for a in attempts)
    if not total:
        return None
    return sum(a.weight for a in attempts if a.is_correct) / total


def lookup_rate(student, item, recent):
    """Share of recent evidence where the right reference was used."""
    cited = [a.cited_correct for a in recent if a.cited_correct is not None]
    drills = list(
        Attempt.objects.filter(student=student, spec_item=item, kind=Attempt.Kind.LOOKUP).values_list("is_correct", flat=True)[:6]
    )
    evidence = cited + drills
    if not evidence:
        return None
    return sum(evidence) / len(evidence)


def evaluate(student, item, attempts, lesson_done, review):
    """Return (earned level, decayed level, stats) for one item.

    `attempts` are this item's problem attempts, newest first.
    """
    stats = {"accuracy": weighted_accuracy(attempts[:8]), "counted": sum(a.weight for a in attempts[:8])}
    last5 = attempts[:PROFICIENT_N]
    stats["median_seconds"] = statistics.median(a.seconds for a in last5) if last5 else None
    stats["lookup_rate"] = lookup_rate(student, item, last5) if last5 else None

    level = LevelChoices.NOT_STARTED
    if lesson_done or attempts:
        level = LevelChoices.INTRODUCED
    recent = attempts[:8]
    if len(recent) >= PRACTICING_MIN and (weighted_accuracy(recent) or 0) >= PRACTICING_ACC:
        level = LevelChoices.PRACTICING
    if len(last5) == PROFICIENT_N:
        days = {timezone.localtime(a.created_at).date() for a in last5}
        hinted = sum(1 for a in last5 if a.hint_used)
        if (weighted_accuracy(last5) or 0) >= PROFICIENT_ACC and len(days) >= 2 and hinted <= 1:
            level = LevelChoices.PROFICIENT
            span = last5[0].created_at - last5[-1].created_at
            on_pace = stats["median_seconds"] <= pace_seconds()
            looked_up = (stats["lookup_rate"] or 0) >= LOOKUP_RATE
            if on_pace and looked_up and span >= timedelta(days=READY_SPAN_DAYS) and last5[0].is_correct:
                level = LevelChoices.EXAM_READY

    shown = level
    decayed = False
    if level >= LevelChoices.PRACTICING and review and review.due < timezone.localdate():
        shown = level - 1
        decayed = True
    return level, shown, decayed, stats


def recompute(student, items=None):
    """Recompute and store mastery for a student's items. Returns {item_id: Mastery}."""
    items = list(items or SpecItem.objects.all())
    reviews = {r.spec_item_id: r for r in ItemReview.objects.filter(student=student)}
    done = set(
        LessonProgress.objects.filter(student=student, stage=LessonProgress.Stage.DONE).values_list("spec_item_id", flat=True)
    )
    by_item = {}
    for a in Attempt.objects.filter(student=student, kind=Attempt.Kind.PROBLEM, counts_for_mastery=True).order_by("-created_at"):
        by_item.setdefault(a.spec_item_id, []).append(a)
    out = {}
    with transaction.atomic():
        for item in items:
            earned, shown, decayed, stats = evaluate(student, item, by_item.get(item.id, []), item.id in done, reviews.get(item.id))
            m, _ = Mastery.objects.update_or_create(
                student=student,
                spec_item=item,
                defaults={
                    "level": shown,
                    "earned_level": earned,
                    "decayed": decayed,
                    "accuracy": stats["accuracy"],
                    "attempts_counted": stats["counted"],
                    "median_seconds": stats["median_seconds"],
                    "lookup_rate": stats["lookup_rate"],
                },
            )
            out[item.id] = m
    return out


def levels(student):
    """{item_id: Mastery} without recomputing; fills gaps with a recompute."""
    found = {m.spec_item_id: m for m in Mastery.objects.filter(student=student)}
    if len(found) < SpecItem.objects.count():
        return recompute(student)
    return found


# --- Spaced review ------------------------------------------------------------


def schedule_item(student, item, correct, when=None):
    """Move an item along the 1, 3, 7, 14, 30-day ladder.

    A correct answer only climbs a rung when the review was due, so a
    cramming session can't push an item out to 30 days in one evening.
    """
    when = when or timezone.now()
    today = timezone.localdate(when)
    review, created = ItemReview.objects.get_or_create(
        student=student, spec_item=item, defaults={"due": today + timedelta(days=1), "rung": 0}
    )
    if created and correct:
        review.last_result = True
    elif correct:
        if review.due <= today:
            review.rung = min(review.rung + 1, len(ItemReview.LADDER) - 1)
            review.due = today + timedelta(days=ItemReview.LADDER[review.rung])
        review.last_result = True
    else:
        review.rung = 0
        review.due = today + timedelta(days=1)
        review.last_result = False
    review.last_reviewed = when
    review.save()
    return review


GRADES = {"again": 0, "hard": 3, "good": 4, "easy": 5}


def review_card(review: CardReview, grade_name, when=None):
    """SM-2: update ease and interval from a 0–5 grade."""
    when = when or timezone.now()
    q = GRADES[grade_name]
    if q < 3:
        review.reps = 0
        review.lapses += 1
        review.interval_days = 1
    else:
        review.reps += 1
        if review.reps == 1:
            review.interval_days = 1
        elif review.reps == 2:
            review.interval_days = 3 if q < 5 else 4
        else:
            review.interval_days = max(1, round(review.interval_days * review.ease * (1.2 if q == 5 else 1.0)))
        review.ease = max(1.3, review.ease + 0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    review.due = timezone.localdate(when) + timedelta(days=review.interval_days)
    review.last_reviewed = when
    review.save()
    return review


def ensure_cards(student, items):
    """Start spaced review for the cards of items the student has reached."""
    from curriculum.models import Card

    have = set(CardReview.objects.filter(student=student).values_list("card_id", flat=True))
    new = [CardReview(student=student, card=c) for c in Card.objects.filter(spec_item__in=items) if c.id not in have]
    CardReview.objects.bulk_create(new)


# --- Error replay -------------------------------------------------------------


def track_replay(student, template, correct, cause=""):
    replay = ErrorReplay.objects.filter(student=student, template=template, closed_at__isnull=True).first()
    if correct and replay:
        replay.solved += 1
        if replay.solved >= ErrorReplay.REQUIRED:
            replay.closed_at = timezone.now()
        replay.save()
    elif not correct and not replay:
        ErrorReplay.objects.create(student=student, template=template, cause=cause)
    elif not correct and replay:
        replay.solved = 0
        replay.cause = cause or replay.cause
        replay.save()
