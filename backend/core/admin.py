from django.contrib import admin
from .models import List, ListItem, ExternalReference, APICache, VersusMatch, VersusParticipant, VersusRound, VersusVote


@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'owner', 'created_at', 'items_count']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'owner__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Nombre d\'éléments'


@admin.register(ListItem)
class ListItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'list', 'position', 'is_watched', 'created_at']
    list_filter = ['is_watched', 'list__category', 'created_at']
    search_fields = ['title', 'description', 'list__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ExternalReference)
class ExternalReferenceAdmin(admin.ModelAdmin):
    list_display = ['list_item', 'external_source', 'external_id', 'rating', 'last_updated']
    list_filter = ['external_source', 'last_updated']
    search_fields = ['external_id', 'list_item__title']
    readonly_fields = ['created_at', 'last_updated']


@admin.register(APICache)
class APICacheAdmin(admin.ModelAdmin):
    list_display = ['cache_key', 'expires_at', 'created_at']
    list_filter = ['expires_at', 'created_at']
    search_fields = ['cache_key']
    readonly_fields = ['created_at']


class VersusParticipantInline(admin.TabularInline):
    model = VersusParticipant
    extra = 0
    readonly_fields = ['joined_at']


class VersusRoundInline(admin.TabularInline):
    model = VersusRound
    extra = 0
    readonly_fields = ['created_at', 'completed_at']


@admin.register(VersusMatch)
class VersusMatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'status', 'current_round', 'max_rounds', 'completed', 'created_by', 'created_at']
    list_filter = ['category', 'status', 'completed', 'created_at']
    search_fields = ['created_by__username']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    inlines = [VersusParticipantInline, VersusRoundInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(VersusParticipant)
class VersusParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'match', 'score', 'joined_at']
    list_filter = ['joined_at', 'match__category']
    search_fields = ['user__username', 'match__id']
    readonly_fields = ['joined_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'match')


class VersusVoteInline(admin.TabularInline):
    model = VersusVote
    extra = 0
    readonly_fields = ['voted_at']


@admin.register(VersusRound)
class VersusRoundAdmin(admin.ModelAdmin):
    list_display = ['match', 'round_number', 'status', 'item1', 'item2', 'winner_item', 'votes_count', 'created_at']
    list_filter = ['status', 'created_at', 'match__category']
    search_fields = ['match__id', 'item1__title', 'item2__title']
    readonly_fields = ['created_at', 'completed_at']
    inlines = [VersusVoteInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('match', 'item1', 'item2', 'winner_item')
    
    def votes_count(self, obj):
        return obj.votes.count()
    votes_count.short_description = 'Nombre de votes'


@admin.register(VersusVote)
class VersusVoteAdmin(admin.ModelAdmin):
    list_display = ['participant', 'round', 'chosen_item', 'voted_at']
    list_filter = ['voted_at', 'round__match__category']
    search_fields = ['participant__user__username', 'chosen_item__title']
    readonly_fields = ['voted_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('participant__user', 'round__match', 'chosen_item')


# Register your models here.
