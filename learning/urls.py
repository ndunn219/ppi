from django.urls import path

from . import views, views_practice as practice

app_name = "learning"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("start/", views.onboarding, name="onboarding"),
    path("plan/", views.plan, name="plan"),
    path("plan/accept/", views.accept_plan, name="accept_plan"),
    path("plan/replan/", views.replan, name="replan"),
    path("topics/", views.topics, name="topics"),
    path("topics/<str:code>/", views.topic, name="topic"),
    path("learn/<str:code>/", practice.tutorial, name="tutorial"),
    path("tutorial/check/<int:pk>/", practice.tutorial_check, name="tutorial_check"),
    path("study/<str:code>/", practice.study, name="study"),
    path("study/<str:code>/answer/", practice.study_answer, name="study_answer"),
    path("study/<str:code>/next/", practice.study_next, name="study_next"),
    path("practice/", practice.practice, name="practice"),
    path("practice/start/", practice.start, name="start"),
    path("practice/explain/", practice.explain, name="explain"),
    path("s/<int:pk>/", practice.session_view, name="session"),
    path("s/<int:pk>/answer/", practice.answer, name="answer"),
    path("s/<int:pk>/finish/", practice.finish, name="finish"),
    path("s/<int:pk>/results/", practice.results, name="results"),
    path("cards/", practice.cards, name="cards"),
    path("cards/<int:pk>/grade/", practice.card_grade, name="card_grade"),
    path("errors/", practice.errors, name="errors"),
    path("attempt/<int:pk>/audit/", practice.audit, name="audit"),
    path("simulation/", views.simulation, name="simulation"),
    path("references/", views.references, name="references"),
    path("help/", views.help_page, name="help"),
]
