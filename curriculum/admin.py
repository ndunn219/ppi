from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html, format_html_join
from django_docutils.lib.publisher import publish_html_from_source

from .generation import draw
from .models import (
    Card,
    ExamModule,
    Lesson,
    LookupDrill,
    ProblemTemplate,
    Reference,
    ReferenceLocation,
    SpecArea,
    SpecItem,
    TutorialBlock,
)


@admin.action(description="Mark as reviewed by a licensed PE")
def mark_reviewed(modeladmin, request, queryset):
    name = request.user.get_full_name() or request.user.username
    queryset.update(reviewed_by_pe=True, reviewer=name, reviewed_on=timezone.localdate())


class SpecAreaInline(admin.TabularInline):
    model = SpecArea
    extra = 0
    fields = ["code", "name", "weight", "order"]


@admin.register(ExamModule)
class ExamModuleAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active", "total_weight"]
    prepopulated_fields = {"slug": ["name"]}
    inlines = [SpecAreaInline]

    @admin.display(description="Weights sum to")
    def total_weight(self, obj):
        return sum(a.weight for a in obj.areas.all())


class SpecItemInline(admin.TabularInline):
    model = SpecItem
    extra = 0
    fields = ["code", "name", "method_name", "order"]
    show_change_link = True


@admin.register(SpecArea)
class SpecAreaAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "module", "weight", "order"]
    list_filter = ["module"]
    list_editable = ["weight", "order"]
    inlines = [SpecItemInline]


class ReferenceLocationInline(admin.TabularInline):
    model = ReferenceLocation
    extra = 0


class CardInline(admin.TabularInline):
    model = Card
    extra = 0
    fields = ["kind", "front", "back", "order"]


class LookupDrillInline(admin.StackedInline):
    model = LookupDrill
    extra = 0


@admin.register(SpecItem)
class SpecItemAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "area", "template_count", "card_count", "has_lesson"]
    list_filter = ["area"]
    search_fields = ["code", "name", "method_name"]
    inlines = [ReferenceLocationInline, CardInline, LookupDrillInline]

    @admin.display(description="Templates")
    def template_count(self, obj):
        return obj.templates.count()

    @admin.display(description="Cards")
    def card_count(self, obj):
        return obj.cards.count()

    @admin.display(boolean=True, description="Lesson")
    def has_lesson(self, obj):
        return hasattr(obj, "lesson")


@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ["short_name", "title", "publisher", "is_public_domain"]
    list_filter = ["is_public_domain"]


@admin.register(ReferenceLocation)
class ReferenceLocationAdmin(admin.ModelAdmin):
    list_display = ["spec_item", "reference", "locator", "what_is_there"]
    list_filter = ["reference", "spec_item__area"]
    search_fields = ["locator", "what_is_there", "search_terms"]


class TutorialBlockInline(admin.StackedInline):
    model = TutorialBlock
    extra = 0
    fields = ["order", "kind", "title", "body", "widget", "config", "prompt", "choices", "answer", "tolerance", "unit", "hint", "explanation", "steps"]
    ordering = ["order"]


@admin.register(TutorialBlock)
class TutorialBlockAdmin(admin.ModelAdmin):
    list_display = ["__str__", "kind", "widget", "lesson"]
    list_filter = ["kind", "lesson__spec_item__area"]
    search_fields = ["title", "body", "prompt", "explanation"]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    inlines = [TutorialBlockInline]
    list_display = ["title", "spec_item", "minutes", "reviewed_by_pe", "reviewed_on"]
    list_filter = ["reviewed_by_pe", "spec_item__area"]
    search_fields = ["title", "body"]
    actions = [mark_reviewed]
    readonly_fields = ["preview"]
    fields = ["spec_item", "title", "minutes", "body", "preview", "reviewed_by_pe", "reviewer", "reviewed_on"]

    @admin.display(description="Rendered")
    def preview(self, obj):
        if not obj.body:
            return "—"
        return format_html('<div class="rst-preview">{}</div>', publish_html_from_source(obj.body, show_title=False))


@admin.register(ProblemTemplate)
class ProblemTemplateAdmin(admin.ModelAdmin):
    list_display = ["title", "spec_item", "solver", "difficulty", "est_minutes", "is_active", "reviewed_by_pe"]
    list_filter = ["is_active", "reviewed_by_pe", "difficulty", "spec_item__area"]
    search_fields = ["title", "slug", "stem"]
    prepopulated_fields = {"slug": ["title"]}
    actions = [mark_reviewed]
    readonly_fields = ["sample"]

    @admin.display(description="A freshly drawn instance")
    def sample(self, obj):
        if not obj.pk:
            return "Save first to see a sample."
        try:
            d = draw(obj)
        except Exception as exc:  # show the author what broke
            return f"Could not draw: {exc}"
        choices = format_html_join(
            "", "<li>{}{}</li>", ((c["label"], f" — {c['cause']}: {c['note']}" if c["cause"] else " — correct") for c in d["choices"])
        )
        steps = format_html_join("", "<li>{}</li>", ((s["text"],) for s in d["steps"]))
        return format_html("<p>{}</p><ul>{}</ul><ol>{}</ol>", d["stem"], choices, steps)


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ["front", "kind", "spec_item"]
    list_filter = ["kind", "spec_item__area"]
    search_fields = ["front", "back"]


@admin.register(LookupDrill)
class LookupDrillAdmin(admin.ModelAdmin):
    list_display = ["prompt", "answer", "spec_item", "seconds_target"]
    list_filter = ["spec_item__area"]
    search_fields = ["prompt", "answer"]
