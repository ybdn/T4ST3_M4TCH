"""
Script de test pour valider le cache warming et le hit rate
"""

from django.core.management.base import BaseCommand
from core.services.cached_external_api_service import CachedExternalAPIService
from core.services.tmdb_service import TMDBService
from core.services.spotify_service import SpotifyService
from core.services.books_service import BooksService
import time


class Command(BaseCommand):
    help = 'Test de warming du cache et validation du hit rate >40%'

    def add_arguments(self, parser):
        parser.add_argument(
            '--iterations',
            type=int,
            default=20,
            help='Nombre d\'itérations pour le test',
        )

    def handle(self, *args, **options):
        iterations = options['iterations']
        
        self.stdout.write(
            self.style.SUCCESS('=== TEST DE WARMING DU CACHE ===')
        )
        
        # Reset des métriques
        CachedExternalAPIService.reset_global_metrics()
        
        # Initialiser les services
        tmdb = TMDBService()
        spotify = SpotifyService() 
        books = BooksService()
        
        # Listes de requêtes de test
        movie_queries = [
            "The Matrix", "Inception", "Interstellar", "The Dark Knight",
            "Pulp Fiction", "Fight Club", "The Godfather", "Forrest Gump"
        ]
        
        music_queries = [
            "The Beatles", "Queen", "Pink Floyd", "Led Zeppelin",
            "Bob Dylan", "Michael Jackson", "David Bowie", "Radiohead"
        ]
        
        book_queries = [
            "Harry Potter", "Lord of the Rings", "1984", "To Kill a Mockingbird",
            "Pride and Prejudice", "The Great Gatsby", "Dune", "The Catcher in the Rye"
        ]
        
        self.stdout.write(f'Début du test avec {iterations} itérations...')
        
        start_time = time.time()
        
        for i in range(iterations):
            # Choisir des requêtes aléatoirement avec répétition pour favoriser le cache
            movie_query = movie_queries[i % len(movie_queries)]
            music_query = music_queries[i % len(music_queries)]
            book_query = book_queries[i % len(book_queries)]
            
            try:
                # Requêtes TMDB
                tmdb.search_movies(movie_query, limit=3)
                tmdb.search_tv_shows(movie_query, limit=3)
                
                # Requêtes Spotify
                spotify.search_music(music_query, limit=3)
                
                # Requêtes Books
                books.search_books(book_query, limit=3)
                
                if (i + 1) % 5 == 0:
                    self.stdout.write(f'  Itération {i + 1}/{iterations} terminée')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Erreur à l\'itération {i + 1}: {e}')
                )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Afficher les résultats
        metrics = CachedExternalAPIService.get_global_metrics()
        
        self.stdout.write(
            self.style.SUCCESS('\n=== RÉSULTATS DU TEST ===')
        )
        
        self.stdout.write(f'Durée totale: {duration:.2f} secondes')
        self.stdout.write(f'Requêtes totales: {metrics["total_requests"]}')
        self.stdout.write(f'Cache hits: {metrics["hits"]}')
        self.stdout.write(f'Cache misses: {metrics["misses"]}')
        self.stdout.write(f'Taux de réussite: {metrics["hit_rate"]}%')
        
        # Validation de l'objectif
        if metrics['hit_rate'] >= 40.0:
            self.stdout.write(
                self.style.SUCCESS(f'\n✓ OBJECTIF ATTEINT! Hit rate: {metrics["hit_rate"]}% (>40%)')
            )
            return_code = 0
        else:
            self.stdout.write(
                self.style.ERROR(f'\n✗ OBJECTIF NON ATTEINT. Hit rate: {metrics["hit_rate"]}% (<40%)')
            )
            return_code = 1
        
        # Statistiques additionnelles
        if metrics['total_requests'] > 0:
            avg_time_per_request = duration / metrics['total_requests']
            self.stdout.write(f'Temps moyen par requête: {avg_time_per_request:.3f}s')
            
            if metrics['hits'] > 0:
                cache_efficiency = (metrics['hits'] / metrics['total_requests']) * 100
                self.stdout.write(f'Efficacité du cache: {cache_efficiency:.1f}%')
        
        self.stdout.write('\nPour voir les métriques détaillées, utilisez: python manage.py cache_metrics')
        
        # Retourner le code approprié pour les scripts
        if return_code != 0:
            raise SystemExit(return_code)