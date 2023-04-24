from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, UserProfile, DogProfile, EventPost, Groups
from django.forms import DateTimeInput


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    password = None

    class Meta:
        model = CustomUser
        fields = ("email",)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("fname", "lname", "bio", "dob")


# , "first_name", "last_name", "bio", "dob"


class DogProfileForm(forms.ModelForm):
    class Meta:
        model = DogProfile
        fields = ("name", "bio", "dob")
        widgets = {
            "dob": forms.DateInput(attrs={"type": "date"}),
        }


class EventPostForm(forms.ModelForm):
    event_time = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
        ),
    )

    class Meta:
        model = EventPost
        fields = ("event_title", "event_description", "event_time")
        widgets = {
            "event_time": DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            )
        }


class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = Groups
        fields = ["group_title", "group_description"]

        widgets = {"group_description": forms.Textarea()}
