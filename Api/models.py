from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.utils import timezone
from django.db.models.signals import post_save



class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    side_predicted = models.CharField(max_length=4, choices=[('HEAD', 'HEAD'), ('TAIL', 'TAIL')])
    stake_amount = models.DecimalField(max_digits=10, decimal_places=2)
    result = models.CharField(max_length=4, choices=[('HEAD', 'HEAD'), ('TAIL', 'TAIL')])
    predicted_at = models.DateTimeField(default=timezone.now)



