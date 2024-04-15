from django.dispatch import receiver
from django.contrib.auth import get_user_model
from Api.models import UserProfile
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create a UserProfile instance when a new User is created.
    """
    if created and not hasattr(instance, 'userprofile'):
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal handler to save the UserProfile instance whenever the associated User is saved.
    """
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, **kwargs):
    """
    Signal handler to update the UserProfile whenever the associated User is updated.
    """
    profile, _ = UserProfile.objects.get_or_create(user=instance)
    profile.full_name = instance.full_name
    profile.username = instance.username
    profile.save()
