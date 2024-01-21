from rest_framework import viewsets, permissions,status
from django.contrib.auth import authenticate, login, logout
from .models import UserProfile, Prediction
from .serializers import UserProfileSerializer, PredictionSerializer,BalanceUpdateSerializer
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.http import Http404
import random
from decimal import Decimal

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def balance(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            serializer = self.get_serializer(user_profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            raise Http404("UserProfile matching query does not exist.")

    @action(detail=True, methods=['post'])
    def update_balance(self, request, pk=None):
        user_profile = self.get_object()
        serializer = BalanceUpdateSerializer(data=request.data)

        if serializer.is_valid():
            new_balance = serializer.validated_data['balance']
            user_profile.balance = new_balance
            user_profile.save()
            return Response({'message': 'Balance updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if username and password:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return Response({'message': 'User registered and logged in successfully'}, status=201)
        else:
            return Response({'error': 'Username and password are required'}, status=400)

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            # Issue a JWT token
            refresh = RefreshToken.for_user(user)
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            return Response({'message': 'Login successful', 'tokens': data}, status=200)
        else:
            return Response({'error': 'Invalid credentials'}, status=401)
    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'message': 'Logout successful'}, status=200)


class CoinTossViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def history(self, request):
        user = request.user
        predictions = Prediction.objects.filter(user=user)
        serializer = PredictionSerializer(predictions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def predict(self, request):
        user = request.user
        try:
            profile = user.userprofile  # Assuming a one-to-one relationship between User and UserProfile
        except UserProfile.DoesNotExist:
            raise Http404("UserProfile matching query does not exist.")

        # Implement coin toss logic
        result = random.choice(['HEAD', 'TAIL'])  # Simulating the coin toss

        # Update user balance accordingly
        try:
            stake_amount = Decimal(request.data.get('stake_amount', 0.0))
            if stake_amount <= 0:
                raise ValueError("Invalid stake amount")

            if stake_amount > profile.balance:
                raise ValueError("Insufficient balance")
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Save the prediction to the user's history
        prediction = Prediction.objects.create(
            user=user,
            side_predicted=request.data.get('side'),
            stake_amount=stake_amount,
            result=result
        )

        if result == 'HEAD':
            profile.balance += 2 * stake_amount
            profile.save()
            message = f'Congratulations! You won {2 * stake_amount} units. New balance: {profile.balance}'
        else:
            profile.balance -= stake_amount
            profile.save()
            message = f'Oops! You lost {stake_amount} units. New balance: {profile.balance}'

        return Response({'message': message, 'result': result, 'prediction': PredictionSerializer(prediction).data}, status=status.HTTP_200_OK)