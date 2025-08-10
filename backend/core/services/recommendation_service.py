"""
Service dédié aux recommandations de contenu.
Centralise la logique de recommandation pour tous les types de contenu.
"""

from typing import Dict, List, Optional, Any
from ..models import ListItem, ExternalReference, List as TasteList, APICache
import logging

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service centralisé pour les recommandations de contenu"""
    
    def __init__(self, tmdb_service=None, spotify_service=None, books_service=None):
        """Initialise le service avec les services externes optionnels"""
        self.tmdb_service = tmdb_service
        self.spotify_service = spotify_service  
        self.books_service = books_service
        
        # Lazy loading si les services ne sont pas fournis
        if not tmdb_service:
            from .tmdb_service import TMDBService
            self.tmdb_service = TMDBService()
            
        if not spotify_service:
            from .spotify_service import SpotifyService
            self.spotify_service = SpotifyService()
            
        if not books_service:
            from .books_service import BooksService
            self.books_service = BooksService()
    
    def get_recommendations_for_item(self, list_item: ListItem, limit: int = 10) -> List[Dict]:
        """
        Récupère des recommandations basées sur un élément de liste existant.
        
        Args:
            list_item: Élément de liste source
            limit: Nombre maximum de recommandations
            
        Returns:
            Liste de dictionnaires contenant les recommandations
        """
        try:
            # Vérifier s'il y a une référence externe
            external_ref = getattr(list_item, 'external_ref', None)
            
            if not external_ref:
                # Si pas de référence externe, retourner du contenu tendance
                return self.get_trending_content(list_item.list.category, limit)
            
            recommendations = self._get_recommendations_by_source(external_ref, list_item.list.category, limit)
            
            # Si aucune recommandation n'a été trouvée, utiliser le contenu tendance en fallback
            if not recommendations:
                return self.get_trending_content(list_item.list.category, limit)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations for item {list_item.id}: {e}")
            # Fallback vers le contenu tendance
            return self.get_trending_content(list_item.list.category, limit)
    
    def get_similar_content(self, list_item: ListItem, limit: int = 10) -> List[Dict]:
        """
        Récupère du contenu similaire basé sur un élément existant.
        
        Args:
            list_item: Élément de liste source
            limit: Nombre maximum d'éléments similaires
            
        Returns:
            Liste de dictionnaires contenant le contenu similaire
        """
        try:
            external_ref = getattr(list_item, 'external_ref', None)
            
            if not external_ref:
                return self.get_trending_content(list_item.list.category, limit)
            
            return self._get_similar_by_source(external_ref, list_item.list.category, limit)
            
        except Exception as e:
            logger.error(f"Error getting similar content for item {list_item.id}: {e}")
            return self.get_trending_content(list_item.list.category, limit)
    
    def get_trending_content(self, category: str = None, limit: int = 20) -> List[Dict]:
        """
        Récupère le contenu tendance pour une catégorie donnée.
        
        Args:
            category: Catégorie de contenu (FILMS, SERIES, MUSIQUE, LIVRES)
            limit: Nombre maximum d'éléments
            
        Returns:
            Liste de dictionnaires contenant le contenu tendance
        """
        results = []
        
        try:
            # Films via TMDB
            if not category or category == 'FILMS':
                trending_movies = self._get_trending_movies(limit=limit // 2 if category else limit // 4)
                results.extend(trending_movies)
            
            # Séries via TMDB  
            if not category or category == 'SERIES':
                trending_shows = self._get_trending_tv_shows(limit=limit // 2 if category else limit // 4)
                results.extend(trending_shows)
            
            # Musique via Spotify
            if not category or category == 'MUSIQUE':
                trending_music = self._get_trending_music(limit=limit // 2 if category else limit // 4)
                results.extend(trending_music)
            
            # Livres
            if not category or category == 'LIVRES':
                trending_books = self._get_trending_books(limit=limit // 2 if category else limit // 4)
                results.extend(trending_books)
            
        except Exception as e:
            logger.error(f"Error getting trending content for category {category}: {e}")
        
        return results[:limit]
    
    def get_multi_source_recommendations(self, user_preferences: Dict, limit: int = 20) -> List[Dict]:
        """
        Récupère des recommandations depuis plusieurs sources basées sur les préférences utilisateur.
        
        Args:
            user_preferences: Dictionnaire des préférences utilisateur par catégorie
            limit: Nombre total de recommandations
            
        Returns:
            Liste agrégée de recommandations depuis toutes les sources
        """
        all_recommendations = []
        
        try:
            # Distribuer le limit entre les catégories disponibles
            categories = list(user_preferences.keys())
            if not categories:
                return []
            
            limit_per_category = max(1, limit // len(categories))
            
            for category, preferences in user_preferences.items():
                try:
                    category_recs = self._get_category_recommendations(category, preferences, limit_per_category)
                    all_recommendations.extend(category_recs)
                except Exception as e:
                    logger.error(f"Error getting recommendations for category {category}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error in multi-source recommendations: {e}")
        
        return all_recommendations[:limit]
    
    def _get_recommendations_by_source(self, external_ref: ExternalReference, category: str, limit: int) -> List[Dict]:
        """Récupère des recommandations selon la source externe"""
        source = external_ref.external_source
        external_id = external_ref.external_id
        
        if source == 'tmdb':
            return self._get_tmdb_recommendations(external_id, category, limit)
        elif source == 'spotify':
            return self._get_spotify_recommendations(external_id, external_ref.metadata, limit)
        elif source in ['openlibrary', 'google_books']:
            return self._get_books_recommendations(external_id, limit)
        else:
            return self.get_trending_content(category, limit)
    
    def _get_similar_by_source(self, external_ref: ExternalReference, category: str, limit: int) -> List[Dict]:
        """Récupère du contenu similaire selon la source externe"""
        source = external_ref.external_source
        external_id = external_ref.external_id
        
        if source == 'tmdb':
            return self._get_tmdb_similar(external_id, category, limit)
        elif source == 'spotify':
            return self._get_spotify_similar(external_id, external_ref.metadata, limit)
        elif source in ['openlibrary', 'google_books']:
            return self._get_books_similar(external_id, limit)
        else:
            return self.get_trending_content(category, limit)
    
    def _get_tmdb_recommendations(self, external_id: str, category: str, limit: int) -> List[Dict]:
        """Récupère les recommandations TMDB"""
        results = []
        
        try:
            if category == 'FILMS':
                # Combiner recommandations et similaires pour plus de diversité
                recommendations = self.tmdb_service.get_recommendations_movies(int(external_id), limit // 2)
                similar = self.tmdb_service.get_similar_movies(int(external_id), limit // 2)
                results = recommendations + similar
            elif category == 'SERIES':
                recommendations = self.tmdb_service.get_recommendations_tv_shows(int(external_id), limit // 2)
                similar = self.tmdb_service.get_similar_tv_shows(int(external_id), limit // 2)
                results = recommendations + similar
            
            # Ajouter les métadonnées de catégorie
            for item in results:
                item['category'] = category
                item['category_display'] = dict(TasteList.Category.choices)[category]
                
        except Exception as e:
            logger.error(f"Error getting TMDB recommendations for {external_id}: {e}")
        
        return self._deduplicate_by_id(results)[:limit]
    
    def _get_tmdb_similar(self, external_id: str, category: str, limit: int) -> List[Dict]:
        """Récupère le contenu similaire TMDB"""
        results = []
        
        try:
            if category == 'FILMS':
                results = self.tmdb_service.get_similar_movies(int(external_id), limit)
            elif category == 'SERIES':
                results = self.tmdb_service.get_similar_tv_shows(int(external_id), limit)
            
            for item in results:
                item['category'] = category
                item['category_display'] = dict(TasteList.Category.choices)[category]
                
        except Exception as e:
            logger.error(f"Error getting TMDB similar content for {external_id}: {e}")
        
        return results
    
    def _get_spotify_recommendations(self, external_id: str, metadata: Dict, limit: int) -> List[Dict]:
        """Récupère les recommandations Spotify"""
        results = []
        
        try:
            content_type = metadata.get('type', 'track')
            
            if content_type == 'artist':
                # Pour les artistes, obtenir les artistes similaires et top tracks
                related = self.spotify_service.get_related_artists(external_id, limit // 2)
                top_tracks = self.spotify_service.get_artist_top_tracks(external_id, limit=limit // 2)
                results = related + top_tracks
            else:
                # Pour les autres types, retourner du contenu tendance
                results = self._get_trending_music(limit)
            
            for item in results:
                item['category'] = 'MUSIQUE'
                item['category_display'] = 'Musique'
                
        except Exception as e:
            logger.error(f"Error getting Spotify recommendations for {external_id}: {e}")
        
        return results[:limit]
    
    def _get_spotify_similar(self, external_id: str, metadata: Dict, limit: int) -> List[Dict]:
        """Récupère le contenu similaire Spotify"""
        results = []
        
        try:
            content_type = metadata.get('type', 'track')
            
            if content_type == 'artist':
                results = self.spotify_service.get_related_artists(external_id, limit)
            else:
                # Pour les albums/tracks, pas d'API similaire directe
                results = self._get_trending_music(limit)
            
            for item in results:
                item['category'] = 'MUSIQUE' 
                item['category_display'] = 'Musique'
                
        except Exception as e:
            logger.error(f"Error getting Spotify similar content for {external_id}: {e}")
        
        return results[:limit]
    
    def _get_books_recommendations(self, external_id: str, limit: int) -> List[Dict]:
        """Récupère les recommandations de livres"""
        results = []
        
        try:
            # Pour les livres, pas d'API de recommandation directe
            # Retourner des livres populaires
            results = self._get_trending_books(limit)
            
        except Exception as e:
            logger.error(f"Error getting books recommendations for {external_id}: {e}")
        
        return results
    
    def _get_books_similar(self, external_id: str, limit: int) -> List[Dict]:
        """Récupère le contenu similaire pour les livres"""
        results = []
        
        try:
            # Pour les livres, pas d'API similaire directe
            # Retourner des livres populaires
            results = self._get_trending_books(limit)
            
        except Exception as e:
            logger.error(f"Error getting similar books for {external_id}: {e}")
        
        return results
    
    def _get_trending_movies(self, limit: int = 20) -> List[Dict]:
        """Récupère les films tendance"""
        try:
            trending = self.tmdb_service.get_trending_movies(limit=limit)
            for movie in trending:
                movie['category'] = 'FILMS'
                movie['category_display'] = 'Films'
            return trending
        except Exception as e:
            logger.error(f"Error getting trending movies: {e}")
            return []
    
    def _get_trending_tv_shows(self, limit: int = 20) -> List[Dict]:
        """Récupère les séries tendance"""
        try:
            trending = self.tmdb_service.get_trending_tv_shows(limit=limit)
            for show in trending:
                show['category'] = 'SERIES'
                show['category_display'] = 'Séries'
            return trending
        except Exception as e:
            logger.error(f"Error getting trending TV shows: {e}")
            return []
    
    def _get_trending_music(self, limit: int = 20) -> List[Dict]:
        """Récupère la musique tendance"""
        try:
            # Combiner nouvelles sorties et playlists populaires
            new_releases = self.spotify_service.get_new_releases(limit=limit // 2)
            featured = self.spotify_service.get_featured_playlists(limit=limit // 2)
            
            results = new_releases + featured
            for item in results:
                item['category'] = 'MUSIQUE'
                item['category_display'] = 'Musique'
            
            return results[:limit]
        except Exception as e:
            logger.error(f"Error getting trending music: {e}")
            return []
    
    def _get_trending_books(self, limit: int = 20) -> List[Dict]:
        """Récupère les livres tendance"""
        try:
            trending = self.books_service.get_popular_books(limit=limit)
            for book in trending:
                book['category'] = 'LIVRES'
                book['category_display'] = 'Livres'
            return trending
        except Exception as e:
            logger.error(f"Error getting trending books: {e}")
            return []
    
    def _get_category_recommendations(self, category: str, preferences: Dict, limit: int) -> List[Dict]:
        """Récupère des recommandations pour une catégorie spécifique"""
        if not preferences:
            return self.get_trending_content(category, limit)
        
        # Ici on pourrait analyser les préférences pour des recommandations plus ciblées
        # Pour l'instant, retourner du contenu tendance
        return self.get_trending_content(category, limit)
    
    def _deduplicate_by_id(self, items: List[Dict]) -> List[Dict]:
        """Supprime les doublons basés sur external_id"""
        seen_ids = set()
        unique_items = []
        
        for item in items:
            external_id = item.get('external_id')
            if external_id and external_id not in seen_ids:
                seen_ids.add(external_id)
                unique_items.append(item)
        
        return unique_items
    
    def clear_cache(self, category: str = None) -> int:
        """
        Nettoie le cache des recommandations.
        
        Args:
            category: Catégorie spécifique à nettoyer (optionnel)
            
        Returns:
            Nombre d'entrées supprimées
        """
        try:
            if category:
                # Nettoyer le cache pour une catégorie spécifique
                cache_pattern = category.lower()
                deleted_count = APICache.objects.filter(cache_key__icontains=cache_pattern).delete()[0]
            else:
                # Nettoyer tout le cache expiré
                deleted_count = APICache.clean_expired()[0]
            
            logger.info(f"Cleared {deleted_count} cache entries for category: {category or 'all'}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, int]:
        """
        Retourne des statistiques sur le cache.
        
        Returns:
            Dictionnaire avec les statistiques du cache
        """
        try:
            from django.utils import timezone
            
            total_entries = APICache.objects.count()
            expired_entries = APICache.objects.filter(expires_at__lt=timezone.now()).count()
            active_entries = total_entries - expired_entries
            
            return {
                'total_entries': total_entries,
                'active_entries': active_entries,
                'expired_entries': expired_entries
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {'total_entries': 0, 'active_entries': 0, 'expired_entries': 0}