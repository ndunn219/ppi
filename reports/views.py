from datetime import timedelta

from django.contrib import messages
from django.db.models import F
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from learning.models import PracticeSession
from learning.views import needs_profile

from . import charts, data
from .models import SharedReport

EXPIRY_CHOICES = [(7, "7 days"), (30, "30 days"), (90, "90 days")]


def chart_context(kind, payload):
    if kind == SharedReport.Kind.READINESS:
        return {"trend": charts.trend_chart(payload["trend"], payload["estimate"]["target"])}
    if kind == SharedReport.Kind.SIMULATION:
        return {"pacing": charts.pacing_chart(payload["cumulative"], payload["pace_target"])}
    return {}


@needs_profile
def index(request):
    shares = SharedReport.objects.filter(student=request.user)
    sims = PracticeSession.objects.filter(
        student=request.user,
        kind__in=[PracticeSession.Kind.FULL_EXAM, PracticeSession.Kind.HALF_EXAM, PracticeSession.Kind.TIMED_BLOCK, PracticeSession.Kind.DIAGNOSTIC],
        finished_at__isnull=False,
    )[:10]
    return render(request, "reports/index.html", {"shares": shares, "sims": sims})


@needs_profile
def readiness_view(request):
    payload = data.readiness_report(request.user)
    return render(
        request,
        "reports/readiness.html",
        {
            "d": payload,
            "sections": [k for k, _ in SharedReport.SECTIONS],
            "section_choices": SharedReport.SECTIONS,
            "expiry_choices": EXPIRY_CHOICES,
            "kind": SharedReport.Kind.READINESS,
            **chart_context(SharedReport.Kind.READINESS, payload),
        },
    )


@needs_profile
def weekly_view(request):
    payload = data.weekly_report(request.user)
    return render(
        request,
        "reports/weekly.html",
        {"d": payload, "expiry_choices": EXPIRY_CHOICES, "kind": SharedReport.Kind.WEEKLY},
    )


@needs_profile
def simulation_view(request, pk):
    session = get_object_or_404(PracticeSession, pk=pk, student=request.user, finished_at__isnull=False)
    payload = data.simulation_report(session)
    return render(
        request,
        "reports/simulation.html",
        {
            "d": payload,
            "session": session,
            "expiry_choices": EXPIRY_CHOICES,
            "kind": SharedReport.Kind.SIMULATION,
            **chart_context(SharedReport.Kind.SIMULATION, payload),
        },
    )


@require_POST
@needs_profile
def share(request):
    kind = request.POST.get("kind")
    if kind not in SharedReport.Kind.values:
        raise Http404
    days = int(request.POST.get("days", 30))
    if days not in dict(EXPIRY_CHOICES):
        days = 30
    simulation = None
    if kind == SharedReport.Kind.SIMULATION:
        simulation = get_object_or_404(PracticeSession, pk=request.POST.get("simulation"), student=request.user)
        snapshot = data.simulation_report(simulation)
    elif kind == SharedReport.Kind.WEEKLY:
        snapshot = data.weekly_report(request.user)
    else:
        snapshot = data.readiness_report(request.user)
    valid = {k for k, _ in SharedReport.SECTIONS}
    sections = [s for s in request.POST.getlist("sections") if s in valid] or sorted(valid)
    report = SharedReport.objects.create(
        student=request.user,
        kind=kind,
        simulation=simulation,
        recipient=request.POST.get("recipient", "")[:120],
        sections=sections,
        live=bool(request.POST.get("live")) and kind == SharedReport.Kind.READINESS,
        snapshot=snapshot,
        expires_at=timezone.now() + timedelta(days=days),
    )
    link = request.build_absolute_uri(reverse("public_report", args=[report.token]))
    messages.success(request, f"Share link ready: {link}")
    return redirect("reports:index")


@require_POST
@needs_profile
def revoke(request, pk):
    report = get_object_or_404(SharedReport, pk=pk, student=request.user)
    report.revoked_at = timezone.now()
    report.save(update_fields=["revoked_at"])
    messages.success(request, "Link revoked. It no longer opens.")
    return redirect("reports:index")


def public(request, token):
    report = SharedReport.objects.filter(token=token).select_related("student", "simulation").first()
    if not report or not report.is_active:
        return render(request, "reports/public_gone.html", status=404)
    SharedReport.objects.filter(pk=report.pk).update(views=F("views") + 1)
    if report.live and report.kind == SharedReport.Kind.READINESS:
        payload = data.readiness_report(report.student)
    else:
        payload = report.snapshot
    template = {
        SharedReport.Kind.READINESS: "reports/public_readiness.html",
        SharedReport.Kind.WEEKLY: "reports/public_weekly.html",
        SharedReport.Kind.SIMULATION: "reports/public_simulation.html",
    }[report.kind]
    return render(
        request,
        template,
        {"d": payload, "report": report, "sections": report.sections, "public": True, **chart_context(report.kind, payload)},
    )
