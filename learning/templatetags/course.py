from django import template

register = template.Library()


@register.filter
def pct(value, digits=0):
    if value is None or value == "":
        return "—"
    return f"{float(value) * 100:.{int(digits)}f}%"


@register.filter
def minutes(seconds):
    """Seconds → '4.5 min'."""
    if seconds is None:
        return "—"
    return f"{float(seconds) / 60:.1f} min"


@register.filter
def clock(seconds):
    if seconds is None:
        return "—"
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


@register.filter
def letter(index):
    return "ABCDEFGH"[int(index)]


@register.filter
def get(mapping, key):
    try:
        return mapping.get(key)
    except AttributeError:
        return None


@register.filter
def at(seq, index):
    try:
        return seq[int(index)]
    except (IndexError, TypeError, ValueError):
        return None


@register.filter
def times(value, factor):
    return float(value) * float(factor)


LEVEL_NAMES = ["Not started", "Introduced", "Practicing", "Proficient", "Exam-ready"]


@register.filter
def level_name(level):
    return LEVEL_NAMES[int(level or 0)]


@register.simple_tag
def level_badge(level, decayed=False):
    from django.utils.html import format_html

    level = int(level or 0)
    extra = " lvl-decayed" if decayed else ""
    title = " (review overdue)" if decayed else ""
    return format_html('<span class="lvl lvl-{}{}" title="{}{}">{}</span>', level, extra, LEVEL_NAMES[level], title, LEVEL_NAMES[level])
