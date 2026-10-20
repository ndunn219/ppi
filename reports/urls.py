from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("", views.index, name="index"),
    path("readiness/", views.readiness_view, name="readiness"),
    path("weekly/", views.weekly_view, name="weekly"),
    path("simulation/<int:pk>/", views.simulation_view, name="simulation"),
    path("share/", views.share, name="share"),
    path("share/<int:pk>/revoke/", views.revoke, name="revoke"),
]
