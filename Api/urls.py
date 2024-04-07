from django.urls import path,include
from .views import (UserRegistrationView,MyTokenObtainPairView,EmailVerificationView,
                    ChangePasswordView,ProfileView, UserProfileUpdateView)

urlpatterns = [
    # Auth URLs
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('verify-email/<str:verification_code>/', EmailVerificationView.as_view(), name='email-verification'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('password-reset/', include('django_rest_passwordreset.urls', namespace='password-reset')),
    path('profile/', ProfileView.as_view(), name='profile'),

    # # User Profile URLs
    path('update-profile/', UserProfileUpdateView.as_view(), name='update-profile'),
    path('update-balance/', UserProfileUpdateView.as_view(), name='update-balance'),

    # # Coin Toss URLs
    # path('api/coin-toss/history/', CoinTossAPIView.as_view(), name='coin-toss-history'),
    # path('api/coin-toss/predict/', CoinTossAPIView.as_view(), name='coin-toss-predict'),
]
