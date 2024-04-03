from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import Http404
from decimal import Decimal
import random
from .models import UserProfile, Prediction
from .serializers import UserProfileSerializer, PredictionSerializer, BalanceUpdateSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg import openapi

User = get_user_model()

class RegisterAPIView(APIView):
    def post(self, request):
        """
        Register a new user.
        """
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(**serializer.validated_data)
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Login a user.
        """
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({'message': 'Login successful', 'tokens': {'refresh_token': str(refresh), 'access_token': str(refresh.access_token)}}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        """
        Logout a user.
        """
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)

class UserProfileAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        """
        Get user profile.
        """
        user_profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)

    swagger_schema_post = {
        'operation_id': 'update_user_balance',
        'request_body': BalanceUpdateSerializer,
        'responses': {
            200: 'Balance updated successfully',
            400: 'Bad Request'
        }
    }

    def post(self, request):
        """
        Update user balance.
        """
        serializer = BalanceUpdateSerializer(data=request.data)
        if serializer.is_valid():
            added_amount = serializer.validated_data['balance']
            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.balance += added_amount
            user_profile.save()
            return Response({'message': 'Balance updated successfully', 'New balance': f'Ghs {user_profile.balance}'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CoinTossAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        """
        Get user prediction history.
        """
        user = request.user
        predictions = Prediction.objects.filter(user=user)
        serializer = PredictionSerializer(predictions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request):
        """
        Make a prediction.
        """
        result_options = ['HEAD', 'TAIL']
        result = random.choice(result_options)

        side = request.data.get('side', '').upper()
        stake_amount = Decimal(request.data.get('stake_amount', 0.0))

        if side not in result_options:
            return Response({'error': 'Invalid side. Please choose from the options: HEAD or TAIL'}, status=status.HTTP_400_BAD_REQUEST)

        if stake_amount <= 0:
            return Response({'error': 'Invalid stake amount. It must be greater than zero'}, status=status.HTTP_400_BAD_REQUEST)

        user_profile = UserProfile.objects.get(user=request.user)

        if stake_amount > user_profile.balance:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

        prediction = Prediction.objects.create(
            user=request.user,
            side_predicted=side,
            stake_amount=stake_amount,
            result=result,
        )

        if result == side:
            amount_won = 2 * stake_amount
            user_profile.balance += amount_won
            user_profile.save()
            message = f'Congratulations! You won Ghs {amount_won}. New balance: Ghs {user_profile.balance}'
        else:
            user_profile.balance -= stake_amount
            user_profile.save()
            message = f'Oops! You lost Ghs {stake_amount}. New balance: Ghs {user_profile.balance}'

        return Response({'message': message}, status=status.HTTP_200_OK)
