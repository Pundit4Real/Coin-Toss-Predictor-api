from django.contrib import admin
from .models import UserProfile, Prediction,User

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Prediction)
admin.site.register(User)