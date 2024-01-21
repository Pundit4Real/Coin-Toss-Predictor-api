# Create a new Django app or use your existing app's urls.py file.

# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, AuthViewSet, CoinTossViewSet

# Create a router and register the viewsets
router = DefaultRouter()
router.register(r'user-profiles', UserProfileViewSet, basename='user-profile')
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'coin-toss', CoinTossViewSet, basename='coin-toss')

urlpatterns = [
    path('api/', include(router.urls)),
]
