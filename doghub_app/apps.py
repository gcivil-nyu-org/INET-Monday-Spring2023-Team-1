from django.apps import AppConfig
from django.db.models.signals import post_save


class DoghubAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "doghub_app"

    def ready(self):
        from .models import DogProfile
        from .signals import dog_profile_create_triggers

        post_save.connect(dog_profile_create_triggers, sender=DogProfile)
