import random
from django.http import Http404
from decimal import Decimal
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
        return self.request.user

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            # Create UserProfile instance if it doesn't exist
            profile = UserProfile.objects.create(user=user)

        serializer = self.serializer_class(profile, data=request.data)
        if serializer.is_valid():
            # Update the balance by adding the new deposit to the old balance
            new_balance = profile.balance + Decimal(request.data.get('deposit', 0))
            profile.balance = new_balance
            profile.save()
            return Response({'username': user.username, 'balance': new_balance})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class CoinTossView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def cointoss(self):
        """
        Simulate a coin toss game.
        """
        return random.choice(['TAIL', 'HEAD'])

    def user_prediction(self, user_choice):
        """
        Simulate user's prediction.
        """
        result = random.random()
        if user_choice == 'TAIL' and result <= 0.45:
            return 'WIN'
        elif user_choice == 'HEAD' and result > 0.45:
            return 'WIN'
        else:
            return 'LOSS'

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
        Make a prediction using the provided coin toss simulation.
        """
        user_choice = request.data.get('side', '').upper()
        stake_amount = Decimal(request.data.get('stake_amount', 0.0))

        if user_choice not in ['HEAD', 'TAIL']:
            return Response({'error': 'Invalid side. Please choose from the options: HEAD or TAIL'}, status=status.HTTP_400_BAD_REQUEST)

        if stake_amount <= 0:
            return Response({'error': 'Invalid stake amount. It must be greater than zero'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

        if stake_amount > user_profile.balance:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
        
# Save the UserProfile associated with the User object
        try:
             user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
    # Handle the case where UserProfile doesn't exist
         return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)


        # Simulate the coin toss and user prediction
        coin_result = self.cointoss()
        user_result = self.user_prediction(user_choice)

        # Create a new prediction record in the database
        prediction = Prediction.objects.create(
            user=request.user,
            side_predicted=user_choice,
            stake_amount=stake_amount,
            result=coin_result,
        )
        # request.user.save()

        if user_result == 'WIN':
            amount_won = 2 * stake_amount
            user_profile.balance += amount_won
            user_profile.save()
            message = f'Congratulations! You won Ghs {amount_won}. New balance: Ghs {user_profile.balance}'
        else:
            user_profile.balance -= stake_amount
            user_profile.save()
            message = f'Oops! You lost Ghs {stake_amount}. New balance: Ghs {user_profile.balance}'

        return Response({'message': message, 'coin_result': coin_result, 'user_result': user_result}, status=status.HTTP_200_OK)