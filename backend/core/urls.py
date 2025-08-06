from django.urls import path
from .views import health_check, register_user, get_user_profile

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('auth/register/', register_user, name='auth_register'),
    path('users/me/', get_user_profile, name='user_profile'),
]
