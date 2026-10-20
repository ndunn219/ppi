"""Practice pages: the hub, the question runner, the lesson loop, cards,
the error journal, and the tutor's audits."""

import json
import random

from django.conf import settings
from django.contrib.staticfiles import finders
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from curriculum.models import ErrorCause, LookupDrill, ProblemTemplate, Reference, SpecItem

from . import mastery, sessions, tutor
from .models import Attempt, CardReview, ErrorReplay, LessonProgress, PracticeSession, ProblemInstance
from .views import needs_profile

Kind = PracticeSession.Kind

MODES = [
    ("Every day", [
        (Kind.WARMUP, "i-bolt", "", "Daily warm-up", "Topics due for spaced review, one new-number problem each.", "5 to 10 min"),
        (None, "i-cards", "", "Flashcards", "Formulas, variables, when to use each method and where it lives.", "5 min"),
    ]),
    ("Build fluency", [
        (Kind.DRILL, "i-repeat", "", "Parametric drill", "One problem type four times in a row with new numbers.", "10 to 15 min"),
        (Kind.REPLAY, "i-alert", "amber", "Error replay", "Problems you missed come back until you solve them twice.", "10 min"),
        (Kind.UNITS, "i-ruler", "", "Units and conversions", "Ten fast conversions common in transportation problems.", "3 min"),
    ]),
    ("Think like the exam", [
        (Kind.LOOKUP, "i-search", "blue", "Lookup sprint", "Name the reference and section where each value lives, against the clock.", "4 min"),
        (Kind.METHOD, "i-split", "blue", "Which method?", "Read a problem and pick the approach without solving it.", "5 min"),
        (Kind.ESTIMATE, "i-gauge", "blue", "Estimate first", "Pick a plausible range before you solve, then check.", "15 min"),
        (Kind.SPOT_ERROR, "i-bug", "blue", "Spot the error", "Find the wrong step in a worked solution.", "10 min"),
        ("explain", "i-chat", "blue", "Explain it back", "Explain why one step of a method works.", "3 min"),
    ]),
    ("Exam conditions", [
        (Kind.TIMED_BLOCK, "i-timer", "amber", "Mixed timed block", "10 mixed questions at about 6 minutes each, no hints.", "60 min"),
        (Kind.HALF_EXAM, "i-timer", "amber", "Half-exam set", "40 questions in one sitting under exam rules.", "4 hours"),
        (Kind.FULL_EXAM, "i-timer", "amber", "Full exam simulation", "80 questions, on-screen references, dry-erase scratch work.", "8 hours"),
    ]),
]


@needs_profile
def practice(request):
    open_sessions = PracticeSession.objects.filter(student=request.user, finished_at__isnull=True).exclude(kind=Kind.LESSON)[:5]
    return render(
        request,
        "learning/practice.html",
        {"modes": MODES, "items": SpecItem.objects.select_related("area"), "open_sessions": open_sessions},
    )


@require_POST
@needs_profile
def start(request):
    kind = request.POST.get("kind")
    if kind not in Kind.values or kind == Kind.LESSON:
        raise Http404
    code = request.POST.get("item") or None
    item = SpecItem.objects.filter(code=code).first() if code else None
    if kind == Kind.DIAGNOSTIC:
        existing = PracticeSession.objects.filter(student=request.user, kind=kind, finished_at__isnull=True).first()
        if existing:
            return redirect("learning:session", existing.id)
    session = sessions.build(request.user, kind, item)
    if session is None:
        empty = {
            Kind.WARMUP: "Nothing is due for review today. Try a drill instead.",
            Kind.REPLAY: "No open error replays. Missed problems land here.",
        }
        messages.info(request, empty.get(kind, "Nothing to practice here yet."))
        return redirect(request.POST.get("back") or "learning:practice")
    return redirect("learning:session", session.id)


# --- The runner ---------------------------------------------------------------


def question_context(session, position):
    q = session.items[position]
    ctx = {"q": q, "position": position, "number": position + 1, "total": len(session.items)}
    if q["type"] in ("problem", "method", "spot_error"):
        inst = ProblemInstance.objects.select_related("template__spec_item").get(id=q["instance"])
        ctx["instance"] = inst
        ctx["choices"] = inst.choices
    if q["type"] == "spot_error":
        steps = []
        for i, s in enumerate(ctx["instance"].steps):
            steps.append({"text": s["wrong"] if i == q["flaw"] else s["text"], "i": i})
        ctx["flawed_steps"] = steps
    if q["type"] == "lookup":
        ctx["drill"] = LookupDrill.objects.select_related("spec_item").get(id=q["drill"])
    if q["type"] == "units":
        ctx["uq"] = q["q"]
    return ctx


