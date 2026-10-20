"""Building practice sessions and scoring their answers.

A session's `items` is a list of question descriptors, one per position:

    {"type": "problem", "instance": 12, "item": 3}
    {"type": "problem", "instance": 12, "item": 3, "estimate": [...buckets]}
    {"type": "lookup", "drill": 4, "item": 3, "options": ["…", …]}
    {"type": "method", "instance": 12, "item": 3, "options": [{"item": 3, "label": "…"}, …]}
    {"type": "spot_error", "instance": 12, "item": 3, "flaw": 2}
    {"type": "units", "q": {...}}

Every answer becomes an Attempt; problem attempts then move mastery,
spaced review and error replay.
"""

import random
from datetime import timedelta

from django.conf import settings
from django.db.models import Count
from django.utils import timezone

from curriculum.generation import draw, estimate_buckets, units_question
from curriculum.models import ErrorCause, LookupDrill, ProblemTemplate, Reference, SpecItem

from . import mastery
from .models import Attempt, ErrorReplay, ItemReview, PracticeSession, ProblemInstance

Kind = PracticeSession.Kind


def new_instance(template, rng=None):
    d = draw(template, rng)
    return ProblemInstance.objects.create(
        template=template,
        params=d["params"],
        stem=d["stem"],
        answer=d["answer"],
        answer_label=d["answer_label"],
        choices=d["choices"],
        steps=d["steps"],
    )


def active_templates(items=None):
    qs = ProblemTemplate.objects.filter(is_active=True).select_related("spec_item")
    if items is not None:
        qs = qs.filter(spec_item__in=items)
    return list(qs)


def problem(template, rng, **extra):
    inst = new_instance(template, rng)
    return {"type": "problem", "instance": inst.id, "item": template.spec_item_id, **extra}


def spread(templates, n, rng):
    """n templates, cycling through every one before repeating any."""
    out = []
    while len(out) < n and templates:
        batch = templates[:]
        rng.shuffle(batch)
        out.extend(batch)
    return out[:n]


def mixed_problems(n, rng, items=None):
    return [problem(t, rng) for t in spread(active_templates(items), n, rng)]


def lookup_item(drill, rng):
    options = [drill.answer, drill.wrong_1, drill.wrong_2, drill.wrong_3]
    rng.shuffle(options)
    return {"type": "lookup", "drill": drill.id, "item": drill.spec_item_id, "options": options}


def method_item(template, rng):
    inst = new_instance(template, rng)
    others = list(SpecItem.objects.exclude(id=template.spec_item_id).exclude(method_name=template.spec_item.method_name))
    picks = rng.sample(others, 3) + [template.spec_item]
    rng.shuffle(picks)
    return {
        "type": "method",
        "instance": inst.id,
        "item": template.spec_item_id,
        "options": [{"item": s.id, "label": s.method_name} for s in picks],
    }


def spot_error_item(template, rng):
    inst = new_instance(template, rng)
    flawed = [i for i, s in enumerate(inst.steps) if s.get("wrong")]
    if not flawed:
        return None
    return {"type": "spot_error", "instance": inst.id, "item": template.spec_item_id, "flaw": rng.choice(flawed)}


