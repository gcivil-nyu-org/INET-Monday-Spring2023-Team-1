from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserTag, DogTag, DogProfile
from dateutil.relativedelta import relativedelta
import datetime as dt
import logging


def give_tag(model, model_id: dict[str, int], tag_id: int):
    """
    adds tag_id to model if model doesn't have it
    not that model is the intersect table, examples below

    model: tag model from doghub_app.models.py
        ex: UserTag, DogTag, ParkTag, ServiceTag
    model_id: dic[str, int]:
    one record dictionary in the form of id_name: id
    ex: {'user_id': 1} or {'dog_id': 2}
        or {'park_id': 1}, {'ser_id': 3}, etc.
    Note that the key is used to query the table so
    it must match the model table id name

    tag_id: int: the tag id to give to model
    """
    obj = model.objects.filter(**model_id, tag_id=tag_id)
    if not obj:
        "has to append _id at the end to insert by id"
        rec = dict()
        rec[list(model_id.keys())[0] + "_id"] = list(model_id.values())[0]
        rec["tag_id_id"] = tag_id
        obj = model(**rec)
        obj.save()
    return None


@receiver(post_save, sender=DogProfile)
def dog_profile_create_triggers(sender, instance, created, **kwargs):
    "runs when a dog profile is created"
    if created:
        logging.debug("new dogprofile created")

        # give dog owner tag
        logging.debug("giving dog owner tag")
        give_tag(UserTag, {"user_id": instance.user_id.id}, 1)

        # give puppy tag
        logging.debug("checking if dog qualifies for puppy tag")
        dob = instance.dob
        if not isinstance(dob, dt.datetime):
            dob = dt.datetime.strptime(instance.dob, "%Y-%m-%d")

        age = relativedelta(dt.datetime.now(), dob).years
        logging.debug(f"dog is {age} years old")
        if age <= 1:
            logging.debug("dog is a puppy, giving tag")
            give_tag(DogTag, {"dog_id": instance.dog_id}, 3)
