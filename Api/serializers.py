from rest_framework import serializers
from .models import UserProfile, Prediction

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ('timestamp', 'side_predicted', 'stake_amount', 'result')
class BalanceUpdateSerializer(serializers.Serializer):
    balance = serializers.DecimalField(max_digits=10, decimal_places=2)