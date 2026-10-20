from django.contrib import admin

from .models import (
    Attempt,
    CardReview,
    ErrorReplay,
    ItemReview,
    LessonProgress,
    Mastery,
    PracticeSession,
    ProblemInstance,
    StudentProfile,
)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "module", "exam_date", "hours_per_week", "plan_accepted_at", "created_at"]
    list_filter = ["module"]
    search_fields = ["user__username", "user__email"]


class AttemptInline(admin.TabularInline):
    model = Attempt
    extra = 0
    fields = ["position", "kind", "spec_item", "is_correct", "cause", "seconds", "hint_used"]
    readonly_fields = fields
    can_delete = False
    show_change_link = True


@admin.register(PracticeSession)
class PracticeSessionAdmin(admin.ModelAdmin):
    list_display = ["kind", "student", "spec_item", "question_count", "started_at", "finished_at"]
    list_filter = ["kind"]
    search_fields = ["student__username"]
    date_hierarchy = "started_at"
    inlines = [AttemptInline]

    @admin.display(description="Questions")
    def question_count(self, obj):
        return len(obj.items)


@admin.register(ProblemInstance)
class ProblemInstanceAdmin(admin.ModelAdmin):
    list_display = ["__str__", "template", "answer_label", "created_at"]
    list_filter = ["template__spec_item__area"]
    search_fields = ["stem", "template__slug"]


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ["student", "kind", "spec_item", "is_correct", "cause", "seconds", "hint_used", "audit_source", "created_at"]
    list_filter = ["kind", "is_correct", "cause", "hint_used", "audit_source", "spec_item__area"]
    search_fields = ["student__username", "response", "audit"]
    date_hierarchy = "created_at"
    raw_id_fields = ["session", "instance"]


@admin.register(CardReview)
class CardReviewAdmin(admin.ModelAdmin):
    list_display = ["student", "card", "due", "interval_days", "ease", "reps", "lapses"]
    list_filter = ["due"]
    search_fields = ["student__username", "card__front"]


@admin.register(ItemReview)
class ItemReviewAdmin(admin.ModelAdmin):
    list_display = ["student", "spec_item", "due", "rung", "last_result"]
    list_filter = ["spec_item__area"]


@admin.register(Mastery)
class MasteryAdmin(admin.ModelAdmin):
    list_display = ["student", "spec_item", "level", "earned_level", "decayed", "accuracy", "attempts_counted", "median_seconds"]
    list_filter = ["level", "decayed", "spec_item__area"]
    search_fields = ["student__username"]


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ["student", "spec_item", "stage", "tested_out", "started_at", "completed_at"]
    list_filter = ["stage", "tested_out"]


@admin.register(ErrorReplay)
class ErrorReplayAdmin(admin.ModelAdmin):
    list_display = ["student", "template", "cause", "solved", "opened_at", "closed_at"]
    list_filter = ["cause"]
