"""Tutorials: every module validates, seeds, renders and logs checks."""

import json
import shutil
import subprocess
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from curriculum import tutorials
from curriculum.models import ExamModule, SpecItem, TutorialBlock
from learning.models import Attempt, StudentProfile


class TutorialTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_course", verbosity=0)

    def setUp(self):
        self.user = User.objects.create_user("t")
        StudentProfile.objects.create(user=self.user, module=ExamModule.objects.first())
        self.client.force_login(self.user)

    def test_modules_validate(self):
        call_command("check_tutorials", verbosity=0)

    def test_widgets_render_in_node(self):
        if not shutil.which("node"):
            self.skipTest("node is not installed")
        out = Path(settings.BASE_DIR, "build", "widget-configs.json")
        out.parent.mkdir(exist_ok=True)
        call_command("check_tutorials", export=str(out), verbosity=0)
        result = subprocess.run(["node", "scripts/check_widgets.js", str(out)], cwd=settings.BASE_DIR, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout[-2000:])

    def test_every_tutorial_seeded_and_renders(self):
        for code, tut in tutorials.load_all().items():
            item = SpecItem.objects.get(code=code)
            self.assertEqual(item.lesson.blocks.count(), len(tut["blocks"]), code)
            resp = self.client.get(f"/learn/{code}/")
            self.assertEqual(resp.status_code, 200, code)
            self.assertContains(resp, f"js/widgets/{code.lower()}.js")
            self.assertContains(resp, "data-check")

    def test_check_is_logged_but_not_counted(self):
        block = TutorialBlock.objects.filter(kind="check").first()
        resp = self.client.post(
            f"/tutorial/check/{block.id}/", json.dumps({"correct": True, "response": "0", "tries": 1}), content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        att = Attempt.objects.get(student=self.user, kind=Attempt.Kind.CHECK)
        self.assertTrue(att.is_correct)
        self.assertFalse(att.counts_for_mastery)
