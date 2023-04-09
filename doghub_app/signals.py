from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DogProfile, UserTag, Tag
import logging


@receiver(post_save, sender=DogProfile)
def create_user_tag(sender, instance, created, **kwargs):
    if created:
        logging.debug("new dogprofile created")
        logging.debug("fetching user id")
        user_id = instance.user_id
        logging.debug("fetching Dog Ownder tag")
        dog_owner_tag = Tag.objects.get(tag_name="Dog Owner")

        logging.debug("checking if tag exists")
        tag_exists = UserTag.objects.filter(
            user_id=user_id, tag_id=dog_owner_tag
        ).exists()
        logging.debug(f"tag_exists: {tag_exists}")
        if not tag_exists:
            logging.debug("Creating UserTag now.")
            UserTag.objects.create(user_id=user_id, tag_id=dog_owner_tag)
    logging.debug("tag created successfully")
    return None
