from django.contrib import admin
from .models import UserProfile, Prediction,User

class UserAdmin(admin.ModelAdmin):
    list_display = ['username','email','first_name']

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Prediction)
admin.site.register(User, UserAdmin)


