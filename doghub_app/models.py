from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
class CustomUser(AbstractUser):
    # don't have additional fields for now
    # happy with email, password1, password2
    email = models.EmailField(_('email'), unique=True)
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['password', 'username']
    def __str__(self):
        return self.email
    # pass



