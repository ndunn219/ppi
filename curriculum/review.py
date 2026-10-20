"""PE review of course content.

Content is reviewed in units, per topic:

* the lesson: its summary and every block of its interactive tutorial
* each problem template, including its solver's code
* the topic's flashcards, as one group
* the topic's lookup drills, as one group

Approving a unit stamps every object in it with the reviewer, their
license, the date and a fingerprint of the content. If the content
changes later, the fingerprint no longer matches and the unit goes back
to the queue as "changed since approval".
"""

import hashlib
import inspect
import json

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone

from .models import Card, Lesson, LookupDrill, ProblemTemplate, ReviewEvent, ReviewStatus, SpecItem

STATE_LABELS = {
    "approved": "PE-reviewed",
    "stale": "Changed since approval",
    "changes": "Needs changes",
    "unreviewed": "Not yet reviewed",
}


def _digest(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()


def content_hash(obj):
    """A fingerprint of everything a reviewer approves for this object."""
    if isinstance(obj, Lesson):
        blocks = list(
            obj.blocks.order_by("order").values(
                "kind", "title", "body", "widget", "config", "prompt", "choices", "answer", "tolerance", "unit", "hint", "explanation", "steps"
            )
        ) if obj.pk else []
        return _digest({"title": obj.title, "body": obj.body, "blocks": blocks})
    if isinstance(obj, ProblemTemplate):
        from .solvers import REGISTRY

        fn = REGISTRY.get(obj.solver)
        source = inspect.getsource(fn) if fn else ""
        return _digest(
            {
                "stem": obj.stem,
                "solver": obj.solver,
                "source": source,
                "params": obj.params,
                "unit": obj.answer_unit,
                "decimals": obj.decimals,
                "explain": [obj.explain_prompt, obj.explain_answer],
            }
        )
    if isinstance(obj, Card):
        return _digest({"kind": obj.kind, "front": obj.front, "back": obj.back})
    if isinstance(obj, LookupDrill):
        return _digest([obj.prompt, obj.answer, obj.wrong_1, obj.wrong_2, obj.wrong_3, obj.explanation])
    raise TypeError(obj)


def group_state(objs):
    """One state for a group: the weakest of its members'."""
    states = {o.review_state for o in objs}
    if not objs:
        return "approved"
    for s in ("changes", "stale", "unreviewed"):
        if s in states:
            return s
    return "approved"


def units(item):
    """The review units of one topic, in the order a reviewer works through them."""
    out = []
    lesson = getattr(item, "lesson", None)
    if lesson:
        out.append({"kind": "lesson", "key": f"lesson-{lesson.pk}", "label": "Lesson and tutorial", "objects": [lesson],
                    "count": lesson.blocks.count(), "noun": "tutorial blocks"})
    for t in item.templates.filter(is_active=True):
        out.append({"kind": "template", "key": f"template-{t.pk}", "label": f"Problem: {t.title}", "objects": [t], "count": None})
    cards = list(item.cards.all())
    if cards:
        out.append({"kind": "cards", "key": f"cards-{item.code}", "label": "Flashcards", "objects": cards, "count": len(cards), "noun": "cards"})
    drills = list(item.lookup_drills.all())
    if drills:
        out.append({"kind": "drills", "key": f"drills-{item.code}", "label": "Lookup drills", "objects": drills, "count": len(drills), "noun": "questions"})
    for u in out:
        u["state"] = group_state(u["objects"])
        u["state_label"] = STATE_LABELS[u["state"]]
        approved = [o for o in u["objects"] if o.review_status == ReviewStatus.APPROVED and o.reviewed_on]
        last = max(approved, key=lambda o: o.reviewed_on) if approved else None
        u["reviewer"] = last.reviewer if last else ""
        u["reviewer_license"] = last.reviewer_license if last else ""
        u["reviewed_on"] = last.reviewed_on if last else None
        u["notes"] = next((o.review_notes for o in u["objects"] if o.review_notes), "")
    return out


def find_unit(key):
    """The unit a review page or form refers to, by its key."""
    kind, _, ref = key.partition("-")
    if kind == "lesson":
        lesson = Lesson.objects.select_related("spec_item").get(pk=ref)
        item = lesson.spec_item
    elif kind == "template":
        item = ProblemTemplate.objects.select_related("spec_item").get(pk=ref).spec_item
    elif kind in ("cards", "drills"):
        item = SpecItem.objects.get(code=ref)
    else:
        raise LookupError(key)
    for u in units(item):
        if u["key"] == key:
            return item, u
    raise LookupError(key)


def topic_summary(item):
    us = units(item)
    approved = sum(1 for u in us if u["state"] == "approved")
    if approved == len(us):
        state = "approved"
    elif approved == 0:
        state = "unreviewed"
    else:
        state = "partial"
    return {"units": us, "approved": approved, "total": len(us), "state": state}


def course_summary():
    approved = total = 0
    for item in SpecItem.objects.all():
        s = topic_summary(item)
        approved += s["approved"]
        total += s["total"]
    return {"approved": approved, "total": total, "all": total > 0 and approved == total, "none": approved == 0}


@transaction.atomic
def record(unit, item, user, reviewer, status, notes=""):
    """Stamp a decision on every object in a unit and log it."""
    today = timezone.localdate()
    for obj in unit["objects"]:
        obj.review_status = status
        obj.reviewer = reviewer.name
        obj.reviewer_license = reviewer.license
        obj.reviewed_on = today
        obj.review_notes = notes
        obj.reviewed_hash = content_hash(obj) if status == ReviewStatus.APPROVED else ""
        obj.save(update_fields=["review_status", "reviewer", "reviewer_license", "reviewed_on", "review_notes", "reviewed_hash"])
        ReviewEvent.objects.create(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.pk,
            spec_item=item,
            label=f"{item.code} {unit['label']}" + (f": {str(obj)[:80]}" if len(unit["objects"]) > 1 else ""),
            status=status,
            reviewer=user,
            reviewer_name=reviewer.name,
            reviewer_license=reviewer.license,
            notes=notes,
            content_hash=content_hash(obj),
        )