def build(student, kind, item=None, rng=None):
    """Create a session of `kind`, optionally limited to one spec item."""
    rng = rng or random.Random()
    cfg = settings.COURSE
    pace = cfg["PACE_TARGET_MINUTES"] * 60
    items_scope = [item] if item else None
    questions, limit = [], None

    if kind == Kind.DIAGNOSTIC:
        for it in SpecItem.objects.all():
            for t in spread(active_templates([it]), cfg["DIAGNOSTIC_PER_ITEM"], rng):
                questions.append(problem(t, rng))
        rng.shuffle(questions)
        drills = list(LookupDrill.objects.all())
        questions += [lookup_item(d, rng) for d in rng.sample(drills, min(6, len(drills)))]
        limit = int(len(questions) * pace)
    elif kind == Kind.DRILL:
        templates = active_templates(items_scope)
        t = rng.choice(templates)
        questions = [problem(t, rng) for _ in range(4)]
    elif kind == Kind.WARMUP:
        due = ItemReview.objects.filter(student=student, due__lte=timezone.localdate()).select_related("spec_item")[:8]
        for r in due:
            ts = active_templates([r.spec_item])
            if ts:
                questions.append(problem(rng.choice(ts), rng))
    elif kind == Kind.LOOKUP:
        drills = list(LookupDrill.objects.filter(spec_item=item) if item else LookupDrill.objects.all())
        questions = [lookup_item(d, rng) for d in rng.sample(drills, min(8, len(drills)))]
    elif kind == Kind.METHOD:
        questions = [method_item(t, rng) for t in spread(active_templates(), 8, rng)]
    elif kind == Kind.ESTIMATE:
        for t in spread(active_templates(items_scope), 5, rng):
            q = problem(t, rng)
            inst = ProblemInstance.objects.get(id=q["instance"])
            q["estimate"] = estimate_buckets(inst.answer, rng)
            questions.append(q)
    elif kind == Kind.SPOT_ERROR:
        for t in spread(active_templates(items_scope), 10, rng):
            q = spot_error_item(t, rng)
            if q:
                questions.append(q)
            if len(questions) == 5:
                break
    elif kind == Kind.REPLAY:
        open_replays = ErrorReplay.objects.filter(student=student, closed_at__isnull=True).select_related("template")[:6]
        questions = [problem(r.template, rng) for r in open_replays]
    elif kind == Kind.UNITS:
        questions = [{"type": "units", "q": units_question(rng)} for _ in range(10)]
    elif kind == Kind.TIMED_BLOCK:
        questions = mixed_problems(cfg["TIMED_BLOCK_SIZE"], rng, items_scope)
        limit = int(len(questions) * pace)
    elif kind == Kind.HALF_EXAM:
        questions = mixed_problems(cfg["HALF_EXAM_SIZE"], rng)
        limit = int(len(questions) * pace)
    elif kind == Kind.FULL_EXAM:
        questions = mixed_problems(cfg["FULL_EXAM_SIZE"], rng)
        limit = int(len(questions) * pace)
    else:
        raise ValueError(kind)

    if not questions:
        return None
    return PracticeSession.objects.create(student=student, kind=kind, spec_item=item, items=questions, time_limit_seconds=limit)


# --- Scoring ------------------------------------------------------------------


def references():
    return list(Reference.objects.all())


def record(session, position, data, seconds, student):
    """Score one answer and store it as an Attempt (updating it on revisit).

    `data` is the submitted form. Returns the Attempt.
    """
    q = session.items[position]
    kind = q["type"]
    existing = Attempt.objects.filter(session=session, position=position).first()
    att = existing or Attempt(student=student, session=session, position=position)
    att.seconds = (existing.seconds if existing else 0) + max(0, int(seconds or 0))
    att.created_at = timezone.now()
    att.counts_for_mastery = True
    item_id = q.get("item")
    att.spec_item_id = item_id

    if kind in ("problem", "method", "spot_error"):
        inst = ProblemInstance.objects.select_related("template").get(id=q["instance"])
        att.instance = inst

    if kind == "problem":
        att.kind = Attempt.Kind.PROBLEM
        idx = data.get("choice")
        if idx in (None, ""):
            att.response, att.is_correct, att.cause = "", False, ""
        else:
            choice = inst.choices[int(idx)]
            att.response = choice["label"]
            att.is_correct = not choice["cause"]
            att.cause = choice["cause"]
        att.hint_used = bool(data.get("hint_used")) and not session.is_exam_style
        cited = data.get("cited_reference", "")
        att.cited_reference = cited
        if cited:
            valid = set(inst.template.spec_item.locations.values_list("reference__short_name", flat=True))
            att.cited_correct = cited in valid
        if "estimate" in q and data.get("estimate") not in (None, ""):
            b = q["estimate"][int(data["estimate"])]
            att.extra = {**att.extra, "estimate_correct": b["correct"]}
    elif kind == "lookup":
        drill = LookupDrill.objects.get(id=q["drill"])
        att.kind = Attempt.Kind.LOOKUP
        att.lookup_drill = drill
        pick = data.get("choice")
        att.response = q["options"][int(pick)] if pick not in (None, "") else ""
        att.is_correct = att.response == drill.answer
        att.cause = "" if att.is_correct else ErrorCause.LOOKUP
        att.counts_for_mastery = False
    elif kind == "method":
        att.kind = Attempt.Kind.METHOD
        pick = data.get("choice")
        chosen = q["options"][int(pick)] if pick not in (None, "") else None
        att.response = chosen["label"] if chosen else ""
        att.is_correct = bool(chosen) and chosen["item"] == item_id
        att.cause = "" if att.is_correct else ErrorCause.METHOD
        att.counts_for_mastery = False
    elif kind == "spot_error":
        att.kind = Attempt.Kind.SPOT_ERROR
        pick = data.get("choice")
        att.response = str(pick)
        att.is_correct = pick not in (None, "") and int(pick) == q["flaw"]
        att.cause = "" if att.is_correct else ErrorCause.CONCEPT
        att.counts_for_mastery = False
    elif kind == "units":
        att.kind = Attempt.Kind.UNITS
        uq = q["q"]
        att.response = (data.get("value") or "").replace(",", "").strip()
        try:
            v = float(att.response)
            tol = max(abs(uq["answer"]) * 0.01, 10 ** -uq["decimals"])
            att.is_correct = abs(v - uq["answer"]) <= tol
        except ValueError:
            att.is_correct = False
        att.cause = "" if att.is_correct else ErrorCause.UNITS
        att.counts_for_mastery = False
    att.save()

    # In exam-style sessions the effects wait for the finish, when every
    # answer is final; practice answers take effect at once.
    if not session.is_exam_style:
        apply_effects(att)
    return att


