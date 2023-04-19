from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import (
    CustomUser,
    UserProfile,
    DogProfile,
    EventPost,
    Chat,
    Attendee,
    Friends,
    Service,
)

admin.site.register(CustomUser)
admin.site.register(UserProfile)
admin.site.register(DogProfile)
admin.site.register(EventPost)
admin.site.register(Chat)
admin.site.register(Attendee)
admin.site.register(Friends)
admin.site.register(Service)


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["email", "username"]
