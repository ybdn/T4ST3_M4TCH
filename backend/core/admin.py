from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import List, ListItem, ExternalReference, APICache, BetaInvite


@admin.register(BetaInvite)
class BetaInviteAdmin(admin.ModelAdmin):
    list_display = (
        'email', 'status_display', 'created_at', 'expires_at', 
        'used_at', 'used_by_link', 'created_by'
    )
    list_filter = ('created_at', 'expires_at', 'used_at')
    search_fields = ('email', 'token', 'used_by__username', 'notes')
    readonly_fields = ('token', 'used_at', 'used_by')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Information de base', {
            'fields': ('email', 'token', 'notes')
        }),
        ('Dates', {
            'fields': ('created_at', 'expires_at', 'used_at')
        }),
        ('Utilisation', {
            'fields': ('used_by', 'created_by')
        }),
    )
    
    def status_display(self, obj):
        """Affiche le statut avec couleur"""
        if obj.is_used:
            return format_html(
                '<span style="color: green;">✓ Utilisée</span>'
            )
        elif obj.is_expired:
            return format_html(
                '<span style="color: red;">✗ Expirée</span>'
            )
        else:
            return format_html(
                '<span style="color: orange;">⏳ Active</span>'
            )
    status_display.short_description = 'Statut'
    
    def used_by_link(self, obj):
        """Lien vers l'utilisateur qui a utilisé l'invitation"""
        if obj.used_by:
            url = reverse('admin:auth_user_change', args=[obj.used_by.pk])
            return format_html('<a href="{}">{}</a>', url, obj.used_by.username)
        return '-'
    used_by_link.short_description = 'Utilisateur'
    
    actions = ['create_test_invitations', 'clean_expired_invitations']
    
    def create_test_invitations(self, request, queryset):
        """Action pour créer des invitations de test"""
        test_emails = [
            'test1@example.com',
            'test2@example.com', 
            'test3@example.com'
        ]
        
        created = 0
        for email in test_emails:
            if not BetaInvite.objects.filter(email=email, used_at__isnull=True).exists():
                BetaInvite.create_invitation(
                    email=email,
                    created_by=request.user,
                    notes='Invitation de test créée par admin'
                )
                created += 1
        
        self.message_user(request, f'{created} invitations de test créées.')
    create_test_invitations.short_description = 'Créer des invitations de test'
    
    def clean_expired_invitations(self, request, queryset):
        """Action pour nettoyer les invitations expirées"""
        count = BetaInvite.clean_expired_invitations()
        self.message_user(request, f'{count} invitations expirées supprimées.')
    clean_expired_invitations.short_description = 'Nettoyer les invitations expirées'


@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'owner', 'items_count', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'owner__username', 'description')
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Nombre d\'éléments'


@admin.register(ListItem)
class ListItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'list', 'position', 'is_watched', 'created_at')
    list_filter = ('list__category', 'is_watched', 'created_at')
    search_fields = ('title', 'description', 'list__name')


@admin.register(ExternalReference)
class ExternalReferenceAdmin(admin.ModelAdmin):
    list_display = ('list_item', 'external_source', 'external_id', 'rating', 'last_updated')
    list_filter = ('external_source', 'last_updated')
    search_fields = ('list_item__title', 'external_id')


@admin.register(APICache)
class APICacheAdmin(admin.ModelAdmin):
    list_display = ('cache_key', 'expires_at', 'created_at')
    list_filter = ('expires_at', 'created_at')
    search_fields = ('cache_key',)
    readonly_fields = ('cache_key', 'data', 'created_at')
    
    actions = ['clean_expired_cache']
    
    def clean_expired_cache(self, request, queryset):
        """Action pour nettoyer le cache expiré"""
        count = APICache.clean_expired()
        self.message_user(request, f'{count} entrées de cache expirées supprimées.')
    clean_expired_cache.short_description = 'Nettoyer le cache expiré'
