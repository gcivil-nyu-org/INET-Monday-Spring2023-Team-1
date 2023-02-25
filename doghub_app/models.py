from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # don't have additional fields for now
    # happy with email, password1, password2
    pass

