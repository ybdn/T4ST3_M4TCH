from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import health_check, register_user, get_user_profile, ListViewSet, ListItemViewSet

router = DefaultRouter()
router.register(r'lists', ListViewSet, basename='list')
router.register(r'list-items', ListItemViewSet, basename='listitem')

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('auth/register/', register_user, name='auth_register'),
    path('users/me/', get_user_profile, name='user_profile'),
    # Nested routes for list items
    path('lists/<int:list_pk>/items/', ListItemViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='list-items-list'),
    path('lists/<int:list_pk>/items/<int:pk>/', ListItemViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='list-items-detail'),
    path('', include(router.urls)),
]
