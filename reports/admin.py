from django.contrib import admin

from .models import ReadinessSnapshot, SharedReport


@admin.register(ReadinessSnapshot)
class ReadinessSnapshotAdmin(admin.ModelAdmin):
    list_display = ["student", "taken_on", "zone", "low", "mid", "high", "coverage", "evidence"]
    list_filter = ["zone"]
    date_hierarchy = "taken_on"


@admin.register(SharedReport)
class SharedReportAdmin(admin.ModelAdmin):
    list_display = ["student", "kind", "recipient", "live", "expires_at", "revoked_at", "views", "created_at"]
    list_filter = ["kind", "live"]
    search_fields = ["student__username", "recipient", "token"]
    readonly_fields = ["token", "views"]
