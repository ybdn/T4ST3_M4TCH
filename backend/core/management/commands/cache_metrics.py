"""
Management command pour afficher les métriques de cache des APIs externes
"""

from django.core.management.base import BaseCommand
from core.services.cached_external_api_service import CachedExternalAPIService
from core.models import APICache


class Command(BaseCommand):
    help = 'Affiche les métriques de cache des APIs externes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remet à zéro les métriques',
        )
        parser.add_argument(
            '--clean-expired',
            action='store_true',
            help='Nettoie les entrées de cache expirées',
        )

    def handle(self, *args, **options):
        if options['reset']:
            CachedExternalAPIService.reset_global_metrics()
            self.stdout.write(
                self.style.SUCCESS('Métriques de cache remises à zéro')
            )
            return

        if options['clean_expired']:
            deleted_count = APICache.clean_expired()
            self.stdout.write(
                self.style.SUCCESS(f'Supprimé {deleted_count[0]} entrées de cache expirées')
            )

        # Afficher les métriques actuelles
        metrics = CachedExternalAPIService.get_global_metrics()
        
        self.stdout.write(
            self.style.SUCCESS('\n=== MÉTRIQUES DE CACHE DES APIS EXTERNES ===')
        )
        
        self.stdout.write(f"Requêtes totales: {metrics['total_requests']}")
        self.stdout.write(f"Cache hits: {metrics['hits']}")
        self.stdout.write(f"Cache misses: {metrics['misses']}")
        self.stdout.write(f"Taux de réussite: {metrics['hit_rate']}%")
        
        # Couleur selon le taux de réussite
        if metrics['hit_rate'] >= 40:
            style = self.style.SUCCESS
            status = "✓ OBJECTIF ATTEINT"
        elif metrics['hit_rate'] >= 20:
            style = self.style.WARNING  
            status = "⚠ EN COURS"
        else:
            style = self.style.ERROR
            status = "✗ INSUFFISANT"
            
        self.stdout.write(
            style(f"\nSTATUT: {status} (objectif: >40%)")
        )
        
        # Statistiques du cache en base
        total_cache_entries = APICache.objects.count()
        self.stdout.write(f"\nEntrées en cache: {total_cache_entries}")
        
        if total_cache_entries > 0:
            # Répartition par service (approximative)
            tmdb_count = APICache.objects.filter(cache_key__startswith='tmdb_').count()
            spotify_count = APICache.objects.filter(cache_key__startswith='spotify_').count()
            books_count = APICache.objects.filter(cache_key__startswith='books_').count()
            
            self.stdout.write(f"  - TMDB: {tmdb_count}")
            self.stdout.write(f"  - Spotify: {spotify_count}")
            self.stdout.write(f"  - Books: {books_count}")
            self.stdout.write(f"  - Autres: {total_cache_entries - tmdb_count - spotify_count - books_count}")