def apply_effects(att):
    if att.kind == Attempt.Kind.PROBLEM and att.spec_item_id:
        mastery.schedule_item(att.student, att.spec_item, att.is_correct, att.created_at)
        if att.instance_id:
            mastery.track_replay(att.student, att.instance.template, att.is_correct, att.cause)
        mastery.recompute(att.student, [att.spec_item])


def finish(session):
    """Close a session; for exam-style ones, score unanswered questions and apply effects."""
    if session.finished_at:
        return session
    session.finished_at = timezone.now()
    session.save(update_fields=["finished_at"])
    if session.is_exam_style:
        answered = set(session.attempts.values_list("position", flat=True))
        for pos, q in enumerate(session.items):
            if pos in answered:
                continue
            record(session, pos, {}, 0, session.student)
        touched = set()
        for att in session.attempts.select_related("instance__template", "spec_item"):
            if att.kind != Attempt.Kind.PROBLEM:
                continue
            if att.response:
                mastery.schedule_item(att.student, att.spec_item, att.is_correct, att.created_at)
                mastery.track_replay(att.student, att.instance.template, att.is_correct, att.cause)
            touched.add(att.spec_item_id)
        mastery.recompute(session.student, SpecItem.objects.filter(id__in=touched))
        if session.kind == Kind.DIAGNOSTIC:
            mastery.ensure_cards(session.student, SpecItem.objects.all())
    return session


def results(session):
    attempts = list(session.attempts.select_related("spec_item__area", "instance"))
    total = len(session.items)
    correct = sum(a.is_correct for a in attempts)
    by_cause = (
        session.attempts.exclude(cause="").values("cause").annotate(n=Count("id")).order_by("-n")
    )
    by_area = {}
    for a in attempts:
        if not a.spec_item_id:
            continue
        row = by_area.setdefault(a.spec_item.area, {"n": 0, "correct": 0, "seconds": 0})
        row["n"] += 1
        row["correct"] += a.is_correct
        row["seconds"] += a.seconds
    return {
        "total": total,
        "correct": correct,
        "score": correct / total if total else 0,
        "seconds": sum(a.seconds for a in attempts),
        "attempts": sorted(attempts, key=lambda a: a.position or 0),
        "by_cause": [{"cause": ErrorCause(r["cause"]).label, "key": r["cause"], "n": r["n"]} for r in by_cause],
        "by_area": [
            {"area": area, **row, "accuracy": row["correct"] / row["n"], "minutes": row["seconds"] / row["n"] / 60}
            for area, row in sorted(by_area.items(), key=lambda kv: kv[0].order)
        ],
    }


FIXES = {
    "lookup": ("Lookup sprint", Kind.LOOKUP, "Practice finding the right reference fast."),
    "units": ("Units drill", Kind.UNITS, "Ten quick conversions."),
    "method": ("Which method?", Kind.METHOD, "Practice recognizing problem types."),
    "setup": ("Parametric drill", Kind.DRILL, "The same problem type with new numbers."),
    "arithmetic": ("Estimate first", Kind.ESTIMATE, "Pick a range before solving to catch slips."),
    "concept": ("Spot the error", Kind.SPOT_ERROR, "Find the mistake in a flawed solution."),
    "misread": ("Parametric drill", Kind.DRILL, "Slow down on the stem: underline what is asked."),
}


def fix_for(cause):
    return FIXES.get(cause)


def stale_cutoff():
    return timezone.now() - timedelta(days=1)
