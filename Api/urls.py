from django.urls import path
from .views import RegisterAPIView, LoginAPIView, LogoutAPIView, UserProfileAPIView, CoinTossAPIView

urlpatterns = [
    # Auth URLs
    path('api/auth/register/', RegisterAPIView.as_view(), name='register'),
    path('api/auth/login/', LoginAPIView.as_view(), name='login'),
    path('api/auth/logout/', LogoutAPIView.as_view(), name='logout'),

    # User Profile URLs
    path('api/user-profiles/', UserProfileAPIView.as_view(), name='user-profile-list'),
    path('api/user-profiles/balance/', UserProfileAPIView.as_view(), name='user-profile-balance'),
    path('api/user-profiles/<int:pk>/update_balance/', UserProfileAPIView.as_view(), name='user-profile-update-balance'),

    # Coin Toss URLs
    path('api/coin-toss/history/', CoinTossAPIView.as_view(), name='coin-toss-history'),
    path('api/coin-toss/predict/', CoinTossAPIView.as_view(), name='coin-toss-predict'),
]
