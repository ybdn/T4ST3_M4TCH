from django.contrib import admin
from .models import List, ListItem, ExternalReference, APICache, VersusMatch, VersusRound, VersusChoice


@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'owner', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'owner__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ListItem)
class ListItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'list', 'position', 'is_watched', 'created_at')
    list_filter = ('list__category', 'is_watched', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ExternalReference)
class ExternalReferenceAdmin(admin.ModelAdmin):
    list_display = ('list_item', 'external_source', 'external_id', 'rating', 'created_at')
    list_filter = ('external_source', 'created_at')
    search_fields = ('external_id', 'list_item__title')
    readonly_fields = ('created_at', 'last_updated')


@admin.register(APICache)
class APICacheAdmin(admin.ModelAdmin):
    list_display = ('cache_key', 'expires_at', 'created_at')
    list_filter = ('expires_at', 'created_at')
    search_fields = ('cache_key',)
    readonly_fields = ('created_at',)


@admin.register(VersusMatch)
class VersusMatchAdmin(admin.ModelAdmin):
    list_display = ('player1', 'player2', 'category', 'status', 'current_round', 'player1_score', 'player2_score', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('player1__username', 'player2__username')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')


@admin.register(VersusRound)
class VersusRoundAdmin(admin.ModelAdmin):
    list_display = ('match', 'round_number', 'item1', 'item2', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('match__player1__username', 'match__player2__username', 'item1__title', 'item2__title')
    readonly_fields = ('created_at', 'completed_at')


@admin.register(VersusChoice)
class VersusChoiceAdmin(admin.ModelAdmin):
    list_display = ('round', 'player', 'chosen_item', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('player__username', 'chosen_item__title')
    readonly_fields = ('created_at',)