def feedback_context(att, q):
    """What a student sees after answering: the verdict, why, and what to do next."""
    ctx = {"att": att, "fix": sessions.fix_for(att.cause) if not att.is_correct else None}
    if att.instance_id:
        ctx["steps"] = att.instance.steps
        ctx["answer_label"] = att.instance.answer_label
        ctx["template"] = att.instance.template
        if att.kind == Attempt.Kind.PROBLEM and att.response:
            ctx["chosen"] = next((c for c in att.instance.choices if c["label"] == att.response), None)
    if q["type"] == "spot_error":
        ctx["flaw"] = q["flaw"]
        ctx["flaw_step"] = att.instance.steps[q["flaw"]]
    if q["type"] == "lookup":
        ctx["drill"] = att.lookup_drill
    if q["type"] == "estimate" or "estimate" in q:
        ctx["estimate_correct"] = att.extra.get("estimate_correct")
    ctx["tutor_on"] = tutor.enabled()
    ctx["causes"] = ErrorCause.choices
    ctx["self_checks"] = SELF_CHECKS
    return ctx


@needs_profile
def session_view(request, pk):
    session = get_object_or_404(PracticeSession, pk=pk, student=request.user)
    if session.kind == Kind.LESSON:
        return redirect("learning:study", session.spec_item.code)
    deadline = session.deadline()
    if not session.finished_at and deadline and timezone.now() > deadline:
        sessions.finish(session)
        messages.warning(request, "Time is up. Your answers were submitted.")
        return redirect("learning:results", session.id)
    try:
        position = int(request.GET.get("q", 0))
    except ValueError:
        position = 0
    if not 0 <= position < len(session.items):
        position = 0

    answered = {a.position: a for a in session.attempts.select_related("instance__template", "lookup_drill")}
    if session.is_finished and "q" not in request.GET:
        return redirect("learning:results", session.id)
    if not session.is_exam_style and "q" not in request.GET:
        unanswered = [i for i in range(len(session.items)) if i not in answered]
        if not unanswered:
            return redirect("learning:results", session.id)
        position = unanswered[0]

    ctx = {
        "session": session,
        "answered": answered,
        "references": Reference.objects.all(),
        "deadline": deadline,
        "pace_minutes": settings.COURSE["PACE_TARGET_MINUTES"],
        **question_context(session, position),
    }
    att = answered.get(position)
    show_feedback = att is not None and (not session.is_exam_style or session.is_finished)
    ctx["att"] = att
    if show_feedback:
        ctx.update(feedback_context(att, session.items[position]))
        ctx["next_position"] = position + 1 if position + 1 < len(session.items) else None
    ctx["show_feedback"] = show_feedback
    ctx["nav"] = [
        {"i": i, "answered": i in answered, "flagged": i in session.flags, "current": i == position}
        for i in range(len(session.items))
    ]
    return render(request, "learning/session.html", ctx)


@require_POST
@needs_profile
def answer(request, pk):
    session = get_object_or_404(PracticeSession, pk=pk, student=request.user)
    if session.is_finished:
        return redirect("learning:results", session.id)
    position = int(request.POST.get("position", 0))
    action = request.POST.get("action", "answer")
    if action == "flag":
        flags = set(session.flags)
        flags.symmetric_difference_update({position})
        session.flags = sorted(flags)
        session.save(update_fields=["flags"])
        return redirect(f"{reverse('learning:session', args=[session.id])}?q={position}")
    has_answer = any(request.POST.get(k) not in (None, "") for k in ("choice", "value"))
    if has_answer or not session.is_exam_style:
        sessions.record(session, position, request.POST, request.POST.get("seconds"), request.user)
    if session.is_exam_style:
        if action == "finish":
            sessions.finish(session)
            return redirect("learning:results", session.id)
        target = position - 1 if action == "prev" else position + 1
        target = max(0, min(target, len(session.items) - 1))
        return redirect(f"{reverse('learning:session', args=[session.id])}?q={target}")
    return redirect(f"{reverse('learning:session', args=[session.id])}?q={position}")


