"""The PE review queue: licensed reviewers approve content, unit by unit."""

import inspect
import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.staticfiles import finders
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from . import review
from .generation import draw
from .models import ReviewEvent, ReviewStatus, SpecArea
from .solvers import REGISTRY


def reviewer_for(user):
    rev = getattr(user, "content_reviewer", None)
    return rev if rev and rev.is_active else None


def can_view(user):
    return user.is_superuser or reviewer_for(user) is not None


@login_required
def queue(request):
    if not can_view(request.user):
        raise PermissionDenied
    show = request.GET.get("show", "open")
    areas = []
    counts = {"approved": 0, "stale": 0, "changes": 0, "unreviewed": 0}
    for area in SpecArea.objects.prefetch_related("items").order_by("order"):
        topics = []
        for item in area.items.all():
            summary = review.topic_summary(item)
            for u in summary["units"]:
                counts[u["state"]] += 1
            shown = [u for u in summary["units"] if show == "all" or u["state"] != "approved"]
            topics.append({"item": item, "summary": summary, "units": shown})
        areas.append({"area": area, "topics": topics})
    total = sum(counts.values())
    return render(
        request,
        "review/queue.html",
        {"areas": areas, "counts": counts, "total": total, "show": show, "reviewer": reviewer_for(request.user)},
    )


def next_open_unit(after_key=None):
    keys = []
    for area in SpecArea.objects.prefetch_related("items").order_by("order"):
        for item in area.items.all():
            keys += [u["key"] for u in review.units(item) if u["state"] != "approved"]
    if after_key in keys:
        i = keys.index(after_key)
        keys = keys[i + 1 :] + keys[:i]
    return keys[0] if keys else None


@login_required
def unit(request, key):
    if not can_view(request.user):
        raise PermissionDenied
    try:
        item, u = review.find_unit(key)
    except (LookupError, ValueError):
        raise Http404
    reviewer = reviewer_for(request.user)

    if request.method == "POST":
        if not reviewer:
            raise PermissionDenied
        decision = request.POST.get("decision")
        notes = request.POST.get("notes", "").strip()
        if decision not in (ReviewStatus.APPROVED, ReviewStatus.CHANGES):
            raise Http404
        if decision == ReviewStatus.CHANGES and not notes:
            messages.error(request, "Say what needs to change, so the content can be fixed.")
            return redirect("review:unit", key)
        review.record(u, item, request.user, reviewer, decision, notes)
        label = "Approved" if decision == ReviewStatus.APPROVED else "Marked as needing changes"
        messages.success(request, f"{label}: {item.code} {u['label']}.")
        nxt = next_open_unit(key)
        return redirect("review:unit", nxt) if nxt else redirect("review:queue")

    ctx = {"item": item, "u": u, "reviewer": reviewer}
    obj = u["objects"][0]
    if u["kind"] == "lesson":
        script = f"js/widgets/{item.code.lower()}.js"
        ctx.update({"lesson": obj, "blocks": list(obj.blocks.all()), "widget_script": script if finders.find(script) else None})
    elif u["kind"] == "template":
        rng = random.Random()
        ctx["template"] = obj
        ctx["samples"] = [draw(obj, rng) for _ in range(3)]
        fn = REGISTRY.get(obj.solver)
        ctx["source"] = inspect.getsource(fn) if fn else "(solver not found)"
    ct = {o._meta.model: ContentType.objects.get_for_model(o) for o in u["objects"]}
    ctx["history"] = ReviewEvent.objects.filter(
        content_type__in=set(ct.values()), object_id__in=[o.pk for o in u["objects"]]
    ).select_related("content_type")[:20]
    ctx["next_url"] = reverse("review:unit", args=[n]) if (n := next_open_unit(key)) and n != key else None
    return render(request, "review/unit.html", ctx)
