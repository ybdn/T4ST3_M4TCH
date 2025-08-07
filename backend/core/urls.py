from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import health_check, register_user, get_user_profile, ListViewSet

router = DefaultRouter()
router.register(r'lists', ListViewSet, basename='list')

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('auth/register/', register_user, name='auth_register'),
    path('users/me/', get_user_profile, name='user_profile'),
    path('', include(router.urls)),
]
