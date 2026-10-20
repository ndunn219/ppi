"""Load the proof-of-concept course content from curriculum.content.

Safe to run on every deploy: by default it only creates what is missing,
so edits made in the admin survive. --update rewrites seeded fields from
the content file.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from curriculum import content
from curriculum.models import (
    Card,
    ExamModule,
    Lesson,
    LookupDrill,
    ProblemTemplate,
    Reference,
    ReferenceLocation,
    SpecArea,
    SpecItem,
)


class Command(BaseCommand):
    help = "Create (or with --update, refresh) the course content."

    def add_arguments(self, parser):
        parser.add_argument("--update", action="store_true", help="Overwrite seeded fields with the content file.")

    def upsert(self, model, lookup, values):
        if self.update:
            obj, created = model.objects.update_or_create(**lookup, defaults=values)
        else:
            obj, created = model.objects.get_or_create(**lookup, defaults=values)
        self.counts[model.__name__] = self.counts.get(model.__name__, 0) + int(created)
        return obj

    @transaction.atomic
    def handle(self, *args, update=False, **options):
        self.update = update
        self.counts = {}
        module = self.upsert(
            ExamModule, {"slug": content.MODULE["slug"]}, {k: v for k, v in content.MODULE.items() if k != "slug"}
        )
        refs = {}
        for r in content.REFERENCES:
            refs[r["short_name"]] = self.upsert(
                Reference, {"short_name": r["short_name"]}, {k: v for k, v in r.items() if k != "short_name"}
            )
        for a_order, a in enumerate(content.AREAS):
            area = self.upsert(
                SpecArea,
                {"code": a["code"]},
                {"module": module, "name": a["name"], "weight": a["weight"], "order": a_order},
            )
            for i_order, it in enumerate(a["items"]):
                item = self.upsert(
                    SpecItem,
                    {"code": it["code"]},
                    {
                        "area": area,
                        "name": it["name"],
                        "method_name": it["method_name"],
                        "summary": it["summary"],
                        "cues": it["cues"],
                        "order": i_order,
                    },
                )
                lesson = it["lesson"]
                self.upsert(
                    Lesson,
                    {"spec_item": item},
                    {"title": lesson["title"], "minutes": lesson["minutes"], "body": lesson["body"].strip() + "\n"},
                )
                for c_order, (kind, front, back) in enumerate(it["cards"]):
                    self.upsert(Card, {"spec_item": item, "front": front}, {"kind": kind, "back": back, "order": c_order})
                for lk in it["lookups"]:
                    w1, w2, w3 = lk["wrong"]
                    self.upsert(
                        LookupDrill,
                        {"spec_item": item, "prompt": lk["prompt"]},
                        {"answer": lk["answer"], "wrong_1": w1, "wrong_2": w2, "wrong_3": w3, "explanation": lk["explanation"]},
                    )
                for ref_name, locator, what, terms in it["locations"]:
                    self.upsert(
                        ReferenceLocation,
                        {"spec_item": item, "reference": refs[ref_name], "locator": locator},
                        {"what_is_there": what, "search_terms": terms},
                    )
                for t in it["templates"]:
                    self.upsert(
                        ProblemTemplate,
                        {"slug": t["slug"]},
                        {"spec_item": item, **{k: v for k, v in t.items() if k != "slug"}},
                    )
        made = ", ".join(f"{n} {name}" for name, n in self.counts.items() if n) or "nothing new"
        self.stdout.write(self.style.SUCCESS(f"Course content ready ({'updated' if update else 'created'}: {made})."))
