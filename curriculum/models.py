"""The course's content: the exam specification and what teaches it.

Everything a student practices hangs off a SpecItem, one row of the exam
specification. Lessons are written in reStructuredText and rendered with
django-docutils. Problem templates hold a stem and a parameter range; a
solver in curriculum.solvers computes the answer, the worked steps and the
wrong answers that common mistakes produce, so new numbers never need a
new answer key.
"""

from django.db import models


class ErrorCause(models.TextChoices):
    """Why an answer was wrong. Shared by distractors and attempts."""

    CONCEPT = "concept", "Concept"
    METHOD = "method", "Method choice"
    LOOKUP = "lookup", "Wrong lookup"
    SETUP = "setup", "Setup"
    ARITHMETIC = "arithmetic", "Arithmetic"
    UNITS = "units", "Units"
    MISREAD = "misread", "Misreading"


class ExamModule(models.Model):
    """One NCEES exam module, e.g. PE Civil: Transportation."""

    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SpecArea(models.Model):
    """A knowledge area of the exam specification, weighted by its share
    of exam questions."""

    module = models.ForeignKey(ExamModule, on_delete=models.CASCADE, related_name="areas")
    code = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=160)
    weight = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        help_text="Share of exam questions, 0 to 1. Placeholder until checked against the current NCEES specification.",
    )
    order = models.PositiveSmallIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["module", "order"]

    def __str__(self):
        return f"{self.code} {self.name}"


class SpecItem(models.Model):
    """One teachable item of the specification. Mastery is tracked here."""

    area = models.ForeignKey(SpecArea, on_delete=models.CASCADE, related_name="items")
    code = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=160)
    method_name = models.CharField(
        max_length=160, help_text="The method in a few words, used as an option in Which method? sets."
    )
    summary = models.TextField(blank=True)
    cues = models.TextField(blank=True, help_text="Words in a question that signal this method, one per line.")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["area__order", "order"]

    def __str__(self):
        return f"{self.code} {self.name}"

    @property
    def cue_list(self):
        return [c.strip() for c in self.cues.splitlines() if c.strip()]


class Reference(models.Model):
    """A reference document the exam supplies, or a public-domain manual."""

    short_name = models.CharField(max_length=40, unique=True)
    title = models.CharField(max_length=200)
    publisher = models.CharField(max_length=120, blank=True)
    is_public_domain = models.BooleanField(
        default=False, help_text="Only public-domain documents may be linked or shown in the course."
    )
    url = models.URLField(blank=True, help_text="Public link, for public-domain documents only.")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["short_name"]

    def __str__(self):
        return self.short_name


class ReferenceLocation(models.Model):
    """Where a spec item lives in a reference: a pointer, never the text."""

    spec_item = models.ForeignKey(SpecItem, on_delete=models.CASCADE, related_name="locations")
    reference = models.ForeignKey(Reference, on_delete=models.CASCADE, related_name="locations")
    locator = models.CharField(max_length=200, help_text="Chapter, part or section, as a student would find it.")
    what_is_there = models.CharField(max_length=240)
    search_terms = models.CharField(max_length=240, blank=True, help_text="Comma-separated words that find it fastest.")

    class Meta:
        ordering = ["spec_item", "reference"]

    def __str__(self):
        return f"{self.reference} · {self.locator}"

    @property
    def search_term_list(self):
        return [t.strip() for t in self.search_terms.split(",") if t.strip()]


class ReviewedContent(models.Model):
    """Fields every piece of content carries for the licensed-PE review."""

    reviewed_by_pe = models.BooleanField(default=False)
    reviewer = models.CharField(max_length=120, blank=True)
    reviewed_on = models.DateField(null=True, blank=True)

    class Meta:
        abstract = True


class Lesson(ReviewedContent):
    """The micro-lesson for a spec item, in reStructuredText."""

    spec_item = models.OneToOneField(SpecItem, on_delete=models.CASCADE, related_name="lesson")
    title = models.CharField(max_length=160)
    minutes = models.PositiveSmallIntegerField(default=8)
    body = models.TextField(help_text="reStructuredText.")

    def __str__(self):
        return self.title


class ProblemTemplate(ReviewedContent):
    """A problem whose numbers change every time it is drawn."""

    class Difficulty(models.IntegerChoices):
        CORE = 1, "Core"
        STANDARD = 2, "Standard"
        STRETCH = 3, "Stretch"

    spec_item = models.ForeignKey(SpecItem, on_delete=models.CASCADE, related_name="templates")
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=160)
    stem = models.TextField(help_text="Python format string; {name} slots take the drawn parameters.")
    solver = models.CharField(max_length=60, help_text="Name of a function in curriculum.solvers.")
    params = models.JSONField(
        default=dict,
        help_text='Ranges to draw from: {"V": [40, 70, 5]} is 40 to 70 in steps of 5; {"G": {"choices": [-3, 3]}}.',
    )
    answer_unit = models.CharField(max_length=24, blank=True)
    decimals = models.PositiveSmallIntegerField(default=0)
    min_gap = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Smallest allowed gap between choices. Blank means 3% of the larger value.",
    )
    est_minutes = models.DecimalField(max_digits=4, decimal_places=1, default=5)
    difficulty = models.PositiveSmallIntegerField(choices=Difficulty.choices, default=Difficulty.STANDARD)
    explain_prompt = models.CharField(
        max_length=240, blank=True, help_text="Explain-it-back question about one step of the method."
    )
    explain_answer = models.TextField(blank=True, help_text="The model explanation shown after the student answers.")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["spec_item", "slug"]

    def __str__(self):
        return self.title


class Card(models.Model):
    """A spaced-repetition flashcard."""

    class Kind(models.TextChoices):
        FORMULA = "formula", "Formula"
        VARIABLES = "variables", "Variables and units"
        METHOD = "method", "When to use it"
        WHERE = "where", "Where it lives"

    spec_item = models.ForeignKey(SpecItem, on_delete=models.CASCADE, related_name="cards")
    kind = models.CharField(max_length=12, choices=Kind.choices)
    front = models.TextField()
    back = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["spec_item", "order"]

    def __str__(self):
        return f"{self.spec_item.code} {self.get_kind_display()}: {self.front[:50]}"


class LookupDrill(models.Model):
    """A "where would you look?" question for lookup sprints."""

    spec_item = models.ForeignKey(SpecItem, on_delete=models.CASCADE, related_name="lookup_drills")
    prompt = models.CharField(max_length=240)
    answer = models.CharField(max_length=200)
    wrong_1 = models.CharField(max_length=200)
    wrong_2 = models.CharField(max_length=200)
    wrong_3 = models.CharField(max_length=200)
    explanation = models.TextField(blank=True)
    seconds_target = models.PositiveSmallIntegerField(default=30)

    class Meta:
        ordering = ["spec_item", "id"]

    def __str__(self):
        return self.prompt[:80]