@require_POST
@needs_profile
def finish(request, pk):
    session = get_object_or_404(PracticeSession, pk=pk, student=request.user)
    sessions.finish(session)
    return redirect("learning:results", session.id)


@needs_profile
def results(request, pk):
    session = get_object_or_404(PracticeSession, pk=pk, student=request.user)
    if not session.is_finished:
        sessions.finish(session)
    r = sessions.results(session)
    fixes = [sessions.fix_for(c["key"]) + (c,) for c in r["by_cause"] if sessions.fix_for(c["key"])]
    return render(request, "learning/results.html", {"session": session, "r": r, "fixes": fixes[:3]})


# --- The lesson loop ----------------------------------------------------------

Stage = LessonProgress.Stage
LOOP = [
    (Stage.PRIME, "Cold try", "One problem before any teaching. A miss is expected: it shows what the lesson is for."),
    (Stage.LEARN, "Tutorial", "The interactive tutorial: explanation, explorers, questions and worked examples."),
    (Stage.FADE, "Worked example", "A full solution, then the same kind of problem with more of the steps left to you."),
    (Stage.TRY, "Try it yourself", "Three problems with new numbers and no hints."),
    (Stage.DONE, "Schedule", "The topic joins spaced review, with your flashcards."),
]
LOOP_ORDER = [key for key, _, _ in LOOP]
TRY_COUNT = 3
TESTOUT_COUNT = 2


def lesson_session(user, item):
    s = PracticeSession.objects.filter(student=user, kind=Kind.LESSON, spec_item=item, finished_at__isnull=True).first()
    return s or PracticeSession.objects.create(student=user, kind=Kind.LESSON, spec_item=item, items=[])


def add_problem(session, item, stage, **extra):
    templates = sessions.active_templates([item])
    used = [q["instance"] for q in session.items]
    used_templates = set(ProblemInstance.objects.filter(id__in=used).values_list("template_id", flat=True))
    fresh = [t for t in templates if t.id not in used_templates] or templates
    q = sessions.problem(random.choice(fresh), random.Random(), stage=stage, **extra)
    session.items = session.items + [q]
    session.save(update_fields=["items"])
    return len(session.items) - 1


@needs_profile
def study(request, code):
    item = get_object_or_404(SpecItem.objects.select_related("area"), code=code)
    lp, _ = LessonProgress.objects.get_or_create(student=request.user, spec_item=item)
    session = lesson_session(request.user, item) if lp.stage != Stage.DONE else None
    if session and lp.stage in (Stage.PRIME, Stage.TESTOUT, Stage.TRY) and not session.items:
        add_problem(session, item, lp.stage)
    if session and lp.stage == Stage.FADE and lp.fade_level > 0 and not [q for q in session.items if q.get("fade") == lp.fade_level]:
        add_problem(session, item, "fade", fade=lp.fade_level)

    ctx = {"item": item, "lp": lp, "session": session, "references": Reference.objects.all()}
    review = request.GET.get("step")
    steps = loop_state(lp, item, review)
    ctx["loop_state"] = steps
    current_key = current_step(lp)
    position_now = LOOP_ORDER.index(current_key)
    ctx["previous_step"] = steps[position_now - 1] if position_now > 0 else None
    allowed = {s["key"] for s in steps if s["url"]}
    if review and review != current_key and review in allowed:
        ctx["review"] = next(s for s in steps if s["key"] == review)
        ctx["current"] = steps[position_now]
        ctx.update(review_context(request.user, item, lp, review))
        return render(request, "learning/study.html", ctx)
    if lp.stage == Stage.DONE:
        ctx["summary"] = lesson_summary(request.user, item)
    elif lp.stage == Stage.LEARN:
        ctx.update(tutorial_context(item))
    elif lp.stage == Stage.FADE and lp.fade_level == 0:
        inst = sessions.new_instance(random.choice(sessions.active_templates([item])))
        ctx["worked"] = inst
    else:
        position = len(session.items) - 1
        ctx.update(question_context(session, position))
        if lp.stage == Stage.FADE:
            shown = len(ctx["instance"].steps) - 1 if lp.fade_level == 1 else 1
            ctx["shown_steps"] = ctx["instance"].steps[:shown]
        att = session.attempts.filter(position=position).select_related("instance__template").first()
        ctx["att"] = att
        if att:
            ctx.update(feedback_context(att, session.items[position]))
        stage_items = [q for q in session.items if q.get("stage") == lp.stage]
        ctx["stage_count"] = len(stage_items)
        ctx["stage_total"] = {Stage.TRY: TRY_COUNT, Stage.TESTOUT: TESTOUT_COUNT}.get(lp.stage, 1)
    return render(request, "learning/study.html", ctx)


