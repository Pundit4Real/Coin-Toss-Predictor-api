from django.urls import path,include
from .views import (UserRegistrationView,MyTokenObtainPairView,EmailVerificationAPIView,
                    ChangePasswordView,ProfileAPiView)

urlpatterns = [
    # Auth URLs
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('verify_email/<str:verification_code>/', EmailVerificationAPIView.as_view(), name='email-verification'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('profile/', ProfileAPiView.as_view(), name='profile'),

    # path('api/auth/logout/', LogoutAPIView.as_view(), name='logout'),

    # # User Profile URLs
    # path('api/user-profiles/', UserProfileAPIView.as_view(), name='user-profile-list'),
    # path('api/user-profiles/balance/', UserProfileAPIView.as_view(), name='user-profile-balance'),
    # path('api/user-profiles/<int:pk>/update_balance/', UserProfileAPIView.as_view(), name='user-profile-update-balance'),

    # # Coin Toss URLs
    # path('api/coin-toss/history/', CoinTossAPIView.as_view(), name='coin-toss-history'),
    # path('api/coin-toss/predict/', CoinTossAPIView.as_view(), name='coin-toss-predict'),
]
