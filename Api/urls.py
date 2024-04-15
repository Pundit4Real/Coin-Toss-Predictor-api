from django.urls import path
from .views import (UserRegistrationView,MyTokenObtainPairView,EmailVerificationView,
                    ChangePasswordView,ProfileView, UserProfileUpdateView, BalanceUpdateView,
                    CoinTossView, ForgotPasswordView,ResetPasswordView
                     )

urlpatterns = [
    # Auth URLs
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('verify-email/<str:verification_code>/', EmailVerificationView.as_view(), name='email-verification'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),

    # User Profile URLs
    path('profile/', ProfileView.as_view(), name='profile'),
    path('update-profile/', UserProfileUpdateView.as_view(), name='update-profile'),
    path('update-balance/', BalanceUpdateView.as_view(), name='update-balance'),

    # # Coin Toss URLs
    path('coin-toss/history/', CoinTossView.as_view(), name='coin_toss_history'),
    path('coin-toss/', CoinTossView.as_view(), name='coin_toss'),
]
