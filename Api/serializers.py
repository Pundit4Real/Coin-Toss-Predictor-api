from rest_framework import serializers
from .models import UserProfile, Prediction

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'balance')
        read_only_fields = ('id', 'user')

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ('timestamp', 'side_predicted', 'stake_amount', 'result')
