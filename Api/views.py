from rest_framework import viewsets
from random import choice
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import UserProfile, CoinToss
from .serializers import UserProfileSerializer, CoinTossSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    @action(detail=False, methods=['get'])
    def all_users(self, request):
        users = User.objects.all()
        serializer = UserProfileSerializer(users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def register_user(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Both username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password)
        UserProfile.objects.create(user=user)

        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def login_user(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return Response({'message': 'User logged in successfully'})
        else:
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'])
    def logout_user(self, request):
        if request.user.is_authenticated:
            logout(request)
            return Response({'message': 'User logged out successfully'})
        else:
            return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

class CoinTossViewSet(viewsets.ModelViewSet):
    queryset = CoinToss.objects.all()
    serializer_class = CoinTossSerializer

    @action(detail=False, methods=['post'])
    def toss_coin(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        stake_amount = request.data.get('stake_amount')
        chosen_side = request.data.get('chosen_side')

        # Perform coin toss logic here and update the user's balance and create a CoinToss entry

        # Perform coin toss logic
        result = choice(['HEAD', 'TAIL'])
        win = chosen_side == result

        # Update the user's balance
        if win:
            user_profile.balance += float(stake_amount) * 2
        else:
            user_profile.balance -= float(stake_amount)

        user_profile.save()

        # Create a CoinToss entry
        coin_toss = CoinToss.objects.create(
            user=request.user,
            stake_amount=stake_amount,
            chosen_side=chosen_side,
            result=result,
            win=win
        )
        return Response({'message': 'Coin tossed successfully'})
