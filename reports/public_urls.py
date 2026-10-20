from django.urls import path

from . import views

urlpatterns = [path("", views.public, name="public_report")]
