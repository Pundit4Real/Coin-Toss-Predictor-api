from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import  authenticate, login, logout
from django.contrib.auth.models import User
import random
from .models import UserProfile
from .serializers import UserProfileSerializer

# user registration class
@csrf_exempt
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
    
    @csrf_exempt
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            Token.objects.filter(user=user).delete()

            # Use Token's create method directly
            token = Token.objects.create(user=user)

            return Response({'token': token.key, 'message': 'Login successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)



# the logout view
@csrf_exempt
class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)

# view responsible for handling the prediction# Helper function for updating user balance
def update_user_balance(user, multiplier):
    user_balance = UserProfile.objects.get(user=user).balance
    new_balance = user_balance * multiplier
    UserProfile.objects.filter(user=user).update(balance=new_balance)
    return new_balance

class PredictView(APIView):
    authentication_classes = [TokenAuthentication]
    
    @csrf_exempt
    def post(self, request):
        user = request.user

        if not user.is_authenticated:
            return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        # Input validation for 'side' parameter
        user_prediction = request.data.get('side')
        if user_prediction is None or not user_prediction.isdigit():
            return Response({'error': 'Invalid input for side'}, status=status.HTTP_400_BAD_REQUEST)

        user_prediction = int(user_prediction)

        # Simulate a coin toss - 0 for HEAD, 1 for TAIL
        toss_result = random.choice([0, 1])

        # Determine if the prediction is correct
        prediction_correct = toss_result == user_prediction

        # Update user balance based on the prediction result
        if prediction_correct:
            # User wins, double the stake
            new_balance = update_user_balance(user, 2)
            return Response({'message': f'Prediction made successfully. You won! New balance: {new_balance}'}, status=status.HTTP_200_OK)
        else:
            # User loses, deduct the stake
            new_balance = update_user_balance(user, 0.5)
            return Response({'message': f'Prediction made successfully. You lost! New balance: {new_balance}'}, status=status.HTTP_200_OK)

# Balance updating view
@login_required
class BalanceView(APIView):
    def get(self, request):
        user = request.user

        if not user.is_authenticated:
            return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        profile = UserProfile.objects.get(user=user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
     