def current_step(lp):
    return Stage.PRIME if lp.stage == Stage.TESTOUT else lp.stage


def loop_state(lp, item, viewing=None):
    """The step pills. Finished steps and the current one can be opened;
    the tutorial can always be opened; later steps unlock in order."""
    idx = LOOP_ORDER.index(current_step(lp))
    base = reverse("learning:study", args=[item.code])
    out = []
    for i, (key, label, desc) in enumerate(LOOP):
        state = "done" if i < idx else ("current" if i == idx else "")
        open_ = i <= idx or key == Stage.LEARN
        url = (base if i == idx else f"{base}?step={key}") if open_ else None
        shown = viewing == key if viewing in LOOP_ORDER else i == idx
        out.append({"key": key, "label": label, "desc": desc, "state": state, "url": url, "viewing": shown, "number": i + 1})
    return out


def review_context(user, item, lp, step):
    """A finished step, shown again without changing progress."""
    if step == Stage.LEARN:
        return tutorial_context(item)
    if step == Stage.DONE:
        return {"summary": lesson_summary(user, item)}
    # Every time through the loop, newest first: a redo starts a new lesson
    # session, and the earlier cold try and problems belong in the record too.
    stages = {Stage.PRIME: ("prime", "testout"), Stage.FADE: ("fade",), Stage.TRY: ("try",)}[step]
    answered = []
    runs = list(PracticeSession.objects.filter(student=user, kind=Kind.LESSON, spec_item=item).order_by("-started_at"))
    for run_number, session in zip(range(len(runs), 0, -1), runs):
        attempts = {a.position: a for a in session.attempts.select_related("instance__template")}
        for pos, q in enumerate(session.items):
            if q.get("stage") in stages and pos in attempts:
                att = attempts[pos]
                answered.append({"q": q, "att": att, "instance": att.instance, "chosen": att.response, "run": run_number})
    ctx = {"answered": answered, "runs": len(runs)}
    if step == Stage.FADE:
        ctx["worked"] = sessions.new_instance(random.choice(sessions.active_templates([item])))
    return ctx


@require_POST
@needs_profile
def study_answer(request, code):
    item = get_object_or_404(SpecItem, code=code)
    lp = get_object_or_404(LessonProgress, student=request.user, spec_item=item)
    session = lesson_session(request.user, item)
    position = len(session.items) - 1
    if position < 0 or session.attempts.filter(position=position).exists():
        return redirect("learning:study", code)
    data = request.POST.copy()
    if lp.stage == Stage.FADE:
        data["hint_used"] = "1"  # steps were shown, so half credit
    sessions.record(session, position, data, request.POST.get("seconds"), request.user)
    return redirect("learning:study", code)


@require_POST
@needs_profile
def study_next(request, code):
    """Move the loop forward one step."""
    item = get_object_or_404(SpecItem, code=code)
    lp = get_object_or_404(LessonProgress, student=request.user, spec_item=item)
    session = lesson_session(request.user, item)
    action = request.POST.get("action", "next")
    pace = settings.COURSE["PACE_TARGET_MINUTES"] * 60

    def stage_attempts(stage):
        positions = [i for i, q in enumerate(session.items) if q.get("stage") == stage]
        return list(session.attempts.filter(position__in=positions).order_by("position"))

    if lp.stage == Stage.PRIME:
        if action == "testout":
            lp.stage = Stage.TESTOUT
            lp.save()
            add_problem(session, item, Stage.TESTOUT)
        else:
            lp.stage = Stage.LEARN
            lp.save()
    elif lp.stage == Stage.TESTOUT:
        done = stage_attempts(Stage.TESTOUT)
        if done and (not done[-1].is_correct or done[-1].seconds > pace):
            lp.stage = Stage.LEARN
            lp.save()
            messages.info(request, "Not a test-out this time. The lesson is next.")
        elif len(done) >= TESTOUT_COUNT:
            lp.tested_out = True
            complete(request.user, lp, session)
            messages.success(request, "Tested out. This topic goes straight to spaced review.")
        else:
            add_problem(session, item, Stage.TESTOUT)
    elif lp.stage == Stage.LEARN:
        lp.stage, lp.fade_level = Stage.FADE, 0
        lp.save()
    elif lp.stage == Stage.FADE:
        if lp.fade_level < 2:
            lp.fade_level += 1
            lp.save()
            add_problem(session, item, "fade", fade=lp.fade_level)
        else:
            lp.stage = Stage.TRY
            lp.save()
            add_problem(session, item, Stage.TRY)
    elif lp.stage == Stage.TRY:
        if len(stage_attempts(Stage.TRY)) >= TRY_COUNT:
            complete(request.user, lp, session)
        else:
            add_problem(session, item, Stage.TRY)
    elif lp.stage == Stage.DONE and action == "restart":
        lp.stage, lp.fade_level, lp.completed_at = Stage.LEARN, 0, None
        lp.save()
    return redirect("learning:study", code)


