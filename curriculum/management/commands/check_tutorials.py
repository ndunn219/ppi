"""Validate every tutorial module before it is seeded.

Checks each block's fields for its kind, that each multiple-choice check
has exactly one correct answer and a reason on every choice, that numeric
checks have a tolerance, that every widget named is registered in the
topic's widget file, and that all reStructuredText renders without
warnings. --export writes the widget configs for scripts/check_widgets.js.
"""

import json
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django_docutils.lib.publisher import publish_html_from_source
from docutils.core import publish_doctree

from curriculum import tutorials
from curriculum.models import SpecItem, TutorialBlock

KINDS = set(TutorialBlock.Kind.values)
FIELDS = {f.name for f in TutorialBlock._meta.get_fields()} - {"id", "lesson", "order"}


def rst_problems(text):
    """Warnings from docutils, plus any failure of the django-docutils
    writer the pages use (it can fail where plain docutils does not)."""
    problems = []
    doctree = publish_doctree(text or "", settings_overrides={"report_level": 5, "halt_level": 5})
    for msg in doctree.traverse(condition=lambda n: n.tagname == "system_message"):
        if int(msg.get("level", 0)) >= 2:
            problems.append(msg.astext().splitlines()[0])
    try:
        publish_html_from_source(text or "", show_title=False)
    except Exception as exc:  # report every writer failure, whatever its type
        problems.append(f"page renderer failed: {type(exc).__name__}: {exc}")
    return problems


class Command(BaseCommand):
    help = "Validate the tutorial modules in curriculum/tutorials."

    def add_arguments(self, parser):
        parser.add_argument("--export", help="Write widget configs as JSON to this path.")
        parser.add_argument("--only", help="Check one spec item code.")

    def handle(self, *args, export=None, only=None, **options):
        errors, configs = [], []
        all_tutorials = tutorials.load_all()
        codes = [only.upper()] if only else sorted(all_tutorials)
        for code in codes:
            tut = all_tutorials.get(code)
            if tut is None:
                errors.append(f"{code}: no tutorial module")
                continue
            if not SpecItem.objects.filter(code=code).exists():
                errors.append(f"{code}: no spec item with this code")
            js = Path(settings.BASE_DIR, "static", "js", "widgets", f"{code.lower()}.js")
            registered = set(re.findall(r"""\.register\(\s*["']([\w-]+)["']""", js.read_text())) if js.exists() else set()
            counts = {}
            for i, b in enumerate(tut.get("blocks", [])):
                where = f"{code} block {i} ({b.get('kind')})"
                kind = b.get("kind")
                counts[kind] = counts.get(kind, 0) + 1
                if kind not in KINDS:
                    errors.append(f"{where}: unknown kind")
                    continue
                extra = set(b) - FIELDS
                if extra:
                    errors.append(f"{where}: unknown fields {sorted(extra)}")
                if kind == "text" and not b.get("body"):
                    errors.append(f"{where}: text needs a body")
                if kind in ("figure", "explorer") and not b.get("widget"):
                    errors.append(f"{where}: needs a widget")
                if kind == "check":
                    if not b.get("prompt") or not b.get("explanation"):
                        errors.append(f"{where}: needs a prompt and an explanation")
                    choices = b.get("choices") or []
                    if choices:
                        if sum(bool(c.get("correct")) for c in choices) != 1:
                            errors.append(f"{where}: needs exactly one correct choice")
                        if any(not c.get("why") for c in choices):
                            errors.append(f"{where}: every choice needs a why")
                    elif b.get("answer") is None or b.get("tolerance") is None:
                        errors.append(f"{where}: numeric check needs answer and tolerance")
                if kind == "example":
                    if not b.get("prompt") or not b.get("steps"):
                        errors.append(f"{where}: needs a prompt and steps")
                    if any(not s.get("text") for s in b.get("steps", [])):
                        errors.append(f"{where}: every step needs text")
                if b.get("widget"):
                    if b["widget"] not in registered:
                        errors.append(f"{where}: widget {b['widget']!r} not registered in {js.name}")
                    configs.append({"code": code, "block": i, "widget": b["widget"], "config": b.get("config") or {}})
                texts = [b.get("body"), b.get("prompt"), b.get("explanation")] + [s.get("text") for s in b.get("steps", [])]
                for t in texts:
                    for p in rst_problems(t):
                        errors.append(f"{where}: reStructuredText: {p}")
            needed = {"text": 3, "explorer": 1, "check": 3, "example": 2}
            for k, n in needed.items():
                if counts.get(k, 0) < n:
                    errors.append(f"{code}: has {counts.get(k, 0)} {k} blocks; at least {n} expected")
            self.stdout.write(f"{code}: {sum(counts.values())} blocks {counts}")
        if export:
            Path(export).parent.mkdir(parents=True, exist_ok=True)
            Path(export).write_text(json.dumps(configs, indent=1))
            self.stdout.write(f"Wrote {len(configs)} widget configs to {export}")
        if errors:
            for e in errors:
                self.stderr.write(e)
            raise CommandError(f"{len(errors)} problem(s)")
        self.stdout.write(self.style.SUCCESS("All tutorials valid."))
