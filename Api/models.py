from django.db import models
from django.contrib.auth.models import User


# user models.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delte=models.CASCADE)
    balance = models.DecimalField(max_digits=0, decimal_places=2, default=0)