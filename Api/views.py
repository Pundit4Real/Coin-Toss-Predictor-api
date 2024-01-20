from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import  authenticate, login, logout
from django.contrib.auth.models import User
import random
from .models import UserProfile
from .serializers import UserProfileSerializer


# user registration class
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if username and password:
            user = User.objects.create_user(username=username, password=password)
            UserProfile.objects.create(user=user)
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

# user log in class view
        
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# the logout view
class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)

# view responsible for handling the prediction
class PredictView(APIView):
    def post(self, request):
        user = request.user
        if user.is_authenticated:
            # Simulate a coin toss - 0 for HEAD, 1 for TAIL
            toss_result = random.choice([0, 1])

            # Assuming the user provided 'side' in the request data (0 for HEAD, 1 for TAIL)
            user_prediction = int(request.data.get('side', 0))

            # Determine if the prediction is correct
            prediction_correct = toss_result == user_prediction

            # Update user balance based on the prediction result
            if prediction_correct:
                # User wins, double the stake
                user_balance = UserProfile.objects.get(user=user).balance
                user_balance *= 2
                UserProfile.objects.filter(user=user).update(balance=user_balance)

                return Response({'message': f'Prediction made successfully. You won! New balance: {user_balance}'}, status=status.HTTP_200_OK)
            else:
                # User loses, deduct the stake
                user_balance = UserProfile.objects.get(user=user).balance
                UserProfile.objects.filter(user=user).update(balance=user_balance)

                return Response({'message': f'Prediction made successfully. You lost! New balance: {user_balance}'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

# Balance updating view
class BalanceView(APIView):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            profile = UserProfile.objects.get(user=user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)       