import random
import numpy as np
from decimal import Decimal
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import  status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import (UserProfile, Prediction,PasswordResetCode,User)
from .serializers import (UserRegistrationSerializer,MyTokenObtainPairSerializer,
                          UserProfileSerializer,UserProfileUpdateSerializer, 
                          ChangePasswordSerializer, BalanceUpdateSerializer,
                          PredictionSerializer,ForgotPasswordEmailSerializer,PasswordResetSerializer
                          )

User = get_user_model()

class UserRegistrationView(APIView):
    @swagger_auto_schema(
        operation_description="Register your account now !",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='Enter your full name here'),
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Enter your username here'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Enter your email here'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Enter your password here'),
                'password_confirm': openapi.Schema(type=openapi.TYPE_STRING, description='Enter your password_confirm here'),
            },
            required=['username','email','password','password_confirm']
        )
    )
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

    @swagger_auto_schema(
        operation_description="Verify your email now.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Enter your registered email here.'),
                'verification_code': openapi.Schema(type=openapi.TYPE_STRING, description='Enter the verification code here.'),
            },
            required=['email','verification_code']
        )
    )
    
    def post(self, request):
        verification_code = request.data.get('verification_code')
        email = request.data.get('email')

        try:
            user = User.objects.get(email_verification_code=verification_code, email=email, is_active=False)
        except User.DoesNotExist:
            return Response({'message': 'Invalid verification code or email'}, status=status.HTTP_400_BAD_REQUEST)
        
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
                'full_name': user.full_name,
                'username': user.username,
                'email': user.email,
                'balance': user.balance
            }
        }, status=status.HTTP_200_OK)
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Change your password.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'old_password': openapi.Schema(type=openapi.TYPE_STRING, description='Enter your old password.'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='Enter your new password.'),
            },
            required=['old_password','new_password']
        )
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            old_password = serializer.data.get('old_password')
            new_password = serializer.data.get('new_password')

            # Check if the new password is the same as the old one
            if user.check_password(new_password):
                return Response({'error': 'New password cannot be the same as the old one.'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the old password is correct
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class ForgotPasswordView(APIView):
    def generate_numeric_code(self):
        # Generate a 6-digit numeric code
        return ''.join(random.choices('0123456789', k=6))
    @swagger_auto_schema(
        operation_description="Enter your email to reset your password.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Enter your email to reset your password.'),
            },
            required=['email']
        )
    )
    def post(self, request):
        serializer = ForgotPasswordEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'detail': 'No user with that email address.'}, status=status.HTTP_404_NOT_FOUND)

            # Generate and store a unique 6-digit numeric code
            code = self.generate_numeric_code()
            print("Generated code:", code)  # Print the generated code for debugging purposes
            PasswordResetCode.objects.create(user=user, code=code)

            # Send the code to the user's email
            subject = 'Password Reset Code'
            message = f'Your password reset code is: {code}'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]

            try:
                send_mail(subject, message, from_email, recipient_list, auth_user=settings.EMAIL_HOST_USER, auth_password=settings.EMAIL_HOST_PASSWORD)
                return Response({'detail': 'An email with a reset code has been sent to your email address.'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'detail': 'Failed to send the reset code. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Reset your password now!",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'reset_code': openapi.Schema(type=openapi.TYPE_STRING, description='Enter the reset code sent to your email here!.'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='Enter your new password here'),
            },
            required=['reset_code','new_password']
        )
    )
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            reset_code = serializer.validated_data['reset_code']
            new_password = serializer.validated_data['new_password']

            try:
                password_reset_code = PasswordResetCode.objects.get(code=reset_code)

                # Check if the reset code is expired
                if password_reset_code.is_expired:
                    return Response({'detail': 'The reset code has expired.'}, status=status.HTTP_400_BAD_REQUEST)

                    # Proceed with password reset
                user = password_reset_code.user
                
                # Check if the reset code is associated with a user
                user = password_reset_code.user
                if user:
                    # Check if the user's email matches the requester's email
                    if user.email != request.data.get('email'):
                        return Response({'detail': 'Invalid email for this reset code.'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'detail': 'Invalid reset code.'}, status=status.HTTP_400_BAD_REQUEST)


                # Check if the new password is different from the old one
                if user.check_password(new_password):
                    return Response({'detail': 'New password cannot be the same as the old one.'}, status=status.HTTP_400_BAD_REQUEST)

                # Set and save the new password
                user.set_password(new_password)
                user.save()


                # Delete the reset code after successful password reset
                password_reset_code.delete()

                return Response({'detail': 'Password reset successfully.'}, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response({'detail': 'Invalid reset code.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
           
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
    @swagger_auto_schema(
        operation_description="Update the user profile now!",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='Enter your full name'),
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Enter your username'),
                'avatar': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_BINARY, description='choose your profile avatar')
            },
            required=['username']
        )
    )
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
    @swagger_auto_schema(
        operation_description="Deposit to your balance now!",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'deposit': openapi.Schema(type=openapi.TYPE_STRING, description='Enter the amount to be doposited.'),
            },
            required=['deposit']
        )
    )
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