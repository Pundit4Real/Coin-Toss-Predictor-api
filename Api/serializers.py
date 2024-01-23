from rest_framework import serializers
from .models import UserProfile, Prediction, CustomUser

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'full_name', 'email', 'profile']

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = CustomUser.objects.create(**validated_data)
        UserProfile.objects.create(user=user, **profile_data)
        return user

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ('id','predicted_at', 'side_predicted', 'stake_amount', 'result')

class BalanceUpdateSerializer(serializers.Serializer):
    balance = serializers.DecimalField(max_digits=10, decimal_places=2)
