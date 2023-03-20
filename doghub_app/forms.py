from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, UserProfile, DogProfile


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("username",
                  "first_name",
                  "last_name",
                  "email",
                  "password1",
                  "password2",)

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
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
