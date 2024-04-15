from django.contrib import admin
from .models import UserProfile, Prediction, User, PasswordResetCode


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id','full_name' ,'email','is_active']
    search_fields = ['email']


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name','username','balance']
class PasswordResetCodeAdmin(admin.ModelAdmin):
    list_display = ['user','code','created_at']
    
class PredictionAdmin(admin.ModelAdmin):
    # Customizations for Prediction admin interface can be added here
    pass


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Prediction, PredictionAdmin)
admin.site.register(PasswordResetCode,  PasswordResetCodeAdmin)
