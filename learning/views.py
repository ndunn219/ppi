"""Student pages: onboarding, overview, plan, topics, references."""

import math

from django import forms
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from curriculum.models import ExamModule, Reference, SpecArea, SpecItem
from reports import readiness

from . import mastery
from .models import Attempt, ErrorReplay, ItemReview, LessonProgress, PracticeSession, StudentProfile


class SignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=60, required=False, label="First name")

    class Meta(UserCreationForm.Meta):
        fields = ["username", "first_name"]


def signup(request):
    if request.user.is_authenticated:
        return redirect("learning:dashboard")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("learning:onboarding")
    return render(request, "registration/signup.html", {"form": form})


class ProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ["exam_date", "hours_per_week"]
        widgets = {"exam_date": forms.DateInput(attrs={"type": "date"})}
        labels = {"exam_date": "Exam date", "hours_per_week": "Hours you can study each week"}
        help_texts = {
            "exam_date": "Leave blank if you have not booked yet. The plan assumes 13 weeks.",
            "hours_per_week": "The default plan assumes 8 to 10.",
        }


def profile_or_none(user):
    return StudentProfile.objects.filter(user=user).select_related("module").first()


@login_required
def onboarding(request):
    profile = profile_or_none(request.user)
    form = ProfileForm(request.POST or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        p = form.save(commit=False)
        p.user = request.user
        p.module = ExamModule.objects.filter(is_active=True).first()
        p.save()
        messages.success(request, "Saved. Next, the baseline diagnostic.")
        return redirect("learning:dashboard")
    return render(request, "learning/onboarding.html", {"form": form, "profile": profile, "items": SpecItem.objects.count()})


def needs_profile(view):
    """Send students without a profile to onboarding first."""

    @login_required
    def wrapped(request, *args, **kwargs):
        request.profile = profile_or_none(request.user)
        if request.profile is None:
            return redirect("learning:onboarding")
        return view(request, *args, **kwargs)

    wrapped.__name__ = view.__name__
    wrapped.__doc__ = view.__doc__
    return wrapped


def next_step(user, est, phase, profile):
    """The one thing to do next, for the overview's lead card."""
    if not est.diagnostic_done:
        open_diag = PracticeSession.objects.filter(student=user, kind=PracticeSession.Kind.DIAGNOSTIC, finished_at__isnull=True).first()
        if open_diag:
            return {"title": "Finish your baseline diagnostic", "body": "Pick up where you left off.", "url": open_diag and f"/s/{open_diag.id}/", "post": None}
        return {
            "title": "Take the baseline diagnostic",
            "body": f"About {SpecItem.objects.count() * 2 + 6} questions, timed at exam pace. It sets your personal plan.",
            "post": "diagnostic",
        }
    if not profile.plan_accepted_at:
        return {"title": "Review and accept your plan", "body": "Your topics, ordered by exam weight and current weakness.", "url": "/plan/"}
    due = ItemReview.objects.filter(student=user, due__lte=timezone.localdate()).count()
    if due:
        return {"title": "Daily warm-up", "body": f"{due} topic{'s' if due != 1 else ''} due for spaced review.", "post": "warmup"}
    top = readiness.focus(est, 1)
    if top:
        e = top[0]
        lp = LessonProgress.objects.filter(student=user, spec_item=e.item).first()
        if not lp or lp.stage != LessonProgress.Stage.DONE:
            return {"title": f"Study {e.item.name}", "body": "Your highest-value topic right now.", "url": f"/study/{e.item.code}/"}
        return {"title": f"Drill {e.item.name}", "body": "New numbers on your highest-value topic.", "post": "drill", "item": e.item.code}
    return {"title": "Take a mixed timed block", "body": "Ten questions at exam pace.", "post": "timed_block"}


@needs_profile
def dashboard(request):
    user = request.user
    levels = mastery.recompute(user)
    est = readiness.estimate(user, levels)
    readiness.snapshot(user, est)
    phases, phase = readiness.phase_status(user, est)
    recent = list(Attempt.objects.filter(student=user, kind=Attempt.Kind.PROBLEM)[:30])
    accuracy = sum(a.is_correct for a in recent) / len(recent) if recent else None
    sessions = PracticeSession.objects.filter(student=user).exclude(kind=PracticeSession.Kind.LESSON)[:6]
    areas = coverage_rows(levels)
    return render(
        request,
        "learning/dashboard.html",
        {
            "est": est,
            "phases": phases,
            "phase": phase,
            "accuracy": accuracy,
            "recent_count": len(recent),
            "sessions": sessions,
            "areas": areas,
            "next": next_step(user, est, phase, request.profile),
            "focus": readiness.focus(est),
            "profile": request.profile,
            "greeting": greeting(),
        },
    )


def greeting():
    h = timezone.localtime().hour
    return "Good morning" if h < 12 else ("Good afternoon" if h < 18 else "Good evening")


def coverage_rows(levels):
    rows = []
    for area in SpecArea.objects.prefetch_related("items").order_by("order"):
        rows.append({"area": area, "items": [(it, levels.get(it.id)) for it in area.items.all()]})
    return rows


@needs_profile
def plan(request):
    user, profile = request.user, request.profile
    est = readiness.estimate(user)
    ranked = readiness.priorities(est)
    today = timezone.localdate()
    weeks = 13
    if profile.exam_date and profile.exam_date > today:
        weeks = max(1, math.ceil((profile.exam_date - today).days / 7))
    total_hours = weeks * profile.hours_per_week
    study_hours = total_hours * 0.7  # the rest goes to simulations and review
    score = sum(e.weight * (1 - e.p) for e in ranked) or 1
    rows = [
        {"e": e, "hours": round(study_hours * e.weight * (1 - e.p) / score, 1), "rank": i + 1}
        for i, e in enumerate(ranked)
    ]
    return render(
        request,
        "learning/plan.html",
        {
            "rows": rows,
            "est": est,
            "weeks": weeks,
            "total_hours": total_hours,
            "study_hours": round(study_hours),
            "profile": profile,
        },
    )


@require_POST
@needs_profile
def accept_plan(request):
    request.profile.plan_accepted_at = timezone.now()
    request.profile.save(update_fields=["plan_accepted_at"])
    mastery.ensure_cards(request.user, SpecItem.objects.all())
    messages.success(request, "Plan accepted. Build phase unlocked.")
    return redirect("learning:dashboard")


@needs_profile
def topics(request):
    levels = mastery.levels(request.user)
    est = readiness.estimate(request.user, levels)
    by_item = {e.item.id: e for e in est.items}
    areas = []
    for area in SpecArea.objects.prefetch_related("items").order_by("order"):
        items = []
        for it in area.items.all():
            m = levels.get(it.id)
            items.append({"item": it, "m": m, "e": by_item.get(it.id)})
        areas.append({"area": area, "items": items})
    return render(request, "learning/topics.html", {"areas": areas})


@needs_profile
def topic(request, code):
    item = get_object_or_404(SpecItem.objects.select_related("area"), code=code)
    m = mastery.recompute(request.user, [item])[item.id]
    lp = LessonProgress.objects.filter(student=request.user, spec_item=item).first()
    attempts = Attempt.objects.filter(student=request.user, spec_item=item).select_related("instance")[:12]
    review = ItemReview.objects.filter(student=request.user, spec_item=item).first()
    replays = ErrorReplay.objects.filter(student=request.user, template__spec_item=item, closed_at__isnull=True)
    return render(
        request,
        "learning/topic.html",
        {
            "item": item,
            "m": m,
            "lp": lp,
            "attempts": attempts,
            "review": review,
            "replays": replays,
            "locations": item.locations.select_related("reference"),
            "cards": item.cards.all(),
            "templates": item.templates.filter(is_active=True),
        },
    )


@needs_profile
def references(request):
    refs = Reference.objects.all()
    items = SpecItem.objects.prefetch_related("locations__reference").select_related("area")
    return render(request, "learning/references.html", {"refs": refs, "items": items})


@needs_profile
def simulation(request):
    sims = PracticeSession.objects.filter(
        student=request.user, kind__in=[PracticeSession.Kind.FULL_EXAM, PracticeSession.Kind.HALF_EXAM]
    )
    rows = [{"s": s, "score": readiness.session_score(s) if s.finished_at else None} for s in sims]
    return render(request, "learning/simulation.html", {"rows": rows})


@login_required
def help_page(request):
    from django.conf import settings

    from learning.views_practice import LOOP, MODES

    return render(
        request,
        "learning/help.html",
        {"loop": LOOP, "modes": MODES, "course": settings.COURSE, "phases": readiness.PHASES},
    )
