from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from datetime import datetime

AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "doghub_app.CustomUser")

MID_CHAR_SIZE = 50
LARGE_CHAR_SIZE = 500


class CustomUser(AbstractUser):
    email = models.EmailField(_("email"), unique=True)
    email_verified = models.BooleanField(default=False)
    id = models.AutoField(primary_key=True, editable=False)
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    ID_FIELD = "id"
    REQUIRED_FIELDS = ["password", "username"]

    class Meta:
        db_table = "custom_user"

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user_id = models.OneToOneField(
        AUTH_USER_MODEL,
        db_column="user_id",
        on_delete=models.DO_NOTHING,
        primary_key=True,
    )
    pic = models.ImageField(
        upload_to="user/", default="../static/images/profile1.jpg", null=True
    )
    fname = models.CharField(max_length=MID_CHAR_SIZE)
    lname = models.CharField(max_length=MID_CHAR_SIZE)
    dob = models.DateField()
    bio = models.CharField(max_length=LARGE_CHAR_SIZE, null=True, blank=True)

    class Meta:
        db_table = "user_profile"

    def get_first_name(self):
        return self.user_id.fname


class DogBreed(models.Model):
    bre_id = models.AutoField(primary_key=True)
    bre_name = models.CharField(max_length=MID_CHAR_SIZE)
    bre_size_lbs = models.SmallIntegerField()

    class Meta:
        db_table = "dog_breed"


class DogProfile(models.Model):
    dog_id = models.AutoField(primary_key=True, editable=False)
    pic = models.ImageField(
        upload_to="dog/", default="../static/images/dog_profile.jpeg", null=True
    )
    name = models.CharField(max_length=MID_CHAR_SIZE)
    dob = models.DateField()
    bio = models.CharField(max_length=LARGE_CHAR_SIZE)
    user_id = models.ForeignKey(AUTH_USER_MODEL, models.CASCADE, db_column="user_id")
    bre_id = models.ForeignKey(
        DogBreed, models.DO_NOTHING, db_column="bre_id", null=True, blank=True
    )

    class Meta:
        db_table = "dog_profile"

    def __str__(self):
        return self.name


class Park(models.Model):
    park_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=MID_CHAR_SIZE)
    street = models.CharField(max_length=MID_CHAR_SIZE, blank=True, null=True)
    city = models.CharField(max_length=MID_CHAR_SIZE, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    zipcode = models.CharField(max_length=5, blank=True, null=True)
    latitude = models.CharField(max_length=MID_CHAR_SIZE, blank=True, null=True)
    longitude = models.CharField(max_length=MID_CHAR_SIZE, blank=True, null=True)
    use_coordinates = models.BooleanField(default=0)

    class Meta:
        db_table = "park"


class EventPost(models.Model):
    event_id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.DO_NOTHING, db_column="user_id"
    )
    event_title = models.CharField(max_length=MID_CHAR_SIZE)
    event_description = models.CharField(max_length=LARGE_CHAR_SIZE)
    event_time = models.DateTimeField(default=datetime.now)
    park_id = models.ForeignKey(
        "Park", models.DO_NOTHING, blank=True, null=True, db_column="park_id"
    )

    class Meta:
        db_table = "event_post"

    def get_first_name(self):
        return self.user_id.fname

    def __str__(self):
        return self.event_title
        # return self.event_title + ' | ' + self.name


class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    tag_name = models.CharField(max_length=MID_CHAR_SIZE)
    tag_type = models.CharField(max_length=1)
    sys_tag = models.BooleanField(default=0)

    def __str__(self):
        return f"{self.tag_name} , type:{self.tag_type}"

    class Meta:
        db_table = "tag"


class DogTag(models.Model):
    dtag_id = models.AutoField(primary_key=True)
    dog_id = models.ForeignKey(DogProfile, models.CASCADE, db_column="dog_id")
    tag_id = models.ForeignKey("Tag", models.DO_NOTHING, db_column="tag_id")

    class Meta:
        db_table = "dog_tag"
        unique_together = (("dog_id", "tag_id"),)


class EventTag(models.Model):
    etag_id = models.AutoField(primary_key=True)
    event_id = models.ForeignKey(EventPost, models.CASCADE, db_column="event_id")
    tag_id = models.ForeignKey(Tag, models.DO_NOTHING, db_column="tag_id")

    class Meta:
        db_table = "event_tag"
        unique_together = (("event_id", "tag_id"),)


class Attendee(models.Model):
    attendee_id = models.AutoField(primary_key=True)
    event_id = models.ForeignKey(EventPost, models.CASCADE, db_column="event_id")
    user_id = models.ForeignKey(AUTH_USER_MODEL, models.DO_NOTHING, db_column="user_id")

    class Meta:
        db_table = "attendee"
        unique_together = (("event_id", "user_id"),)


class ParkTag(models.Model):
    ptag_id = models.AutoField(primary_key=True)
    park_id = models.ForeignKey(Park, models.CASCADE, db_column="park_id")
    tag_id = models.ForeignKey(Tag, models.DO_NOTHING, db_column="tag_id")

    class Meta:
        db_table = "park_tag"
        unique_together = (("park_id", "tag_id"),)


class Service(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=MID_CHAR_SIZE)
    description = models.CharField(max_length=LARGE_CHAR_SIZE, default="")
    rate = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    contact_details = models.CharField(max_length=255, default="")
    address = models.CharField(max_length=255, blank=True, null=True)
    tag_id = models.ForeignKey("Tag", models.DO_NOTHING, db_column="tag_id")

    class Meta:
        db_table = "service"

    def __str__(self):
        return self.service_title


class UserTag(models.Model):
    utag_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(AUTH_USER_MODEL, models.CASCADE, db_column="user_id")
    tag_id = models.ForeignKey(Tag, models.DO_NOTHING, db_column="tag_id")

    def __str__(self):
        return f"{self.user_id}, {self.tag_id.tag_name}"

    class Meta:
        db_table = "user_tag"
        unique_together = (("user_id", "tag_id"),)


class Chat(models.Model):
    receiver = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chats_as_user2"
    )
    sender = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages"
    )
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.id} ({self.sender.username} and {self.receiver.username})"

    class Meta:
        db_table = "chat"


class Friends(models.Model):
    fid = models.AutoField(primary_key=True)
    sender = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column="sender_id",
        related_name="user1",
    )
    receiver = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column="receiver_id",
        related_name="user2",
    )
    pending = models.BooleanField(default=True)

    class Meta:
        db_table = "friends"
        unique_together = (("sender", "receiver"),)

    def __str__(self):
        return f"Friends: {self.fid}: ({self.sender}, {self.receiver})"


class Groups(models.Model):
    group_id = models.AutoField(primary_key=True, editable=False)
    group_title = models.CharField(max_length=MID_CHAR_SIZE, unique=True)
    group_description = models.CharField(max_length=LARGE_CHAR_SIZE)
    group_owner = models.ForeignKey(
        AUTH_USER_MODEL, models.CASCADE, db_column="user_id", related_name="group_owner"
    )

    class Meta:
        db_table = "groups"

    def __str__(self):
        return self.group_title


class GroupMember(models.Model):
    gm_id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Groups, models.CASCADE, db_column="group_id")
    member = models.ForeignKey(AUTH_USER_MODEL, models.DO_NOTHING, db_column="user_id")
    pending = models.BooleanField(default=True)

    class Meta:
        db_table = "group_member"
        unique_together = (("group", "member"),)



