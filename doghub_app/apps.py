from django.apps import AppConfig
""" from django.db.models.signals import post_save
from .models import DogProfile
from .signals import create_user_tag """



class DoghubAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "doghub_app"

    def ready(self):
        from . import signals
        #post_save.connect(create_user_tag, sender=DogProfile)
