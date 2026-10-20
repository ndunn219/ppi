from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from learning import views as learning_views

admin.site.site_header = "PE Prep admin"
admin.site.site_title = "PE Prep admin"
admin.site.index_title = "Course content and student records"

urlpatterns = [
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/signup/", learning_views.signup, name="signup"),
    path("reports/", include("reports.urls")),
    path("review/", include("curriculum.urls")),
    path("r/<str:token>/", include("reports.public_urls")),
    path("", include("learning.urls")),
]
