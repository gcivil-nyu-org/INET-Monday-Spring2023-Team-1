import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "doghub.settings")

django.setup()
from doghub_app.models import Tag  # noqa: E402

res = Tag.objects.filter(tag_name="Dog Owner").exists()
if not res:
    Tag.objects.create(tag_name="Dog Owner", tag_type="U")
    print("Tag Dog Owner created.")
else:
    print("Tag Dog Owner already exists.")
