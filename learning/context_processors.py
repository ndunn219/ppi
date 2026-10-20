from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from .models import CardReview, ErrorReplay, ItemReview


def shell(request):
    """The sidebar: its links, the active one, and what is waiting."""
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}
    today = timezone.localdate()
    due_cards = CardReview.objects.filter(student=user, due__lte=today).count()
    due_items = ItemReview.objects.filter(student=user, due__lte=today).count()
    open_replays = ErrorReplay.objects.filter(student=user, closed_at__isnull=True).count()
    path = request.path
    nav = [
        ("Overview", "learning:dashboard", "i-home", None),
        ("My plan", "learning:plan", "i-route", None),
        ("Topics", "learning:topics", "i-layers", None),
        ("Practice", "learning:practice", "i-target", due_items or None),
        ("Flashcards", "learning:cards", "i-cards", due_cards or None),
        ("Error journal", "learning:errors", "i-alert", open_replays or None),
        ("Exam simulation", "learning:simulation", "i-timer", None),
        ("References", "learning:references", "i-book", None),
        ("Reports", "reports:index", "i-chart", None),
    ]
    items = []
    for label, name, icon, count in nav:
        href = reverse(name)
        active = path == href if href == "/" else path.startswith(href)
        items.append({"label": label, "href": href, "icon": icon, "count": count, "active": active})
    return {"nav_items": items, "due_cards": due_cards, "due_items": due_items, "open_replays": open_replays}


def assets(request):
    return {"asset_version": settings.ASSET_VERSION}
