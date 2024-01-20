from django.urls import path, include
from rest_framework import routers
from .views import UserProfileViewSet, CoinTossViewSet

router = routers.DefaultRouter()
router.register(r'user', UserProfileViewSet, basename='user')
router.register(r'coin-toss', CoinTossViewSet, basename='coin-toss')

urlpatterns = [
    path('api/user/users/', UserProfileViewSet.as_view({'get': 'users'}), name='users'),
    path('api/user/register/', UserProfileViewSet.as_view({'post': 'register'}), name='register'),
    path('api/user/login/', UserProfileViewSet.as_view({'post': 'login'}), name='login'),
    path('api/user/logout/', UserProfileViewSet.as_view({'post': 'logout'}), name='logout'),
    path('api/coin-toss/toss-coin/', CoinTossViewSet.as_view({'post': 'toss_coin'}), name='toss-coin'),
    path('api/', include(router.urls)),
]
