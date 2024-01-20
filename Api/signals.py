from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CoinToss, UserProfile

@receiver(post_save, sender=CoinToss)
def update_balance(sender, instance, **kwargs):
    user_profile = UserProfile.objects.get(user=instance.user)

    if instance.win:
        user_profile.balance += instance.stake_amount * 2
    else:
        user_profile.balance -= instance.stake_amount

    user_profile.save()