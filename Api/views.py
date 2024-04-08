import random
from django.http import Http404
from decimal import Decimal
import numpy as np
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, Token
from django.contrib.auth import get_user_model

from .models import UserProfile, Prediction
from .serializers import (UserRegistrationSerializer,MyTokenObtainPairSerializer,
                          UserProfileSerializer,UserProfileUpdateSerializer, 
                          ChangePasswordSerializer, BalanceUpdateSerializer,
                          PredictionSerializer)
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()

class UserRegistrationView(APIView):
    def post(self, request):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            response_data = {
                'full_name': user.full_name,
                'username': user.username,
                'email': user.email,
                'email_verification_code': user.email_verification_code
            }
            return Response({'message': 'User registered successfully', 'response_data': response_data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class EmailVerificationView(APIView):
    def get(self, request, verification_code):
        try:
            user = User.objects.get(email_verification_code=verification_code, is_active=False)
        except User.DoesNotExist:
            return Response({'message': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_active = True
        user.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # Return response with tokens and user data
        return Response({
            'message': 'Email verified successfully',
            'access_token': access_token,
            'refresh_token': str(refresh),
            'user_data': {
                'full_name':user.full_name,
                'username': user.username,
                'email': user.email
            }
        }, status=status.HTTP_200_OK)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get('old_password')):
                user.set_password(serializer.data.get('new_password'))
                user.save()
                update_session_auth_hash(request, user) 
                return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
            return Response({'error': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer 

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.filter(email=user.email)
        return queryset


class UserProfileUpdateView(APIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class BalanceUpdateView(APIView):
    serializer_class = BalanceUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.userprofile

    def post(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.serializer_class(profile, data=request.data)
        if serializer.is_valid():
            profile.balance += Decimal(request.data.get('deposit', 0))
            profile.save()
            return Response({'username': profile.user.username, 'balance': profile.balance})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CoinTossView(APIView):
    WIN_PROBABILITY = 0.2  # Initial win probability
    MAX_WIN_PROBABILITY = 0.5  # Maximum win probability
    WIN_INCREMENT = 0.05  # Increment for win probability
    WIN_LIMIT = 0.6  # Limit after which win probability won't increase further

    def get_user_win_rate(self, user):
        """
        Calculate the win rate of the user based on past predictions.
        """
        total_predictions = Prediction.objects.filter(user=user).count()
        if total_predictions == 0:
            return 0
        win_predictions = Prediction.objects.filter(user=user, win=True).count()
        return win_predictions / total_predictions

    def get_win_probability(self, user):
        """
        Calculate the dynamic win probability based on the user's win rate.
        """
        user_win_rate = self.get_user_win_rate(user)
        dynamic_win_probability = min(self.WIN_PROBABILITY + user_win_rate * self.WIN_INCREMENT, self.MAX_WIN_PROBABILITY)
        return min(dynamic_win_probability, self.WIN_LIMIT)

    def user_prediction(self, user_choice, win_probability):
        """
        Simulate user's prediction with dynamic win probability.
        """
        result = random.random()
        if user_choice == 'TAIL' and result <= win_probability:
            return True
        elif user_choice == 'HEAD' and result > (1 - win_probability):
            return True
        else:
            return False  

    def cointoss(self):
        """
        Simulate a coin toss game with random events.
        """
        # Introduce random events during the coin toss simulation
        if np.random.random() < 0.2:  # 20% chance of a random event
           
            return random.choice(['TAIL', 'HEAD'])
        else:
            # Regular coin toss without any random events
            return random.choice(['TAIL', 'HEAD'])

    def post(self, request):
        user_choice = request.data.get('side', '').upper()
        stake_amount = Decimal(request.data.get('stake_amount', 0.0))

        if user_choice not in ['HEAD', 'TAIL']:
            return Response({'error': 'Invalid side. Please choose from the options: HEAD or TAIL'}, status=status.HTTP_400_BAD_REQUEST)

        if stake_amount <= 0:
            return Response({'error': 'Invalid stake amount. Deposit to continue!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

        if stake_amount > user_profile.balance:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate dynamic win probability
        win_probability = self.get_win_probability(request.user)

        # Simulate the coin toss and user prediction
        coin_result = self.cointoss()
        user_result = self.user_prediction(user_choice, win_probability)

        # Create a new prediction record in the database
        prediction = Prediction.objects.create(
            user=request.user,
            side_predicted=user_choice,
            stake_amount=stake_amount,
            result=coin_result,
            win=user_result
        )

        # Update user's balance based on prediction result
        if user_result:
            amount_won = 2 * stake_amount
            user_profile.balance += amount_won
            user_profile.save()
            message = f'Congratulations! You won Ghs {amount_won}. New balance: Ghs {user_profile.balance}'
            win_status = True

        else:
            user_profile.balance -= stake_amount
            user_profile.save()
            message = f'Oops! You lost Ghs {stake_amount}. New balance: Ghs {user_profile.balance}'
            win_status = False

        response_data = {
            'message': message,
            'coin_result': coin_result,
            'user_result': user_result,
            'side_predicted': user_choice,
            'win':win_status,
            # 'win_probability': win_probability,
            'balance': user_profile.balance
        }

        return Response(response_data, status=status.HTTP_200_OK)
    

    def get_user_predictions(self, user):
        """
        Retrieve prediction history for the user.
        """
        predictions = Prediction.objects.filter(user=user)
        serializer = PredictionSerializer(predictions, many=True)
        return serializer.data

    def get(self, request):
        """
        Get user prediction history.
        """
        user = request.user
        predictions = self.get_user_predictions(user)
        return Response(predictions, status=status.HTTP_200_OK)