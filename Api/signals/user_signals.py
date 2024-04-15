from django.dispatch import receiver
from django.db.models.signals import post_save
from Api.models import UserProfile

@receiver(post_save, sender=UserProfile)
def update_user_balance(sender, instance, **kwargs):
    if kwargs.get('created', False) or instance.balance != instance.user.balance:
        instance.user.balance = instance.balance
        instance.user.save()