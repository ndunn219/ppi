"""What a student does in the course, and what it shows.

Attempts are the evidence: every answer, with its time, hint use and the
cause of a miss. Mastery, readiness and every report are computed from
attempts (learning.mastery, reports.readiness) so nothing is credited for
time alone.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone

from curriculum.models import Card, ErrorCause, ExamModule, LookupDrill, ProblemTemplate, SpecItem


class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    module = models.ForeignKey(ExamModule, on_delete=models.PROTECT)
    exam_date = models.DateField(null=True, blank=True)
    hours_per_week = models.PositiveSmallIntegerField(default=9)
    plan_accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} ({self.module})"


class LevelChoices(models.IntegerChoices):
    NOT_STARTED = 0, "Not started"
    INTRODUCED = 1, "Introduced"
    PRACTICING = 2, "Practicing"
    PROFICIENT = 3, "Proficient"
    EXAM_READY = 4, "Exam-ready"


class PracticeSession(models.Model):
    """One sitting of one mode. Its `items` list is the question order."""

    class Kind(models.TextChoices):
        DIAGNOSTIC = "diagnostic", "Diagnostic"
        LESSON = "lesson", "Lesson"
        DRILL = "drill", "Parametric drill"
        WARMUP = "warmup", "Daily warm-up"
        LOOKUP = "lookup", "Lookup sprint"
        METHOD = "method", "Which method?"
        ESTIMATE = "estimate", "Estimate first"
        SPOT_ERROR = "spot_error", "Spot the error"
        REPLAY = "replay", "Error replay"
        UNITS = "units", "Units and conversions"
        TIMED_BLOCK = "timed_block", "Mixed timed block"
        HALF_EXAM = "half_exam", "Half-exam set"
        FULL_EXAM = "full_exam", "Full exam simulation"

    EXAM_STYLE = {Kind.DIAGNOSTIC, Kind.TIMED_BLOCK, Kind.HALF_EXAM, Kind.FULL_EXAM}

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="practice_sessions")
    kind = models.CharField(max_length=16, choices=Kind.choices)
    spec_item = models.ForeignKey(SpecItem, null=True, blank=True, on_delete=models.SET_NULL)
    items = models.JSONField(default=list, help_text="Ordered question descriptors.")
    flags = models.JSONField(default=list, blank=True, help_text="Positions flagged for review.")
    time_limit_seconds = models.PositiveIntegerField(null=True, blank=True)
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.get_kind_display()} · {self.student} · {self.started_at:%Y-%m-%d}"

    @property
    def is_exam_style(self):
        return self.kind in self.EXAM_STYLE

    @property
    def is_finished(self):
        return self.finished_at is not None

    def deadline(self):
        if not self.time_limit_seconds:
            return None
        return self.started_at + timezone.timedelta(seconds=self.time_limit_seconds)


class ProblemInstance(models.Model):
    """One drawing of a template: its numbers, choices and worked steps."""

    template = models.ForeignKey(ProblemTemplate, on_delete=models.CASCADE, related_name="instances")
    params = models.JSONField()
    stem = models.TextField()
    answer = models.FloatField()
    answer_label = models.CharField(max_length=60)
    choices = models.JSONField()
    steps = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.template.slug} #{self.pk}"

    def choice(self, index):
        return self.choices[index]


class Attempt(models.Model):
    """One answer to one question."""

    class Kind(models.TextChoices):
        PROBLEM = "problem", "Problem"
        LOOKUP = "lookup", "Lookup"
        METHOD = "method", "Which method?"
        ESTIMATE = "estimate", "Estimate"
        SPOT_ERROR = "spot_error", "Spot the error"
        UNITS = "units", "Units"
        EXPLAIN = "explain", "Explain it back"
        CHECK = "check", "Tutorial check"

    class AuditSource(models.TextChoices):
        NONE = "", "None"
        SELF = "self", "Self-audit"
        AI = "ai", "AI tutor"

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attempts")
    session = models.ForeignKey(PracticeSession, null=True, blank=True, on_delete=models.CASCADE, related_name="attempts")
    position = models.PositiveSmallIntegerField(null=True, blank=True)
    kind = models.CharField(max_length=12, choices=Kind.choices, default=Kind.PROBLEM)
    spec_item = models.ForeignKey(SpecItem, null=True, blank=True, on_delete=models.CASCADE, related_name="attempts")
    instance = models.ForeignKey(ProblemInstance, null=True, blank=True, on_delete=models.SET_NULL)
    lookup_drill = models.ForeignKey(LookupDrill, null=True, blank=True, on_delete=models.SET_NULL)
    response = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    cause = models.CharField(max_length=12, choices=ErrorCause.choices, blank=True)
    seconds = models.PositiveIntegerField(default=0)
    hint_used = models.BooleanField(default=False)
    cited_reference = models.CharField(max_length=40, blank=True, help_text="Reference the student says they used.")
    cited_correct = models.BooleanField(null=True, blank=True)
    counts_for_mastery = models.BooleanField(default=True)
    audit = models.TextField(blank=True)
    audit_source = models.CharField(max_length=4, choices=AuditSource.choices, blank=True)
    extra = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["student", "spec_item", "created_at"])]

    def __str__(self):
        mark = "✓" if self.is_correct else "✗"
        code = self.spec_item.code if self.spec_item_id else "—"
        return f"{mark} {code} {self.get_kind_display()} · {self.student}"

    @property
    def weight(self):
        """Hints halve an attempt's credit toward mastery."""
        return 0.5 if self.hint_used else 1.0


