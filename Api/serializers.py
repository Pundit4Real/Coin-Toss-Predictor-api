from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Prediction

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = UserProfile
        fields = ['id','username', 'balance']

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ['id', 'predicted_at', 'side_predicted', 'stake_amount', 'result']
        read_only_fields = ['id', 'predicted_at', 'side_predicted', 'stake_amount', 'result']

class BalanceUpdateSerializer(serializers.Serializer):
    balance = serializers.DecimalField(max_digits=10, decimal_places=2)
