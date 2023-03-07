from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register", views.register_request, name="register"),
    path("register_details", views.register_details_request, name="register_details"),
    path("login", views.login_request, name="login"),
    path("events", views.events, name="events"),
    path("logout", views.logout_request, name="logout"),
    path("dogProfilesCreate", views.dog_profile_create, name="dogProfileCreate"),
]
