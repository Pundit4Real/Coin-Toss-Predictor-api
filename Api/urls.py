from django.urls import path,include
from .views import (UserRegistrationView,MyTokenObtainPairView,EmailVerificationView,
                    PasswordResetView,ProfileView, UserProfileUpdateView, BalanceUpdateView,
                     CoinTossView)

urlpatterns = [
    # Auth URLs
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('verify-email/<str:verification_code>/', EmailVerificationView.as_view(), name='email-verification'),
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('forgot-password/', include('django_rest_passwordreset.urls', namespace='password-reset')),
    path('profile/', ProfileView.as_view(), name='profile'),

    # # User Profile URLs
    path('update-profile/', UserProfileUpdateView.as_view(), name='update-profile'),
    path('update-balance/', BalanceUpdateView.as_view(), name='update-balance'),

    # # Coin Toss URLs
    path('coin-toss/history/', CoinTossView.as_view(), name='coin_toss_history'),
    path('coin-toss/', CoinTossView.as_view(), name='coin_toss'),
]
