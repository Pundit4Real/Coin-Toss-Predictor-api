from rest_framework import viewsets, permissions,status
from django.contrib.auth import authenticate, login, logout
from .models import UserProfile
from .serializers import UserProfileSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.http import Http404
import random
from decimal import Decimal

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def balance(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            serializer = self.get_serializer(user_profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            raise Http404("UserProfile matching query does not exist.")
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
            return Response({'message': 'Login successful'}, status=200)
        else:
            return Response({'error': 'Invalid credentials'}, status=401)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'message': 'Logout successful'}, status=200)


class CoinTossViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def predict(self, request):
        user = request.user

        try:
            profile = user.profile  # Assuming a one-to-one relationship between User and UserProfile
        except UserProfile.DoesNotExist:
            # Create a UserProfile for the user if it doesn't exist
            profile = UserProfile.objects.create(user=user, balance=0.0)

        result = random.choice(['HEAD', 'TAIL'])  # Simulating the coin toss

        # Update user balance accordingly
        stake_amount = Decimal(float(request.data.get('stake_amount', 0.0)))

        if isinstance(stake_amount, (int, float)) and stake_amount > 0:
            if result == 'HEAD':
                profile.balance += 2 * stake_amount
                profile.save()
                message = f'Congratulations! You won {2 * stake_amount} units. New balance: {profile.balance}'
            else:
                profile.balance -= stake_amount
                profile.save()
                message = f'Oops! You lost {stake_amount} units. New balance: {profile.balance}'

            return Response({'message': message, 'result': result}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid stake amount'}, status=status.HTTP_400_BAD_REQUEST)
