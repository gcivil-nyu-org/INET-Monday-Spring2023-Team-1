# print("Loading Signals File...")
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DogProfile, UserTag, Tag

# f = open('output.txt', 'a')
# f.write("We have reached the signals file.")


@receiver(post_save, sender=DogProfile)
def create_user_tag(sender, instance, created, **kwargs):
    # f.write('Entered function')
    if created:
        # f.write('Entered If')
        user_id = instance.user_id
        dog_owner_tag = Tag.objects.get(tag_name="Dog Owner")
        # f.write('Reached till here. Now performing checks\n')

        tag_exists = UserTag.objects.filter(
            user_id=user_id, tag_id=dog_owner_tag
        ).exists()
        # f.write("\n")
        # f.write(str(tag_exists))
        # f.write("\n")
        if not tag_exists:
            # f.write('Creating UserTag now.')
            UserTag.objects.create(user_id=user_id, tag_id=dog_owner_tag)
