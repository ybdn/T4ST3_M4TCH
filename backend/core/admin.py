from django.contrib import admin
from .models import (
    List, ListItem, ExternalReference, APICache,
    UserProfile, UserPreference, Friendship, 
    FriendMatch, MatchSession, FeatureFlag
)


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    """Admin pour les feature flags"""
    
    list_display = ('name', 'enabled', 'rollout_percentage', 'description_short', 'updated_at')
    list_filter = ('enabled', 'rollout_percentage', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    fields = ('name', 'enabled', 'rollout_percentage', 'description')
    
    def description_short(self, obj):
        """Description tronquée pour l'affichage en liste"""
        if obj.description:
            return obj.description[:50] + ('...' if len(obj.description) > 50 else '')
        return '-'
    description_short.short_description = 'Description'
    
    def save_model(self, request, obj, form, change):
        """Sauvegarder le modèle avec validation"""
        super().save_model(request, obj, form, change)


# Enregistrement optionnel des autres modèles pour le debug/admin
@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'owner', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'owner__username')


@admin.register(ListItem)
class ListItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'list', 'position', 'is_watched', 'created_at')
    list_filter = ('is_watched', 'list__category', 'created_at')
    search_fields = ('title', 'description')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'gamertag', 'user', 'total_matches', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('display_name', 'gamertag', 'user__username')


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'action', 'content_type', 'source', 'created_at')
    list_filter = ('action', 'content_type', 'source', 'created_at')
    search_fields = ('title', 'user__username', 'external_id')


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('requester', 'addressee', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('requester__username', 'addressee__username')
