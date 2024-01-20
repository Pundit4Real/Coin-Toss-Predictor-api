from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)

class CoinToss(models.Model):
    HEAD = 'HEAD'
    TAIL = 'TAIL'
    SIDE_CHOICES = [
        (HEAD, 'Head'),
        (TAIL, 'Tail'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stake_amount = models.DecimalField(max_digits=10, decimal_places=2)
    chosen_side = models.CharField(max_length=4, choices=SIDE_CHOICES)
    result = models.CharField(max_length=4, choices=SIDE_CHOICES, null=True, blank=True)
    win = models.BooleanField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)