def complete(user, lp, session):
    lp.stage = Stage.DONE
    lp.completed_at = timezone.now()
    lp.save()
    session.finished_at = timezone.now()
    session.save(update_fields=["finished_at"])
    mastery.ensure_cards(user, [lp.spec_item])
    mastery.recompute(user, [lp.spec_item])


def lesson_summary(user, item):
    s = PracticeSession.objects.filter(student=user, kind=Kind.LESSON, spec_item=item).first()
    attempts = list(s.attempts.all()) if s else []
    tries = [a for i, a in enumerate(attempts) if s and s.items[a.position].get("stage") == Stage.TRY]
    causes = [a.get_cause_display() for a in attempts if a.cause]
    review = item.itemreview_set.filter(student=user).first()
    return {
        "tries": tries,
        "correct": sum(a.is_correct for a in tries),
        "causes": causes,
        "fix": sessions.fix_for(next((a.cause for a in attempts if a.cause), "")),
        "review": review,
        "mastery": mastery.levels(user).get(item.id),
    }


# --- Flashcards ---------------------------------------------------------------


@needs_profile
def cards(request):
    today = timezone.localdate()
    qs = CardReview.objects.filter(student=request.user).select_related("card__spec_item")
    if not qs.exists():
        reached = SpecItem.objects.filter(lessonprogress__student=request.user)
        mastery.ensure_cards(request.user, reached or SpecItem.objects.all())
    code = request.GET.get("item")
    due = qs.filter(due__lte=today)
    if code:
        due = qs.filter(card__spec_item__code=code)
    review = due.order_by("due", "?").first()
    stats = {
        "due": qs.filter(due__lte=today).count(),
        "total": qs.count(),
        "learned": qs.filter(reps__gte=2).count(),
    }
    return render(request, "learning/cards.html", {"review": review, "stats": stats, "item_code": code})


@require_POST
@needs_profile
def card_grade(request, pk):
    review = get_object_or_404(CardReview, pk=pk, student=request.user)
    grade = request.POST.get("grade")
    if grade in mastery.GRADES:
        mastery.review_card(review, grade)
    url = reverse("learning:cards")
    if request.POST.get("item"):
        url += f"?item={request.POST['item']}"
    return redirect(url)


# --- Error journal ------------------------------------------------------------


@needs_profile
def errors(request):
    user = request.user
    replays = ErrorReplay.objects.filter(student=user).select_related("template__spec_item")
    misses = Attempt.objects.filter(student=user, is_correct=False).exclude(response="").select_related("spec_item", "instance", "session")[:25]
    since = timezone.now() - timezone.timedelta(days=30)
    causes = (
        Attempt.objects.filter(student=user, created_at__gte=since).exclude(cause="").values("cause").annotate(n=Count("id")).order_by("-n")
    )
    total = sum(c["n"] for c in causes) or 1
    cause_rows = [
        {"label": ErrorCause(c["cause"]).label, "n": c["n"], "share": c["n"] / total, "fix": sessions.fix_for(c["cause"])}
        for c in causes
    ]
    return render(
        request,
        "learning/errors.html",
        {
            "open": [r for r in replays if r.is_open],
            "closed": [r for r in replays if not r.is_open][:10],
            "misses": misses,
            "cause_rows": cause_rows,
        },
    )


# --- Tutor: audits and explain-it-back ----------------------------------------

SELF_CHECKS = [
    "I picked the right method for the question",
    "I took values from the right table or figure",
    "My setup matched the verified first steps",
    "My units were consistent throughout",
    "My arithmetic checks out when redone",
    "I answered what the question actually asked",
]


