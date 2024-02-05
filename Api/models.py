from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils import timezone


class User(AbstractUser):
    email= models.EmailField(unique=True)
    username = models.CharField(max_length=100)

    USERNAME_FIELD="email"
    REQUIRED_FIELDS=['username']

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    side_predicted = models.CharField(max_length=4, choices=[('HEAD', 'HEAD'), ('TAIL', 'TAIL')])
    stake_amount = models.DecimalField(max_digits=10, decimal_places=2)
    result = models.CharField(max_length=4, choices=[('HEAD', 'HEAD'), ('TAIL', 'TAIL')])
    win = models.BooleanField(default=False)
    predicted_at = models.DateTimeField(default=timezone.now)

    @property
    def username(self):
        return self.user.username