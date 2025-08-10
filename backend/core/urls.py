from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    health_check, register_user, get_user_profile, 
    ListViewSet, ListItemViewSet,
    search_items, get_suggestions, quick_add_item,
    search_external, get_trending_external, enrich_list_item, 
    import_from_external, get_external_details,
    get_trending_suggestions, get_similar_suggestions,
    # Match Global + Social endpoints
    get_match_recommendations, submit_match_action,
    get_user_social_profile, get_user_social_profile_me, update_user_social_profile,
    add_friend_by_gamertag, get_friends_list, get_friend_requests,
    respond_friend_request, search_user_by_gamertag, delete_friend,
    create_versus_match, get_versus_matches,
    get_versus_match_session, submit_versus_choice, get_versus_match_results,
    # Configuration endpoint
    get_config
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
    # Manual enrichment endpoints removed - enrichment is now automatic
    # Nouveaux endpoints pour les suggestions enrichies
    path('suggestions/trending/<str:category>/', get_trending_suggestions, name='get_trending_suggestions'),
    path('suggestions/similar/<int:item_id>/', get_similar_suggestions, name='get_similar_suggestions'),
    
    # ========================================
    # ENDPOINTS SYSTÈME MATCH GLOBAL + SOCIAL
    # ========================================
    
    # Match Global endpoints
    path('match/recommendations/', get_match_recommendations, name='match_recommendations'),
    path('match/action/', submit_match_action, name='submit_match_action'),
    
    # Social Profile endpoints
    path('social/profile/', get_user_social_profile, name='social_profile'),  # legacy
    path('social/profile/me/', get_user_social_profile_me, name='social_profile_me'),
    path('social/profile/update/', update_user_social_profile, name='update_social_profile'),
    
    # Friends Management endpoints
    path('social/friends/add/', add_friend_by_gamertag, name='add_friend'),
    path('social/search/<str:gamertag>/', search_user_by_gamertag, name='search_user_by_gamertag'),
    path('social/friends/', get_friends_list, name='friends_list'),
    path('social/friends/requests/', get_friend_requests, name='friend_requests'),
    path('social/friends/requests/<int:friendship_id>/respond/', respond_friend_request, name='respond_friend_request'),
    path('social/friends/<int:user_id>/', delete_friend, name='delete_friend'),
    
    # Versus Match endpoints
    path('versus/create/', create_versus_match, name='create_versus_match'),
    path('versus/matches/', get_versus_matches, name='versus_matches'),
    path('versus/matches/<int:match_id>/session/', get_versus_match_session, name='versus_match_session'),
    path('versus/matches/<int:match_id>/choice/', submit_versus_choice, name='submit_versus_choice'),
    path('versus/matches/<int:match_id>/results/', get_versus_match_results, name='versus_match_results'),
    
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