@require_POST
@needs_profile
def audit(request, pk):
    att = get_object_or_404(Attempt, pk=pk, student=request.user)
    back = request.POST.get("next") or reverse("learning:dashboard")
    photo = request.FILES.get("photo")
    if photo and att.instance_id:
        if photo.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
            messages.error(request, "That photo is too large. Try one under 10 MB.")
            return redirect(back)
        media = photo.content_type if photo.content_type in ("image/jpeg", "image/png", "image/webp", "image/gif") else None
        if not media:
            messages.error(request, "Upload a JPEG, PNG or WebP photo of your work.")
            return redirect(back)
        text = tutor.audit(att.instance, photo.read(), media, att.response)  # read in memory, never stored
        if text:
            att.audit, att.audit_source = text, Attempt.AuditSource.AI
            att.save(update_fields=["audit", "audit_source"])
            messages.success(request, "The tutor reviewed your work.")
        else:
            messages.info(request, "The tutor is not available. Use the self-audit below.")
        return redirect(back)
    checked = request.POST.getlist("checks")
    misses = [c for c in SELF_CHECKS if c not in checked]
    cause = request.POST.get("cause")
    if cause in ErrorCause.values and not att.is_correct:
        att.cause = cause
    att.audit = "Self-audit. Steps that went wrong: " + ("; ".join(misses) if misses else "none found") + "."
    att.audit_source = Attempt.AuditSource.SELF
    att.save(update_fields=["audit", "audit_source", "cause"])
    messages.success(request, "Self-audit saved to your error journal.")
    return redirect(back)


@needs_profile
def explain(request):
    templates = list(ProblemTemplate.objects.exclude(explain_prompt="").select_related("spec_item"))
    if request.method == "POST":
        t = get_object_or_404(ProblemTemplate, pk=request.POST.get("template"))
        text = request.POST.get("answer", "").strip()
        feedback = tutor.explain(t.explain_prompt, t.explain_answer, text) if text else None
        att = Attempt.objects.create(
            student=request.user,
            kind=Attempt.Kind.EXPLAIN,
            spec_item=t.spec_item,
            response=text,
            is_correct=False,
            counts_for_mastery=False,
            audit=feedback or "",
            audit_source=Attempt.AuditSource.AI if feedback else "",
            extra={"template": t.slug},
        )
        return render(request, "learning/explain.html", {"template": t, "att": att, "done": True})
    code = request.GET.get("item")
    pool = [t for t in templates if t.spec_item.code == code] if code else templates
    if not pool:
        messages.info(request, "No explain-it-back questions for that topic yet.")
        return redirect("learning:practice")
    return render(request, "learning/explain.html", {"template": random.choice(pool), "done": False})


# --- Interactive tutorials ----------------------------------------------------


def tutorial_context(item):
    lesson = getattr(item, "lesson", None)
    blocks = list(lesson.blocks.all()) if lesson else []
    script = f"js/widgets/{item.code.lower()}.js"
    return {
        "lesson": lesson,
        "blocks": blocks,
        "widget_script": script if finders.find(script) else None,
        "locations": item.locations.select_related("reference"),
        "activity_count": sum(1 for b in blocks if b.kind in ("check", "example")),
    }


@needs_profile
def tutorial(request, code):
    """The tutorial on its own, to read or revisit outside the lesson loop."""
    item = get_object_or_404(SpecItem.objects.select_related("area"), code=code)
    lp = LessonProgress.objects.filter(student=request.user, spec_item=item).first()
    return render(request, "learning/tutorial.html", {"item": item, "lp": lp, **tutorial_context(item)})


@require_POST
@needs_profile
def tutorial_check(request, pk):
    """Record an answer to a check inside a tutorial. Not counted toward mastery."""
    from curriculum.models import TutorialBlock

    block = get_object_or_404(TutorialBlock.objects.select_related("lesson__spec_item"), pk=pk, kind="check")
    try:
        data = json.loads(request.body or b"{}")
    except ValueError:
        data = {}
    Attempt.objects.create(
        student=request.user,
        kind=Attempt.Kind.CHECK,
        spec_item=block.lesson.spec_item,
        response=str(data.get("response", ""))[:200],
        is_correct=bool(data.get("correct")),
        counts_for_mastery=False,
        extra={"block": block.id, "tries": int(data.get("tries") or 0)},
    )
    return JsonResponse({"ok": True})
