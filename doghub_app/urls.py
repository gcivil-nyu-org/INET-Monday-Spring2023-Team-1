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
    path("inbox", views.inbox, name="inbox"),
    path(
        "dog_profile_delete/<name>/",
        views.dog_profile_delete,
        name="dog_profile_delete",
    ),
    path("add_post", views.add_post, name="add_post"),
    path("add_service", views.add_service, name="add_service"),
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
    path("rsvp_event/<int:pk>/", views.rsvp_event, name="rsvp_event"),
    path("friends/", views.friends, name="friends"),
    path("add-friend/<str:email>/", views.add_friend, name="add_friend"),
    path("friend_requests/", views.friend_requests, name="friend_requests"),
    path(
        "accept_friend_request/<int:fid>/",
        views.accept_friend_request,
        name="accept_friend_request",
    ),
    path(
        "decline_friend_request/<int:fid>/",
        views.decline_friend_request,
        name="decline_friend_request",
    ),
    path("create-group/", views.create_group, name="create_group"),
    path("join-group/", views.join_group, name="join_group"),
    path("my-groups/", views.my_groups, name="my_groups"),
    path("leave-group/", views.leave_group, name="leave_group"),
    path("edit_password/", views.edit_password, name="edit_password"),
    path("support", views.support, name="support"),
    path("about", views.about, name="about"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
