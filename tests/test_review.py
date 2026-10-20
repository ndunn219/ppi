"""PE review: approvals cover exact content, lapse on change, and only reviewers decide."""

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from curriculum import review
from curriculum.models import ContentReviewer, ExamModule, ReviewEvent, ReviewStatus, SpecItem
from learning.models import StudentProfile


class ReviewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_course", verbosity=0)

    def setUp(self):
        self.item = SpecItem.objects.get(code="VD1")
        self.pe = User.objects.create_user("pe", first_name="Pat", last_name="Lee")
        self.reviewer = ContentReviewer.objects.create(user=self.pe, name="Pat Lee", license_state="OH", license_number="PE.12345")
        self.student = User.objects.create_user("s")
        StudentProfile.objects.create(user=self.student, module=ExamModule.objects.first())

    def unit(self, kind):
        item = SpecItem.objects.get(pk=self.item.pk)  # fresh, so related objects aren't cached
        return next(u for u in review.units(item) if u["kind"] == kind)

    def test_everything_starts_unreviewed(self):
        summary = review.course_summary()
        self.assertTrue(summary["none"])
        self.assertTrue(all(u["state"] == "unreviewed" for u in review.units(self.item)))

    def test_approval_stamps_every_object_and_logs(self):
        u = self.unit("cards")
        review.record(u, self.item, self.pe, self.reviewer, ReviewStatus.APPROVED)
        self.assertEqual(self.unit("cards")["state"], "approved")
        card = u["objects"][0]
        card.refresh_from_db()
        self.assertEqual(card.reviewer_license, "OH PE PE.12345")
        self.assertEqual(ReviewEvent.objects.count(), len(u["objects"]))

    def test_editing_a_tutorial_block_makes_the_approval_stale(self):
        u = self.unit("lesson")
        review.record(u, self.item, self.pe, self.reviewer, ReviewStatus.APPROVED)
        self.assertEqual(self.unit("lesson")["state"], "approved")
        block = SpecItem.objects.get(pk=self.item.pk).lesson.blocks.filter(kind="check").first()
        block.explanation += "\nEdited."
        block.save()
        self.assertEqual(self.unit("lesson")["state"], "stale")

    def test_identical_reseed_keeps_the_approval(self):
        u = self.unit("lesson")
        review.record(u, self.item, self.pe, self.reviewer, ReviewStatus.APPROVED)
        call_command("seed_course", update=True, verbosity=0)
        self.assertEqual(self.unit("lesson")["state"], "approved")

    def test_template_approval_covers_solver_code(self):
        t = self.unit("template")["objects"][0]
        before = review.content_hash(t)
        t.solver = "crest_length"
        self.assertNotEqual(before, review.content_hash(t))

    def test_only_reviewers_can_decide(self):
        key = self.unit("drills")["key"]
        self.client.force_login(self.student)
        self.assertEqual(self.client.get("/review/").status_code, 403)
        self.assertEqual(self.client.post(f"/review/{key}/", {"decision": "approved"}).status_code, 403)
        self.client.force_login(self.pe)
        self.assertEqual(self.client.get(f"/review/{key}/").status_code, 200)
        self.client.post(f"/review/{key}/", {"decision": "approved"})
        self.assertEqual(self.unit("drills")["state"], "approved")

    def test_needs_changes_requires_notes(self):
        key = self.unit("lesson")["key"]
        self.client.force_login(self.pe)
        self.client.post(f"/review/{key}/", {"decision": "changes", "notes": ""})
        self.assertEqual(self.unit("lesson")["state"], "unreviewed")
        self.client.post(f"/review/{key}/", {"decision": "changes", "notes": "Fix the e offset label."})
        self.assertEqual(self.unit("lesson")["state"], "changes")

    def test_every_review_page_renders(self):
        self.client.force_login(self.pe)
        for item in SpecItem.objects.all():
            for u in review.units(item):
                self.assertEqual(self.client.get(f"/review/{u['key']}/").status_code, 200, u["key"])

    def test_students_see_badges(self):
        self.client.force_login(self.student)
        resp = self.client.get("/learn/VD1/")
        self.assertContains(resp, "Not yet PE-reviewed")
        review.record(self.unit("lesson"), self.item, self.pe, self.reviewer, ReviewStatus.APPROVED)
        resp = self.client.get("/learn/VD1/")
        self.assertContains(resp, "Reviewed by Pat Lee, OH PE PE.12345")
        self.assertContains(self.client.get("/help/"), "How the content is checked")
        self.assertContains(self.client.get("/topics/VD1/"), "1 of 5 parts of this topic reviewed")
        self.assertContains(self.client.get("/topics/"), "Partly PE-reviewed")
