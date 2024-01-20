from rest_framework import serializers
from .models import UserProfile, CoinToss

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('user', 'balance')

class CoinTossSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinToss
        fields = ('id', 'user', 'stake_amount', 'chosen_side', 'result', 'win', 'timestamp')