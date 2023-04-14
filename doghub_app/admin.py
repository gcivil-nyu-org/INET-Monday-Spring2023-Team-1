from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, UserProfile, DogProfile, EventPost, Chat, Attendee

admin.site.register(CustomUser)
admin.site.register(UserProfile)
admin.site.register(DogProfile)
admin.site.register(EventPost)
admin.site.register(Chat)
admin.site.register(Attendee)


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["email", "username"]