class CardReview(models.Model):
    """Spaced-repetition state for one card and one student (SM-2 style)."""

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="card_reviews")
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="reviews")
    due = models.DateField(default=timezone.localdate)
    interval_days = models.PositiveSmallIntegerField(default=0)
    ease = models.FloatField(default=2.5)
    reps = models.PositiveSmallIntegerField(default=0)
    lapses = models.PositiveSmallIntegerField(default=0)
    last_reviewed = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [("student", "card")]
        ordering = ["due"]

    def __str__(self):
        return f"{self.card} → {self.due}"


class ItemReview(models.Model):
    """When a spec item's problems next come back in spaced review."""

    LADDER = [1, 3, 7, 14, 30]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="item_reviews")
    spec_item = models.ForeignKey(SpecItem, on_delete=models.CASCADE)
    due = models.DateField(default=timezone.localdate)
    rung = models.PositiveSmallIntegerField(default=0, help_text="Position on the 1, 3, 7, 14, 30-day ladder.")
    last_result = models.BooleanField(null=True, blank=True)
    last_reviewed = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [("student", "spec_item")]
        ordering = ["due"]

    def __str__(self):
        return f"{self.spec_item.code} → {self.due}"


class Mastery(models.Model):
    """The computed mastery level of one spec item for one student."""

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mastery")
    spec_item = models.ForeignKey(SpecItem, on_delete=models.CASCADE)
    level = models.PositiveSmallIntegerField(choices=LevelChoices.choices, default=LevelChoices.NOT_STARTED)
    earned_level = models.PositiveSmallIntegerField(
        choices=LevelChoices.choices, default=LevelChoices.NOT_STARTED, help_text="Level before decay."
    )
    accuracy = models.FloatField(null=True, blank=True, help_text="Weighted accuracy over the recent window.")
    attempts_counted = models.FloatField(default=0)
    median_seconds = models.FloatField(null=True, blank=True)
    lookup_rate = models.FloatField(null=True, blank=True)
    decayed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("student", "spec_item")]
        verbose_name_plural = "mastery"

    def __str__(self):
        return f"{self.spec_item.code}: {self.get_level_display()} · {self.student}"


class LessonProgress(models.Model):
    """Where a student is in the learning loop for one spec item."""

    class Stage(models.TextChoices):
        PRIME = "prime", "Prime"
        TESTOUT = "testout", "Test-out"
        LEARN = "learn", "Learn"
        FADE = "fade", "Worked example"
        TRY = "try", "Try"
        DONE = "done", "Done"

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lesson_progress")
    spec_item = models.ForeignKey(SpecItem, on_delete=models.CASCADE)
    stage = models.CharField(max_length=8, choices=Stage.choices, default=Stage.PRIME)
    fade_level = models.PositiveSmallIntegerField(default=0)
    tested_out = models.BooleanField(default=False)
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [("student", "spec_item")]
        verbose_name_plural = "lesson progress"

    def __str__(self):
        return f"{self.spec_item.code}: {self.get_stage_display()} · {self.student}"


class ErrorReplay(models.Model):
    """A missed problem type that keeps coming back until solved twice."""

    REQUIRED = 2

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="replays")
    template = models.ForeignKey(ProblemTemplate, on_delete=models.CASCADE)
    cause = models.CharField(max_length=12, choices=ErrorCause.choices, blank=True)
    solved = models.PositiveSmallIntegerField(default=0)
    opened_at = models.DateTimeField(default=timezone.now)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["closed_at", "-opened_at"]

    def __str__(self):
        return f"{self.template.slug} ({self.solved}/{self.REQUIRED}) · {self.student}"

    @property
    def is_open(self):
        return self.closed_at is None
