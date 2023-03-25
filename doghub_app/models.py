from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

CHAR_MAX_LENGTH = 30
BIO_MAX_LENGTH = 500
EVENT_TITLE_MAX_LENGTH = 50


class CustomUser(AbstractUser):
    email = models.EmailField(_("email"), unique=True)
    id = models.AutoField(primary_key=True, editable=False)
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    ID_FIELD = "id"
    REQUIRED_FIELDS = ["password", "username"]

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user_id = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        db_column="user_id",
        on_delete=models.CASCADE,
        primary_key=True,
    )
    pic = models.ImageField(upload_to="user/")
    fname = models.CharField(max_length=CHAR_MAX_LENGTH)
    lname = models.CharField(max_length=CHAR_MAX_LENGTH)
    dob = models.DateField(null=True)
    bio = models.CharField(max_length=BIO_MAX_LENGTH, null=True)

    def get_first_name(self):
        return self.user_id.fname


class DogProfile(models.Model):
    dog_id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column="user_id"
    )

    pic = models.ImageField(upload_to="dog/", null=True)
    name = models.CharField(max_length=CHAR_MAX_LENGTH)
    dob = models.DateField()
    bio = models.CharField(max_length=BIO_MAX_LENGTH)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="dog_profile_composite_pk", fields=["dog_id", "user_id"]
            )
        ]

    def __str__(self):
        return self.name


class EventPost(models.Model):
    event_id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=CHAR_MAX_LENGTH, default='Name of User')
    user_id = models.ForeignKey(
    settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column="user_id"
    )
    event_title = models.CharField(max_length=EVENT_TITLE_MAX_LENGTH)
    event_description=models.CharField(max_length=BIO_MAX_LENGTH)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="event_post_composite_pk", fields=["event_id", "user_id"]
            )
        ]

    def get_first_name(self):
        return self.user_id.fname


    def __str__(self):
        return self.event_title + ' | ' + self.name
