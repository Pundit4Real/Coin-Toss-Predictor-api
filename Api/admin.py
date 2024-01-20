from django.contrib import admin
from .models import CoinToss,UserProfile

# Register your models here.
admin.site.register(CoinToss)
admin.site.register(UserProfile)