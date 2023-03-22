# from django.contrib import admin
from django.urls import path
from . import views
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
    # path("dog_profile_delete", views.dog_profile_delete, name="dog_profile_delete"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
