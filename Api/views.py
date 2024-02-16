from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework import viewsets, permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.http import Http404
from decimal import Decimal
import random
from .models import UserProfile, Prediction
from .serializers import UserProfileSerializer, PredictionSerializer, BalanceUpdateSerializer


User = get_user_model()

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    # registration method
    @action(detail=False, methods=['post'])
    def register(self, request):
        try:
            # Extract user registration details from the request data
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')
            password_confirm = request.data.get('password_confirm')

            # Check if required fields are provided
            if not all([first_name, username, email, password, password_confirm]):
                return Response({'error': 'All registration fields are required'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if username is unique
            if User.objects.filter(username=username).exists():
                return Response({'error': 'Username is already taken'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if email is unique
            if User.objects.filter(email=email).exists():
                return Response({'error': 'Email is already registered'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if passwords match
            if password != password_confirm:
                return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

            # Create a new user with a hashed password
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'Internal Server Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    # login method
    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.filter(email=email).first()

        if user:
            user = authenticate(request, email=user.email, password=password)

            if user:
                # Check if the user is active
                if user.is_active:
                    login(request, user)

                    # Issue a JWT token
                    refresh = RefreshToken.for_user(user)
                    data = {
                        'refresh_token': str(refresh),
                        'access_token': str(refresh.access_token),
                    }

                    user_data = {
                        'First_name': user.first_name,
                        'Last_name': user.last_name,
                        'Username': user.username,
                        'Email': user.email
                    }

                    return Response({'message': 'Login successful', 'tokens': data, "user_data": user_data}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'User is not active'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'error': 'Incorrect password'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'User with this email already exists'}, status=status.HTTP_401_UNAUTHORIZED)
        
    # logout method
    @action(detail=False, methods=['post'])
    def logout(self, request):

        user = request.user

        logout(request)

        if user:
            return Response({'message': f'{user.username} logged-out successfully'}, status=200)
        else:
            return Response({'message': 'Logout Successful'}, status=200)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def balance(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            serializer = self.get_serializer(user_profile)
            response_data = {
                'username': serializer.data['user'],
                'balance': serializer.data['balance']
            }
            return Response(response_data)
        except UserProfile.DoesNotExist:
            raise Http404("UserProfile matching query does not exist.")


    @action(detail=True, methods=['post'])
    def update_balance(self, request, pk=None):
        user_profile = self.get_object()
        serializer = BalanceUpdateSerializer(data=request.data)

        if serializer.is_valid():
            added_amount = serializer.validated_data['balance']

            # Ensure the added amount is not negative
            if added_amount <= 0:
                raise ValidationError({'balance': 'Balance update amount must be greater than zero(0).'})

            user_profile.balance += added_amount
            user_profile.save()

            return Response({'message': 'Balance updated successfully', 'New balance': f'Ghs {user_profile.balance}'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CoinTossViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer = PredictionSerializer

    @action(detail=False, methods=['get'])
    def history(self, request):
        user = request.user
        predictions = Prediction.objects.filter(user=user)
        serializer = PredictionSerializer(predictions, many=True)
        
        response_data = []
        for prediction_data in serializer.data:
            win = prediction_data['result'] == prediction_data['side_predicted']
            amount_won = float(prediction_data['stake_amount']) * 2 if win else None
            amount_lost = float(prediction_data['stake_amount']) if not win else None

            response_data.append({
                'username': user.username,
                'side_predicted': prediction_data['side_predicted'],
                'stake_amount': prediction_data['stake_amount'],
                'result': prediction_data['result'],
                'win': win,
                'amount_won': '{:.2f}'.format(amount_won) if amount_won is not None else None,
                'amount_lost': '{:.2f}'.format(amount_lost) if amount_lost is not None else None,
                'predicted_at': prediction_data['predicted_at']
            })

        return Response(response_data, status=status.HTTP_200_OK)



    @action(detail=False, methods=['post'])
    def predict(self, request):
        user = request.user
        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            raise Http404("UserProfile matching query does not exist.")

        # Coin toss logic
        result_options = ['HEAD', 'TAIL']
        result = random.choice(result_options)

        # Convert the side to upper case
        side = request.data.get('side', '').upper()

        # Ensure that the side is a valid option
        if side not in result_options:
            return Response({'error': 'Invalid side. Please choose from the options: HEAD or TAIL'}, status=status.HTTP_400_BAD_REQUEST)

        # Updating user balance accordingly
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
            side_predicted=side,
            stake_amount=stake_amount,
            result=result,
        )

        # Process the result
        if result == side:
            amount_won = 2 * stake_amount
            profile.balance += amount_won
            profile.save()
            message = f'Congratulations! You won Ghs {amount_won}. New balance: Ghs {profile.balance}'
            win = True
        else:
            amount_lost = stake_amount
            profile.balance -= amount_lost
            profile.save()
            message = f'Oops! You lost Ghs {amount_lost}. New balance: Ghs {profile.balance}'
            win = False

        # Include the desired fields in the response
        prediction_data = PredictionSerializer(prediction).data
        response_data = {
            'message': message,
            'amount_won': amount_won if win else None,
            'amount_lost': amount_lost if not win else None,
            'result': result,
            'prediction': {
                'username': user.username,
                'side_predicted': prediction_data['side_predicted'],
                'stake_amount': prediction_data['stake_amount'],
                'result': prediction_data['result'],
                'win': win,
                'predicted_at': prediction_data['predicted_at']
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)
