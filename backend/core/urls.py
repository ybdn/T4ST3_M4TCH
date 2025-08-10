from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    health_check, register_user, get_user_profile, 
    ListViewSet, ListItemViewSet,
    search_items, get_suggestions, quick_add_item,
    search_external, get_trending_external, enrich_list_item, 
    import_from_external, get_external_details,
    get_trending_suggestions, get_similar_suggestions,
    get_versus_match_state
)

router = DefaultRouter()
router.register(r'lists', ListViewSet, basename='list')
router.register(r'list-items', ListItemViewSet, basename='listitem')

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('auth/register/', register_user, name='auth_register'),
    path('users/me/', get_user_profile, name='user_profile'),
    # Search and suggestions endpoints
    path('search/', search_items, name='search_items'),
    path('suggestions/', get_suggestions, name='get_suggestions'), 
    path('quick-add/', quick_add_item, name='quick_add_item'),
    # External APIs endpoints
    path('search/external/', search_external, name='search_external'),
    path('trending/external/', get_trending_external, name='get_trending_external'),
    path('import/external/', import_from_external, name='import_from_external'),
    path('external/<str:source>/<str:external_id>/', get_external_details, name='get_external_details'),
    path('lists/<int:list_pk>/items/<int:item_pk>/enrich/', enrich_list_item, name='enrich_list_item'),
    # Nouveaux endpoints pour les suggestions enrichies
    path('suggestions/trending/<str:category>/', get_trending_suggestions, name='get_trending_suggestions'),
    path('suggestions/similar/<int:item_id>/', get_similar_suggestions, name='get_similar_suggestions'),
    # Versus endpoints
    path('versus/matches/<int:match_id>/', get_versus_match_state, name='get_versus_match_state'),
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
