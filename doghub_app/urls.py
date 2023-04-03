# from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetCompleteView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.home, name="home"),
    path("register", views.register_request, name="register"),
    path("register_details", views.register_details_request, name="register_details"),
    path("login", views.login_request, name="login"),
    path("events", views.events, name="events"),
    path("logout", views.logout_request, name="logout"),
    path("dogProfilesCreate", views.dog_profile_create, name="dogProfileCreate"),
    path("user_profile", views.user_profile, name="user_profile"),
    path("user_profile_edit", views.user_profile_edit, name="user_profile_edit"),
    path("dog_profile_edit/<int:pk>/", views.dog_profile_edit, name="dog_profile_edit"),
    path("dog_profile_add", views.dog_profile_add, name="dog_profile_add"),
    path(
        "dog_profile_delete/<int:pk>/",
        views.dog_profile_delete,
        name="dog_profile_delete",
    ),
    path("add_post", views.add_post, name="add_post"),
    path(
        "forgot_password_email",
        views.forgot_password_email,
        name="forgot_password_email",
    ),
    path(
        "forgot_password_page", views.forgot_password_page, name="forgot_password_page"
    ),
    path(
        "reset_password/confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset_password/complete/",
        PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("verify-email/<token>", views.verify_email, name="verify-email"),
    path("public-profile/<email>", views.public_profile, name="public-profile"),
    path("search-user", views.search_user, name="search-user"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
