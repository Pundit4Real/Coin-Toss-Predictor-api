import json
import string
import random
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from rest_framework.authtoken.models import Token
from .utils import send_email_verification_code
from .models import User, Prediction,UserProfile

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        refresh = RefreshToken.for_user(user)
        access = AccessToken.for_user(user)
        data['message'] = 'Login successful'
        data['tokens'] = {
            'refresh_token': str(refresh),
            'access_token': str(access),
        }
        data['user_data'] = {
            'id': user.id,
            'Full_name': user.full_name,
            'Username': user.username,
            'Email': user.email,
        }
        data.pop('refresh')
        data.pop('access')
        return data


User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'username', 'password', 'password_confirm']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': True},
            'email': {'required': True}
        }

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise ValidationError("Username is already taken")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError("Email is already taken")
        return value

    def validate(self, data):
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        email_verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        validated_data['email_verification_code'] = email_verification_code
        user = User.objects.create_user(**validated_data)
        # Send verification email
        
        send_email_verification_code(validated_data['email'],email_verification_code)  # Call the utility function

        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email','avatar', 'balance']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'username', 'avatar'] 

class BalanceUpdateSerializer(serializers.Serializer):
    deposit = serializers.DecimalField(max_digits=10, decimal_places=2)

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ['user', 'predicted_at', 'side_predicted', 'stake_amount', 'result', 'win']
        read_only_fields = ['predicted_at', 'result', 'win']



