from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils import timezone
from django.db.models.signals import post_save

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    side_predicted = models.CharField(max_length=4, choices=[('HEAD', 'HEAD'), ('TAIL', 'TAIL')])
    stake_amount = models.DecimalField(max_digits=10, decimal_places=2)
    result = models.CharField(max_length=4, choices=[('HEAD', 'HEAD'), ('TAIL', 'TAIL')])
    timestamp = models.DateTimeField(default=timezone.now)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # full_name = models.CharField(max_length=80)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)


