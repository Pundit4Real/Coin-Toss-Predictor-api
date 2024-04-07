from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User, AbstractBaseUser, PermissionsMixin
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from coinTossPredictor.basemodel import TimeStampedModel
from .managers import UserManager


class User(AbstractBaseUser,PermissionsMixin):
    username = models.CharField(max_length=50, null=True, blank=True)
    email= models.EmailField(max_length=254, unique=True)
    full_name = models.CharField(max_length=150,null=True, blank=True)
    password = models.CharField(max_length=200)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    email_verification_code = models.CharField(max_length=50,null=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(True)
    last_login = models.DateTimeField(null=True,blank=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD="email"
    REQUIRED_FIELDS=[]

    objects = UserManager()

    def get_absolute_url(self):
        return "/users/%i/" % (self.pk)
    
    def save(self, *args, **kwargs):
        # Hash the password if it's set and not hashed already
        if self.password and not self.password.startswith("pbkdf2_sha256$"):
            self.password = make_password(self.password)
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        if self.username:
         return self.username
        else:
            return self.email  # or any other field that uniquely identifies the user


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

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