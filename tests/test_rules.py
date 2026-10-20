"""Mastery levels, spaced review and the readiness estimate."""

from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from curriculum.models import SpecItem
from learning import mastery
from learning.models import Attempt, ItemReview, LevelChoices, PracticeSession, StudentProfile
from reports import readiness
from reports.models import Zone


class RulesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_course", verbosity=0)

    def setUp(self):
        self.user = User.objects.create_user("t")
        from curriculum.models import ExamModule

        StudentProfile.objects.create(user=self.user, module=ExamModule.objects.first())
        self.item = SpecItem.objects.get(code="TE1")

    def attempt(self, correct, days_ago=0, seconds=200, hint=False, item=None):
        return Attempt.objects.create(
            student=self.user,
            spec_item=item or self.item,
            kind=Attempt.Kind.PROBLEM,
            is_correct=correct,
            seconds=seconds,
            hint_used=hint,
            response="x",
            created_at=timezone.now() - timedelta(days=days_ago),
        )

    def level(self):
        return mastery.recompute(self.user, [self.item])[self.item.id].level

    def test_no_attempts_not_started(self):
        self.assertEqual(self.level(), LevelChoices.NOT_STARTED)

    def test_practicing_then_proficient(self):
        for d in (5, 4, 3, 2):
            self.attempt(d % 2 == 0, days_ago=d)
        self.assertEqual(self.level(), LevelChoices.PRACTICING)
        for d in (1, 1, 0, 0, 0):
            self.attempt(True, days_ago=d)
        self.assertEqual(self.level(), LevelChoices.PROFICIENT)

    def test_same_day_is_not_proficient(self):
        for _ in range(5):
            self.attempt(True)
        self.assertEqual(self.level(), LevelChoices.PRACTICING)

    def test_hints_cap_proficiency(self):
        for d in (3, 2, 1, 0, 0):
            self.attempt(True, days_ago=d, hint=True)
        self.assertLess(self.level(), LevelChoices.PROFICIENT)

    def test_overdue_review_decays(self):
        for d in (4, 3, 2, 1, 0):
            self.attempt(True, days_ago=d)
        ItemReview.objects.create(student=self.user, spec_item=self.item, due=timezone.localdate() - timedelta(days=2))
        m = mastery.recompute(self.user, [self.item])[self.item.id]
        self.assertEqual(m.earned_level, LevelChoices.PROFICIENT)
        self.assertEqual(m.level, LevelChoices.PRACTICING)
        self.assertTrue(m.decayed)

    def test_review_ladder_only_climbs_when_due(self):
        r = mastery.schedule_item(self.user, self.item, True)
        self.assertEqual(r.rung, 0)
        r = mastery.schedule_item(self.user, self.item, True)  # not due yet: no climb
        self.assertEqual(r.rung, 0)
        r.due = timezone.localdate()
        r.save()
        r = mastery.schedule_item(self.user, self.item, True)
        self.assertEqual(r.rung, 1)
        self.assertEqual(r.due, timezone.localdate() + timedelta(days=3))
        r = mastery.schedule_item(self.user, self.item, False)
        self.assertEqual((r.rung, r.due), (0, timezone.localdate() + timedelta(days=1)))

    def test_no_zone_before_diagnostic(self):
        est = readiness.estimate(self.user)
        self.assertEqual(est.zone, Zone.NONE)
        self.assertIsNone(est.mid)

    def test_strong_student_without_sims_is_approaching(self):
        PracticeSession.objects.create(student=self.user, kind=PracticeSession.Kind.DIAGNOSTIC, finished_at=timezone.now())
        for item in SpecItem.objects.all():
            for d in (12, 9, 6, 3, 0, 0, 1, 2):
                self.attempt(True, days_ago=d, item=item)
        est = readiness.estimate(self.user, mastery.recompute(self.user))
        self.assertGreater(est.low, 0.7)
        self.assertEqual(est.zone, Zone.APPROACHING)  # Ready needs two full simulations

    def test_unstudied_topics_score_as_guessing(self):
        est = readiness.estimate(self.user)
        self.assertTrue(all(e.p == readiness.GUESS for e in est.items))


class PlanningTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_course", verbosity=0)

    def setUp(self):
        from curriculum.models import ExamModule

        self.user = User.objects.create_user("p")
        self.profile = StudentProfile.objects.create(user=self.user, module=ExamModule.objects.first(), hours_per_week=10)
        PracticeSession.objects.create(student=self.user, kind=PracticeSession.Kind.DIAGNOSTIC, finished_at=timezone.now())

    def test_accept_schedules_every_topic_within_the_weeks(self):
        from learning import planning

        planning.save(self.profile, self.user)
        rows = self.profile.plan["rows"]
        self.assertEqual(len(rows), SpecItem.objects.count())
        self.assertTrue(all(1 <= r["week"] <= self.profile.plan["weeks"] for r in rows))
        self.assertIsNotNone(self.profile.plan_accepted_at)

    def test_behind_then_replan_is_on_track(self):
        from learning import planning

        start = timezone.localdate() - timedelta(days=60)
        planning.save(self.profile, self.user, today=start)
        status = planning.progress(self.user, self.profile)
        self.assertFalse(status["on_track"])
        self.assertGreater(status["overdue"], 0)
        planning.save(self.profile, self.user, "replanned")
        status = planning.progress(self.user, self.profile)
        self.assertTrue(status["on_track"])
        self.assertEqual(status["start"], timezone.localdate())

    def test_changing_exam_date_rebuilds_the_schedule(self):
        from learning import planning

        planning.save(self.profile, self.user, today=timezone.localdate() - timedelta(days=30))
        self.client.force_login(self.user)
        new_date = (timezone.localdate() + timedelta(days=70)).isoformat()
        self.client.post("/start/", {"exam_date": new_date, "hours_per_week": 10})
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.plan["reason"], "settings")
        self.assertEqual(self.profile.plan["start"], timezone.localdate().isoformat())
        self.assertEqual(self.profile.plan["weeks"], 10)
