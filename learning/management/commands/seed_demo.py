"""Create a demo student with five weeks of simulated practice.

Gives every page and report something to show: a finished diagnostic, a
plan, lessons, drills, misses with causes, spaced reviews, flashcards, two
simulations and daily readiness snapshots. The answers are simulated: a
student whose accuracy on each topic climbs over the weeks.

    python manage.py seed_demo --password <choose one>
"""

import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from curriculum.models import Card, ExamModule, SpecItem
from learning import mastery, planning, sessions
from learning.models import (
    Attempt,
    CardReview,
    ErrorReplay,
    ItemReview,
    LessonProgress,
    Mastery,
    PracticeSession,
    StudentProfile,
)
from reports import readiness
from reports.models import ReadinessSnapshot, SharedReport

Kind = PracticeSession.Kind
DAYS = 35


class Command(BaseCommand):
    help = "Create (or reset) a demo student with simulated history."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="demo")
        parser.add_argument("--password", required=True)
        parser.add_argument("--seed", type=int, default=7)

    @transaction.atomic
    def handle(self, *args, username, password, seed, **options):
        if not SpecItem.objects.exists():
            raise CommandError("Run seed_course first.")
        rng = random.Random(seed)
        User.objects.filter(username=username).delete()
        user = User.objects.create_user(username, password=password, first_name="Jordan")
        start = timezone.now() - timedelta(days=DAYS)
        StudentProfile.objects.create(
            user=user,
            module=ExamModule.objects.first(),
            exam_date=timezone.localdate() + timedelta(days=45),
            hours_per_week=9,
            plan_accepted_at=start + timedelta(days=1),
        )
        items = list(SpecItem.objects.all())
        # Each topic has its own starting skill and learning rate.
        skill = {it.id: rng.uniform(0.25, 0.6) for it in items}
        growth = {it.id: rng.uniform(0.008, 0.018) for it in items}

        def p_correct(item, day):
            return min(0.95, skill[item.id] + growth[item.id] * day)

        def answer(session, pos, day, at, item_bias=0.0):
            q = session.items[pos]
            if q["type"] == "units":
                data = {"value": str(q["q"]["answer"] if rng.random() < 0.8 else 0)}
            elif q["type"] == "problem":
                from learning.models import ProblemInstance

                inst = ProblemInstance.objects.get(id=q["instance"])
                item = inst.template.spec_item
                right = rng.random() < p_correct(item, day) + item_bias
                idx = next(i for i, c in enumerate(inst.choices) if bool(c["cause"]) != right)
                data = {"choice": idx}
                if rng.random() < 0.6:
                    refs = list(item.locations.values_list("reference__short_name", flat=True))
                    data["cited_reference"] = rng.choice(refs) if rng.random() < 0.8 else "HSM"
                if "estimate" in q:
                    want = rng.random() < 0.7
                    data["estimate"] = next((i for i, b in enumerate(q["estimate"]) if b["correct"] == want), 0)
            elif q["type"] == "lookup":
                from curriculum.models import LookupDrill

                d = LookupDrill.objects.get(id=q["drill"])
                good = rng.random() < 0.55 + day * 0.01
                data = {"choice": q["options"].index(d.answer) if good else (q["options"].index(d.answer) + 1) % 4}
            else:
                data = {"choice": 0}
            secs = int(rng.gauss(35, 12)) if q["type"] == "lookup" else int(rng.gauss(330 - day * 2, 90))
            att = sessions.record(session, pos, data, max(8, secs), user)
            Attempt.objects.filter(pk=att.pk).update(created_at=at)

        def run(kind, day, item=None, n_override=None):
            at = start + timedelta(days=day, hours=rng.randint(18, 21), minutes=rng.randint(0, 59))
            s = sessions.build(user, kind, item, rng)
            if s is None:
                return None
            PracticeSession.objects.filter(pk=s.pk).update(started_at=at)
            s.refresh_from_db()
            for pos in range(len(s.items)):
                answer(s, pos, day, at + timedelta(minutes=5 * pos))
            sessions.finish(s)
            PracticeSession.objects.filter(pk=s.pk).update(finished_at=at + timedelta(minutes=6 * len(s.items)))
            return s

        def backdate_reviews(day):
            # schedule_item ran at "now"; shift what it wrote back to `day`.
            shift = timedelta(days=DAYS - day)
            for r in ItemReview.objects.filter(student=user, last_reviewed__gte=timezone.now() - timedelta(minutes=5)):
                r.due = r.due - shift
                r.last_reviewed = r.last_reviewed - shift
                r.save()

        # Week 1: the diagnostic.
        run(Kind.DIAGNOSTIC, 0)
        backdate_reviews(0)
        # The schedule as accepted on day 1, before any lesson, so the plan
        # page shows real pacing against it.
        planning.save(user.profile, user, "accepted", today=timezone.localdate(start) + timedelta(days=1))
        mastery.ensure_cards(user, items)

        order = sorted(items, key=lambda it: skill[it.id])
        for day in range(1, DAYS):
            if rng.random() < 0.2:
                continue  # a rest day
            if day % 3 == 1 and order:
                it = order.pop(0)
                lp = LessonProgress.objects.create(student=user, spec_item=it, stage=LessonProgress.Stage.DONE, completed_at=start + timedelta(days=day))
                LessonProgress.objects.filter(pk=lp.pk).update(started_at=start + timedelta(days=day))
                run(Kind.DRILL, day, it)
            else:
                run(rng.choice([Kind.DRILL, Kind.ESTIMATE, Kind.WARMUP, Kind.DRILL]), day, rng.choice(items))
            if day % 4 == 0:
                run(rng.choice([Kind.LOOKUP, Kind.METHOD, Kind.SPOT_ERROR, Kind.UNITS]), day)
            if day % 7 == 5:
                run(Kind.TIMED_BLOCK, day)
            if day in (26, 33):
                run(Kind.FULL_EXAM if day == 33 else Kind.HALF_EXAM, day)
            backdate_reviews(day)
            for review in CardReview.objects.filter(student=user).order_by("?")[: rng.randint(5, 12)]:
                mastery.review_card(review, rng.choice(["good", "good", "easy", "hard", "again"]), start + timedelta(days=day))

        # Daily readiness snapshots, recomputed as of each day.
        for day in range(0, DAYS + 1, 2):
            when = start + timedelta(days=day, hours=23)
            Mastery.objects.filter(student=user).delete()
            visible = Attempt.objects.filter(student=user, created_at__gt=when)
            hidden = list(visible.values_list("id", flat=True))
            Attempt.objects.filter(id__in=hidden).update(counts_for_mastery=False)
            est = readiness.estimate(user, mastery.recompute(user), now=when)
            ReadinessSnapshot.objects.update_or_create(
                student=user,
                taken_on=timezone.localdate(when),
                defaults={
                    "zone": est.zone,
                    "low": est.low,
                    "mid": est.mid,
                    "high": est.high,
                    "coverage": est.coverage_practicing,
                    "evidence": est.evidence,
                    "details": {"levels": {e.item.code: e.level for e in est.items}},
                },
            )
            Attempt.objects.filter(id__in=hidden).exclude(kind__in=["lookup", "method", "spot_error", "units", "explain"]).update(counts_for_mastery=True)
        mastery.recompute(user)
        readiness.snapshot(user, readiness.estimate(user))

        SharedReport.objects.create(
            student=user,
            kind=SharedReport.Kind.READINESS,
            recipient="Supervising PE",
            sections=[k for k, _ in SharedReport.SECTIONS],
            live=True,
            expires_at=timezone.now() + timedelta(days=30),
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Demo student '{username}' ready: {Attempt.objects.filter(student=user).count()} answers, "
                f"{ErrorReplay.objects.filter(student=user, closed_at__isnull=True).count()} open replays, "
                f"{Card.objects.count()} cards in review."
            )
        )
