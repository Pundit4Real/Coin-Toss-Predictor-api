from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('predict/', PredictView.as_view(), name='predict'),
    path('balance/', BalanceView.as_view(), name='balance'),
]
