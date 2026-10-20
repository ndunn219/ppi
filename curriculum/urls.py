from django.urls import path

from . import views

app_name = "review"

urlpatterns = [
    path("", views.queue, name="queue"),
    path("<str:key>/", views.unit, name="unit"),
]
