# signals.py

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from .models import UserProfile

@receiver(post_save, sender=get_user_model())
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if isinstance(instance, get_user_model()):
        full_name = instance.get_full_name() or instance.username
        email = instance.email

        if created:
            UserProfile.objects.create(user=instance, full_name=full_name, email=email)
        else:
            try:
                user_profile = instance.UserProfile()
                user_profile.full_name = full_name
                user_profile.email = email
                user_profile.save()
            except UserProfile.DoesNotExist:
                UserProfile.objects.create(user=instance, full_name=full_name, email=email)
