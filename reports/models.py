"""Readiness snapshots and the reports students share."""

import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone

from learning.models import PracticeSession


def new_token():
    return secrets.token_urlsafe(18)


class Zone(models.TextChoices):
    NONE = "none", "No zone yet"
    NOT_YET = "not_yet", "Not yet"
    BUILDING = "building", "Building"
    APPROACHING = "approaching", "Approaching"
    READY = "ready", "Ready"


class ReadinessSnapshot(models.Model):
    """The readiness estimate as it stood on one day, for trend lines."""

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="readiness")
    taken_on = models.DateField(default=timezone.localdate)
    zone = models.CharField(max_length=12, choices=Zone.choices)
    low = models.FloatField(null=True, blank=True)
    mid = models.FloatField(null=True, blank=True)
    high = models.FloatField(null=True, blank=True)
    coverage = models.FloatField(help_text="Share of exam weight at Practicing or above.")
    evidence = models.PositiveIntegerField(default=0, help_text="Problems behind the estimate.")
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = [("student", "taken_on")]
        ordering = ["-taken_on"]

    def __str__(self):
        return f"{self.student} {self.taken_on}: {self.get_zone_display()}"


class SharedReport(models.Model):
    """A link a student hands to an employer, mentor or study partner."""

    class Kind(models.TextChoices):
        WEEKLY = "weekly", "Weekly progress"
        READINESS = "readiness", "Readiness report"
        SIMULATION = "simulation", "Simulation report"

    SECTIONS = [
        ("estimate", "Readiness estimate"),
        ("coverage", "Coverage map"),
        ("accuracy", "Demonstrated accuracy"),
        ("pace", "Pace"),
        ("lookup", "Lookup skill"),
        ("errors", "Error profile"),
        ("simulations", "Simulation history"),
        ("study", "Study record"),
        ("focus", "Recommended focus"),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shared_reports")
    kind = models.CharField(max_length=12, choices=Kind.choices)
    token = models.CharField(max_length=40, unique=True, default=new_token)
    simulation = models.ForeignKey(PracticeSession, null=True, blank=True, on_delete=models.CASCADE)
    recipient = models.CharField(max_length=120, blank=True, help_text="Who it is for, as a note to the student.")
    sections = models.JSONField(default=list, help_text="Section keys to include.")
    live = models.BooleanField(
        default=False, help_text="Live links always show current data; others show the snapshot taken when shared."
    )
    snapshot = models.JSONField(default=dict, blank=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_kind_display()} for {self.recipient or 'link'} · {self.student}"

    @property
    def is_active(self):
        return self.revoked_at is None and self.expires_at > timezone.now()
