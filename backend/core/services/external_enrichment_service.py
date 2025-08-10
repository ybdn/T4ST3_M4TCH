"""
Service d'enrichissement orchestrant toutes les APIs externes
Gère l'intégration et l'enrichissement automatique des éléments de liste
"""

from typing import Dict, List, Optional, Any
from ..models import ListItem, ExternalReference, List as TasteList
from .tmdb_service import TMDBService
from .spotify_service import SpotifyService
from .books_service import BooksService
import logging

logger = logging.getLogger(__name__)


class ExternalEnrichmentService:
    """Service orchestrateur pour l'enrichissement externe"""
    
    def __init__(self):
        self.tmdb = TMDBService()
        self.spotify = SpotifyService()
        self.books = BooksService()
    
    def search_external(self, query: str, category: str = None, limit: int = 10) -> List[Dict]:
        """Recherche enrichie dans toutes les APIs externes pertinentes"""
        results = []
        
        if not category or category == 'FILMS':
            # Rechercher dans TMDB pour les films
            tmdb_movies = self.tmdb.search_movies(query, limit // 4 if category else limit // 3)
            for movie in tmdb_movies:
                movie['category'] = 'FILMS'
                movie['category_display'] = 'Films'
            results.extend(tmdb_movies)
        
        if not category or category == 'SERIES':
            # Rechercher dans TMDB pour les séries
            tmdb_shows = self.tmdb.search_tv_shows(query, limit // 4 if category else limit // 3)
            for show in tmdb_shows:
                show['category'] = 'SERIES'
                show['category_display'] = 'Séries'
            results.extend(tmdb_shows)
        
        if not category or category == 'MUSIQUE':
            # Rechercher dans Spotify
            spotify_results = self.spotify.search_music(query, limit // 2 if category else limit // 3)
            for item in spotify_results:
                item['category'] = 'MUSIQUE'
                item['category_display'] = 'Musique'
            results.extend(spotify_results)
        
        if not category or category == 'LIVRES':
            # Rechercher dans les APIs de livres
            book_results = self.books.search_books(query, limit // 2 if category else limit // 3)
            for book in book_results:
                book['category'] = 'LIVRES'
                book['category_display'] = 'Livres'
            results.extend(book_results)
        
        # Trier par popularité/pertinence et limiter
        results = sorted(results, key=lambda x: x.get('popularity', 0), reverse=True)
        return results[:limit]
    
    def get_trending_content(self, category: str = None, limit: int = 20) -> List[Dict]:
        """Récupère le contenu tendance des APIs externes avec gestion d'erreur robuste"""
        results = []
        
        # Films via TMDB
        if not category or category == 'FILMS':
            try:
                trending_movies = self.tmdb.get_trending_movies(limit=limit // 2 if category else limit // 4)
                for movie in trending_movies:
                    movie['category'] = 'FILMS'
                    movie['category_display'] = 'Films'
                results.extend(trending_movies)
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des films tendance: {e}")
        
        # Séries via TMDB
        if not category or category == 'SERIES':
            try:
                trending_shows = self.tmdb.get_trending_tv_shows(limit=limit // 2 if category else limit // 4)
                for show in trending_shows:
                    show['category'] = 'SERIES'
                    show['category_display'] = 'Séries'
                results.extend(trending_shows)
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des séries tendance: {e}")
        
        # Musique via Spotify
        if not category or category == 'MUSIQUE':
            try:
                # Utiliser les nouvelles sorties et playlists en vedette
                new_releases = self.spotify.get_new_releases(limit=limit // 3 if category else limit // 6)
                for item in new_releases:
                    item['category'] = 'MUSIQUE'
                    item['category_display'] = 'Musique'
                results.extend(new_releases)
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des nouvelles sorties Spotify: {e}")
            
            try:
                featured_playlists = self.spotify.get_featured_playlists(limit=limit // 3 if category else limit // 6)
                for item in featured_playlists:
                    item['category'] = 'MUSIQUE'
                    item['category_display'] = 'Musique'
                results.extend(featured_playlists)
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des playlists Spotify: {e}")
        
        # Livres via Google Books/OpenLibrary
        if not category or category == 'LIVRES':
            try:
                popular_books = self.books.get_popular_books(limit=limit // 2 if category else limit // 4)
                for book in popular_books:
                    book['category'] = 'LIVRES'
                    book['category_display'] = 'Livres'
                results.extend(popular_books)
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des livres populaires: {e}")
        
        return results[:limit]
    
    def get_similar_content(self, list_item: ListItem, limit: int = 10) -> List[Dict]:
        """Récupère du contenu similaire basé sur un élément existant"""
        try:
            # Vérifier s'il y a une référence externe
            external_ref = getattr(list_item, 'external_ref', None)
            
            if not external_ref:
                # Si pas de référence externe, retourner du contenu tendance de la même catégorie
                return self.get_trending_content(list_item.list.category, limit)
            
            # Utiliser l'ID externe pour obtenir des recommandations
            external_id = external_ref.external_id
            source = external_ref.external_source
            category = list_item.list.category
            
            if source == 'tmdb':
                if category == 'FILMS':
                    similar = self.tmdb.get_similar_movies(int(external_id), limit)
                    recommendations = self.tmdb.get_recommendations_movies(int(external_id), limit)
                elif category == 'SERIES':
                    similar = self.tmdb.get_similar_tv_shows(int(external_id), limit)
                    recommendations = self.tmdb.get_recommendations_tv_shows(int(external_id), limit)
                else:
                    return self.get_trending_content(category, limit)
                
                # Combiner et dédupliquer
                all_results = similar + recommendations
                seen_ids = set()
                unique_results = []
                
                for item in all_results:
                    if item['external_id'] not in seen_ids and len(unique_results) < limit:
                        seen_ids.add(item['external_id'])
                        item['category'] = category
                        item['category_display'] = dict(TasteList.Category.choices)[category]
                        unique_results.append(item)
                
                return unique_results
            
            elif source == 'spotify':
                # Pour Spotify, utiliser les artistes similaires ou les meilleurs titres
                if external_ref.metadata.get('type') == 'artist':
                    similar = self.spotify.get_related_artists(external_id, limit)
                    top_tracks = self.spotify.get_artist_top_tracks(external_id, limit=5)
                else:
                    # Pour les albums/titres, retourner du contenu tendance
                    return self.get_trending_content('MUSIQUE', limit)
                
                results = []
                for item in similar:
                    item['category'] = 'MUSIQUE'
                    item['category_display'] = 'Musique'
                    results.append(item)
                
                for item in top_tracks:
                    item['category'] = 'MUSIQUE'
                    item['category_display'] = 'Musique'
                    results.append(item)
                
                return results[:limit]
            
            else:
                # Pour les livres, retourner du contenu tendance
                return self.get_trending_content('LIVRES', limit)
                
        except Exception as e:
            logger.error(f"Error getting similar content for item {list_item.id}: {e}")
            # Fallback vers le contenu tendance
            return self.get_trending_content(list_item.list.category, limit)
    
    def enrich_list_item(self, list_item: ListItem, force_refresh: bool = False) -> bool:
        """Enrichit un élément de liste avec des métadonnées externes"""
        try:
            # Vérifier s'il y a déjà une référence externe
            existing_ref = getattr(list_item, 'external_ref', None)
            
            if existing_ref and not force_refresh and not existing_ref.needs_refresh():
                logger.info(f"Item {list_item.id} already enriched and fresh")
                return True
            
            # Déterminer le service à utiliser selon la catégorie
            category = list_item.list.category
            
            if category == 'FILMS':
                return self._enrich_movie(list_item)
            elif category == 'SERIES':
                return self._enrich_tv_show(list_item)
            elif category == 'MUSIQUE':
                return self._enrich_music(list_item)
            elif category == 'LIVRES':
                return self._enrich_book(list_item)
            
            logger.warning(f"Unknown category {category} for item {list_item.id}")
            return False
            
        except Exception as e:
            logger.error(f"Error enriching item {list_item.id}: {e}")
            return False
    
    def _enrich_movie(self, list_item: ListItem) -> bool:
        """Enrichit un film avec TMDB"""
        search_results = self.tmdb.search_movies(list_item.title, limit=1)
        
        if not search_results:
            logger.info(f"No TMDB results for movie: {list_item.title}")
            return False
        
        movie_data = search_results[0]
        
        # Récupérer les détails complets
        movie_details = self.tmdb.get_movie_details(movie_data['external_id'])
        if movie_details:
            movie_data.update(movie_details)
        
        return self._create_or_update_external_ref(
            list_item, 
            movie_data,
            ExternalReference.Source.TMDB
        )
    
    def _enrich_tv_show(self, list_item: ListItem) -> bool:
        """Enrichit une série avec TMDB"""
        search_results = self.tmdb.search_tv_shows(list_item.title, limit=1)
        
        if not search_results:
            logger.info(f"No TMDB results for TV show: {list_item.title}")
            return False
        
        show_data = search_results[0]
        
        # Récupérer les détails complets
        show_details = self.tmdb.get_tv_show_details(show_data['external_id'])
        if show_details:
            show_data.update(show_details)
        
        return self._create_or_update_external_ref(
            list_item, 
            show_data,
            ExternalReference.Source.TMDB
        )
    
    def _enrich_music(self, list_item: ListItem) -> bool:
        """Enrichit un élément musical avec Spotify"""
        search_results = self.spotify.search_music(list_item.title, limit=1)
        
        if not search_results:
            logger.info(f"No Spotify results for music: {list_item.title}")
            return False
        
        music_data = search_results[0]
        
        # Récupérer les détails complets selon le type
        if music_data['type'] == 'track':
            details = self.spotify.get_track_details(music_data['external_id'])
        elif music_data['type'] == 'artist':
            details = self.spotify.get_artist_details(music_data['external_id'])
        elif music_data['type'] == 'album':
            details = self.spotify.get_album_details(music_data['external_id'])
        else:
            details = None
        
        if details:
            music_data.update(details)
        
        return self._create_or_update_external_ref(
            list_item, 
            music_data,
            ExternalReference.Source.SPOTIFY
        )
    
    def _enrich_book(self, list_item: ListItem) -> bool:
        """Enrichit un livre avec OpenLibrary/Google Books"""
        search_results = self.books.search_books(list_item.title, limit=1)
        
        if not search_results:
            logger.info(f"No book API results for: {list_item.title}")
            return False
        
        book_data = search_results[0]
        
        # Déterminer la source et créer la référence externe
        source = (ExternalReference.Source.OPENLIBRARY 
                 if book_data['source'] == 'openlibrary' 
                 else ExternalReference.Source.GOOGLE_BOOKS)
        
        return self._create_or_update_external_ref(
            list_item, 
            book_data,
            source
        )
    
    def _create_or_update_external_ref(self, list_item: ListItem, data: Dict, source: str) -> bool:
        """Crée ou met à jour une référence externe"""
        try:
            # Extraire les données principales
            external_id = data.get('external_id')
            if not external_id:
                return False
            
            # Préparer les données pour la base
            ref_data = {
                'external_id': str(external_id),
                'external_source': source,
                'poster_url': data.get('poster_url'),
                'backdrop_url': data.get('backdrop_url'),
                'rating': data.get('rating'),
                'metadata': self._clean_metadata(data),
                'user': list_item.list.owner  # Explicitly set user for performance
            }
            
            # Gérer la date de sortie
            release_date = (data.get('release_date') or 
                          data.get('first_air_date') or 
                          data.get('first_publish_year') or
                          data.get('published_date'))
            
            if release_date:
                # Convertir en format date si nécessaire
                if isinstance(release_date, str) and len(release_date) >= 4:
                    try:
                        from datetime import datetime
                        if len(release_date) == 4:  # Année seulement
                            ref_data['release_date'] = datetime(int(release_date), 1, 1).date()
                        else:  # Date complète
                            ref_data['release_date'] = datetime.strptime(release_date[:10], '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        pass
            
            # Créer ou mettre à jour
            external_ref, created = ExternalReference.objects.update_or_create(
                list_item=list_item,
                defaults=ref_data
            )
            
            logger.info(f"{'Created' if created else 'Updated'} external reference for {list_item.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating external reference: {e}")
            return False
    
    def _clean_metadata(self, data: Dict) -> Dict:
        """Nettoie les métadonnées pour stockage JSON"""
        # Supprimer les clés déjà stockées dans des champs dédiés
        excluded_keys = {
            'external_id', 'poster_url', 'backdrop_url', 'rating', 
            'release_date', 'first_air_date', 'first_publish_year', 'published_date'
        }
        
        cleaned = {}
        for key, value in data.items():
            if key not in excluded_keys and value is not None:
                # S'assurer que la valeur est sérialisable en JSON
                if isinstance(value, (str, int, float, bool, list, dict)):
                    cleaned[key] = value
        
        return cleaned
    
    def import_from_external_id(self, external_id: str, source: str, category: str, user) -> Optional[Dict]:
        """Importe directement depuis un ID externe"""
        try:
            # Récupérer les détails selon la source
            if source == 'tmdb':
                if category == 'FILMS':
                    data = self.tmdb.get_movie_details(external_id)
                elif category == 'SERIES':
                    data = self.tmdb.get_tv_show_details(external_id)
                else:
                    return None
            elif source == 'spotify':
                # Détecter le type depuis l'ID ou essayer différents types
                data = (self.spotify.get_track_details(external_id) or
                       self.spotify.get_artist_details(external_id) or
                       self.spotify.get_album_details(external_id))
            elif source in ['openlibrary', 'google_books']:
                data = self.books.get_book_details_by_isbn(external_id)
            else:
                return None
            
            if not data:
                return None
            
            # Créer l'élément de liste
            list_obj = TasteList.objects.get(owner=user, category=category)
            
            # Calculer la prochaine position
            from django.db import models
            max_position = list_obj.items.aggregate(
                max_pos=models.Max('position')
            )['max_pos'] or 0
            
            list_item = ListItem.objects.create(
                title=data['title'],
                description=data.get('description', ''),
                list=list_obj,
                position=max_position + 1
            )
            
            # Créer la référence externe
            source_mapping = {
                'tmdb': ExternalReference.Source.TMDB,
                'spotify': ExternalReference.Source.SPOTIFY,
                'openlibrary': ExternalReference.Source.OPENLIBRARY,
                'google_books': ExternalReference.Source.GOOGLE_BOOKS
            }
            
            self._create_or_update_external_ref(
                list_item, 
                data, 
                source_mapping[source]
            )
            
            return {
                'list_item': list_item,
                'external_data': data
            }
            
        except Exception as e:
            logger.error(f"Error importing from external ID {external_id}: {e}")
            return None