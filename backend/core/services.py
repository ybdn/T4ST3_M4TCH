"""
Services pour le système Match Global + Social
"""

import requests
import random
from typing import List as TypingList, Dict, Optional, Tuple
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .models import (
    UserPreference, UserProfile, Friendship, FriendMatch, MatchSession, 
    List as TasteList, ListItem, ExternalReference, APICache
)


class RecommendationService:
    """Service pour générer des recommandations personnalisées"""
    
    def __init__(self):
        self.tmdb_api_key = getattr(settings, 'TMDB_API_KEY', '')
        self.spotify_client_id = getattr(settings, 'SPOTIFY_CLIENT_ID', '')
        self.spotify_client_secret = getattr(settings, 'SPOTIFY_CLIENT_SECRET', '')
        self.google_books_api_key = getattr(settings, 'GOOGLE_BOOKS_API_KEY', '')
    
    def get_recommendations(self, user: User, category: str = None, count: int = 10) -> TypingList[Dict]:
        """
        Récupère des recommandations personnalisées pour un utilisateur
        
        Args:
            user: L'utilisateur pour qui générer les recommandations
            category: Catégorie spécifique (FILMS, SERIES, MUSIQUE, LIVRES) ou None pour toutes
            count: Nombre de recommandations à retourner
        
        Returns:
            Liste de dictionnaires contenant les recommandations
        """
        recommendations = []
        
        if category:
            categories = [category]
        else:
            # Rotation équilibrée entre toutes les catégories
            categories = ['FILMS', 'SERIES', 'MUSIQUE', 'LIVRES']
            random.shuffle(categories)
        
        items_per_category = max(1, count // len(categories))
        
        for cat in categories:
            try:
                if cat == 'FILMS':
                    items = self._get_movie_recommendations(user, items_per_category)
                elif cat == 'SERIES':
                    items = self._get_tv_recommendations(user, items_per_category)
                elif cat == 'MUSIQUE':
                    items = self._get_music_recommendations(user, items_per_category)
                elif cat == 'LIVRES':
                    items = self._get_book_recommendations(user, items_per_category)
                else:
                    items = []
                
                # Filtrer le contenu déjà vu/ajouté par l'utilisateur
                filtered_items = self._filter_user_content(user, items)
                recommendations.extend(filtered_items[:items_per_category])
                
            except Exception as e:
                print(f"Erreur lors de la récupération de {cat}: {e}")
                continue
        
        # Mélanger les recommandations et appliquer le scoring
        random.shuffle(recommendations)
        
        # Calculer le score de compatibilité pour chaque item
        for item in recommendations:
            item['compatibility_score'] = self._calculate_compatibility_score(user, item)
        
        # Trier par score de compatibilité (décroissant)
        recommendations.sort(key=lambda x: x['compatibility_score'], reverse=True)
        
        return recommendations[:count]
    
    def _get_movie_recommendations(self, user: User, count: int) -> TypingList[Dict]:
        """Récupère des recommandations de films via TMDB"""
        if not self.tmdb_api_key:
            return []
        
        cache_key = f"tmdb_popular_movies_{count}"
        cached_data = APICache.get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            # Récupère les films populaires
            url = "https://api.themoviedb.org/3/movie/popular"
            params = {
                'api_key': self.tmdb_api_key,
                'language': 'fr-FR',
                'page': random.randint(1, 5)  # Varier les pages pour plus de diversité
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            movies = []
            for movie in data.get('results', [])[:count * 2]:  # Prendre plus pour filtrer
                movies.append({
                    'external_id': str(movie['id']),
                    'content_type': 'FILMS',
                    'source': 'tmdb',
                    'title': movie['title'],
                    'description': movie.get('overview', ''),
                    'poster_url': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get('poster_path') else None,
                    'metadata': {
                        'release_date': movie.get('release_date'),
                        'vote_average': movie.get('vote_average'),
                        'genre_ids': movie.get('genre_ids', []),
                        'original_language': movie.get('original_language'),
                        'popularity': movie.get('popularity')
                    }
                })
            
            APICache.set_cached_data(cache_key, movies, ttl_hours=6)
            return movies
            
        except Exception as e:
            print(f"Erreur TMDB films: {e}")
            return []
    
    def _get_tv_recommendations(self, user: User, count: int) -> TypingList[Dict]:
        """Récupère des recommandations de séries via TMDB"""
        if not self.tmdb_api_key:
            return []
        
        cache_key = f"tmdb_popular_tv_{count}"
        cached_data = APICache.get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            url = "https://api.themoviedb.org/3/tv/popular"
            params = {
                'api_key': self.tmdb_api_key,
                'language': 'fr-FR',
                'page': random.randint(1, 3)
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            series = []
            for show in data.get('results', [])[:count * 2]:
                series.append({
                    'external_id': str(show['id']),
                    'content_type': 'SERIES',
                    'source': 'tmdb',
                    'title': show['name'],
                    'description': show.get('overview', ''),
                    'poster_url': f"https://image.tmdb.org/t/p/w500{show['poster_path']}" if show.get('poster_path') else None,
                    'metadata': {
                        'first_air_date': show.get('first_air_date'),
                        'vote_average': show.get('vote_average'),
                        'genre_ids': show.get('genre_ids', []),
                        'origin_country': show.get('origin_country', []),
                        'popularity': show.get('popularity')
                    }
                })
            
            APICache.set_cached_data(cache_key, series, ttl_hours=6)
            return series
            
        except Exception as e:
            print(f"Erreur TMDB séries: {e}")
            return []
    
    def _get_music_recommendations(self, user: User, count: int) -> TypingList[Dict]:
        """Récupère des recommandations musicales (simulation pour l'instant)"""
        # TODO: Implémenter l'intégration Spotify
        # Pour l'instant, on retourne des données simulées
        music_examples = [
            {
                'external_id': 'spotify_001',
                'content_type': 'MUSIQUE',
                'source': 'spotify',
                'title': 'Bohemian Rhapsody - Queen',
                'description': 'Rock classique légendaire',
                'poster_url': 'https://i.scdn.co/image/ab67616d0000b273ce4f1737bc8a646c8c4bd25a',
                'metadata': {
                    'artist': 'Queen',
                    'album': 'A Night at the Opera',
                    'duration_ms': 355000,
                    'genres': ['rock', 'classic rock']
                }
            },
            {
                'external_id': 'spotify_002',
                'content_type': 'MUSIQUE',
                'source': 'spotify',
                'title': 'Hotel California - Eagles',
                'description': 'Classique rock américain',
                'poster_url': 'https://i.scdn.co/image/ab67616d0000b273268c78b801a9caad6bdf67bb',
                'metadata': {
                    'artist': 'Eagles',
                    'album': 'Hotel California',
                    'duration_ms': 391000,
                    'genres': ['rock', 'soft rock']
                }
            }
        ]
        
        return random.sample(music_examples, min(count, len(music_examples)))
    
    def _get_book_recommendations(self, user: User, count: int) -> TypingList[Dict]:
        """Récupère des recommandations de livres via Google Books"""
        if not self.google_books_api_key:
            return self._get_fallback_books(count)
        
        cache_key = f"google_books_recommendations_{count}"
        cached_data = APICache.get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            # Recherche de livres populaires/tendances
            search_terms = ['bestseller', 'roman', 'science fiction', 'fantasy', 'thriller']
            search_term = random.choice(search_terms)
            
            url = "https://www.googleapis.com/books/v1/volumes"
            params = {
                'q': search_term,
                'key': self.google_books_api_key,
                'maxResults': count * 2,
                'orderBy': 'relevance',
                'langRestrict': 'fr'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            books = []
            for item in data.get('items', []):
                volume_info = item.get('volumeInfo', {})
                
                # Filtrer les livres sans titre ou auteur
                if not volume_info.get('title') or not volume_info.get('authors'):
                    continue
                
                thumbnail = volume_info.get('imageLinks', {}).get('thumbnail', '')
                if thumbnail:
                    # Améliorer la qualité de l'image
                    thumbnail = thumbnail.replace('zoom=1', 'zoom=0')
                
                books.append({
                    'external_id': item['id'],
                    'content_type': 'LIVRES',
                    'source': 'google_books',
                    'title': f"{volume_info['title']} - {', '.join(volume_info['authors'])}",
                    'description': volume_info.get('description', '')[:300] + '...' if volume_info.get('description') else '',
                    'poster_url': thumbnail,
                    'metadata': {
                        'authors': volume_info.get('authors', []),
                        'published_date': volume_info.get('publishedDate'),
                        'page_count': volume_info.get('pageCount'),
                        'categories': volume_info.get('categories', []),
                        'language': volume_info.get('language'),
                        'average_rating': volume_info.get('averageRating')
                    }
                })
            
            APICache.set_cached_data(cache_key, books, ttl_hours=12)
            return books[:count]
            
        except Exception as e:
            print(f"Erreur Google Books: {e}")
            return self._get_fallback_books(count)
    
    def _get_fallback_books(self, count: int) -> TypingList[Dict]:
        """Livres de fallback si l'API Google Books échoue"""
        fallback_books = [
            {
                'external_id': 'fallback_book_001',
                'content_type': 'LIVRES',
                'source': 'google_books',
                'title': 'Dune - Frank Herbert',
                'description': 'Épopée de science-fiction dans un univers désertique',
                'poster_url': '',
                'metadata': {
                    'authors': ['Frank Herbert'],
                    'categories': ['Science Fiction', 'Fantasy'],
                    'language': 'fr'
                }
            }
        ]
        
        return random.sample(fallback_books, min(count, len(fallback_books)))
    
    def _filter_user_content(self, user: User, items: TypingList[Dict]) -> TypingList[Dict]:
        """
        Filtre le contenu déjà vu ou ajouté par l'utilisateur
        """
        if not items:
            return items
        
        # Récupérer les IDs externes déjà traités par l'utilisateur
        external_ids = [item['external_id'] for item in items]
        source = items[0]['source'] if items else ''
        
        # Contenu déjà dans les préférences utilisateur
        seen_preferences = set(
            UserPreference.objects.filter(
                user=user,
                external_id__in=external_ids,
                source=source
            ).values_list('external_id', flat=True)
        )
        
        # Contenu déjà dans les listes de l'utilisateur
        seen_in_lists = set()
        user_lists = TasteList.objects.filter(owner=user)
        for user_list in user_lists:
            list_external_ids = ExternalReference.objects.filter(
                list_item__list=user_list,
                external_id__in=external_ids,
                external_source=source
            ).values_list('external_id', flat=True)
            seen_in_lists.update(list_external_ids)
        
        # Filtrer les items déjà vus
        all_seen = seen_preferences.union(seen_in_lists)
        filtered_items = [
            item for item in items 
            if item['external_id'] not in all_seen
        ]
        
        return filtered_items
    
    def _calculate_compatibility_score(self, user: User, content: Dict) -> float:
        """
        Calcule un score de compatibilité basé sur les préférences utilisateur
        """
        base_score = 50.0  # Score de base
        
        # Récupérer les préférences utilisateur pour ce type de contenu
        user_preferences = UserPreference.objects.filter(
            user=user,
            content_type=content['content_type']
        )
        
        if not user_preferences.exists():
            return base_score
        
        # Analyser les genres/catégories préférés
        liked_content = user_preferences.filter(action='liked')
        disliked_content = user_preferences.filter(action='disliked')
        
        # Bonus pour genres similaires
        content_genres = content.get('metadata', {}).get('genre_ids', [])
        if content_genres:
            # Calculer similarity avec les genres likés
            # (implémentation simplifiée pour l'instant)
            base_score += random.uniform(0, 20)
        
        # Bonus pour nouveauté vs popularité
        popularity = content.get('metadata', {}).get('popularity', 0)
        if popularity:
            base_score += min(popularity / 100, 15)  # Max +15 points
        
        # Facteur aléatoire pour découverte
        base_score += random.uniform(-10, 10)
        
        # S'assurer que le score reste dans les limites
        return max(0, min(100, base_score))
    
    def mark_content_as_seen(self, user: User, content: Dict, action: str) -> UserPreference:
        """
        Marque un contenu comme vu avec une action spécifique
        """
        preference, created = UserPreference.objects.update_or_create(
            user=user,
            external_id=content['external_id'],
            source=content['source'],
            defaults={
                'content_type': content['content_type'],
                'action': action,
                'title': content['title'],
                'metadata': content.get('metadata', {})
            }
        )
        
        # Mettre à jour les statistiques du profil utilisateur
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.total_matches += 1
        if action == 'added':
            profile.successful_matches += 1
        profile.save()
        
        return preference


class CompatibilityService:
    """Service pour calculer la compatibilité entre utilisateurs"""
    
    def calculate_friend_compatibility(self, user1: User, user2: User) -> float:
        """
        Calcule le score de compatibilité entre deux utilisateurs
        
        Returns:
            Score de compatibilité entre 0 et 100
        """
        # Récupérer les préférences des deux utilisateurs
        user1_prefs = UserPreference.objects.filter(user=user1)
        user2_prefs = UserPreference.objects.filter(user=user2)
        
        if not user1_prefs.exists() or not user2_prefs.exists():
            return 50.0  # Score neutre si pas assez de données
        
        # Analyser les contenus en commun
        common_likes = self._find_common_content(user1_prefs, user2_prefs, 'liked')
        common_dislikes = self._find_common_content(user1_prefs, user2_prefs, 'disliked')
        opposite_tastes = self._find_opposite_tastes(user1_prefs, user2_prefs)
        
        # Calculer la compatibilité par catégorie
        category_compatibility = self._calculate_category_overlap(user1_prefs, user2_prefs)
        
        # Score final
        compatibility_score = (
            len(common_likes) * 10 +        # +10 par contenu liké en commun
            len(common_dislikes) * 5 +      # +5 par contenu disliké en commun  
            category_compatibility * 20 -    # Bonus pour catégories communes
            len(opposite_tastes) * 15        # Malus pour goûts opposés
        )
        
        # Normaliser entre 0 et 100
        compatibility_score = max(0, min(100, compatibility_score))
        
        return round(compatibility_score, 2)
    
    def _find_common_content(self, user1_prefs, user2_prefs, action: str) -> TypingList[str]:
        """Trouve les contenus avec la même action pour les deux utilisateurs"""
        user1_content = set(
            user1_prefs.filter(action=action).values_list('external_id', flat=True)
        )
        user2_content = set(
            user2_prefs.filter(action=action).values_list('external_id', flat=True)
        )
        
        return list(user1_content.intersection(user2_content))
    
    def _find_opposite_tastes(self, user1_prefs, user2_prefs) -> TypingList[str]:
        """Trouve les contenus avec des actions opposées"""
        user1_likes = set(
            user1_prefs.filter(action='liked').values_list('external_id', flat=True)
        )
        user1_dislikes = set(
            user1_prefs.filter(action='disliked').values_list('external_id', flat=True)
        )
        user2_likes = set(
            user2_prefs.filter(action='liked').values_list('external_id', flat=True)
        )
        user2_dislikes = set(
            user2_prefs.filter(action='disliked').values_list('external_id', flat=True)
        )
        
        # User1 aime ce que User2 n'aime pas, et vice versa
        opposite = user1_likes.intersection(user2_dislikes)
        opposite.update(user1_dislikes.intersection(user2_likes))
        
        return list(opposite)
    
    def _calculate_category_overlap(self, user1_prefs, user2_prefs) -> float:
        """Calcule le chevauchement des catégories préférées"""
        user1_categories = set(
            user1_prefs.filter(action='liked').values_list('content_type', flat=True)
        )
        user2_categories = set(
            user2_prefs.filter(action='liked').values_list('content_type', flat=True)
        )
        
        if not user1_categories or not user2_categories:
            return 0.0
        
        intersection = len(user1_categories.intersection(user2_categories))
        union = len(user1_categories.union(user2_categories))
        
        return intersection / union if union > 0 else 0.0
    
    def get_matching_content(self, user1: User, user2: User) -> TypingList[Dict]:
        """
        Trouve le contenu que les deux utilisateurs ont aimé
        """
        common_likes = UserPreference.objects.filter(
            user=user1,
            action='liked'
        ).values_list('external_id', 'source').intersection(
            UserPreference.objects.filter(
                user=user2,
                action='liked'
            ).values_list('external_id', 'source')
        )
        
        matching_content = []
        for external_id, source in common_likes:
            pref = UserPreference.objects.filter(
                external_id=external_id,
                source=source,
                action='liked'
            ).first()
            
            if pref:
                matching_content.append({
                    'external_id': pref.external_id,
                    'content_type': pref.content_type,
                    'source': pref.source,
                    'title': pref.title,
                    'metadata': pref.metadata
                })
        
        return matching_content
    
    def generate_versus_content(self, user1: User, user2: User, count: int = 10) -> TypingList[Dict]:
        """
        Génère du contenu pour un match versus entre deux amis
        """
        recommendation_service = RecommendationService()
        
        # Mélanger les catégories équitablement
        categories = ['FILMS', 'SERIES', 'MUSIQUE', 'LIVRES']
        items_per_category = max(1, count // len(categories))
        
        versus_content = []
        
        for category in categories:
            # Récupérer des recommandations pour cette catégorie
            recommendations = recommendation_service.get_recommendations(
                user1, category, items_per_category * 2  # Plus d'items pour filtrer
            )
            
            # Filtrer aussi pour user2
            filtered_for_user2 = recommendation_service._filter_user_content(
                user2, recommendations
            )
            
            versus_content.extend(filtered_for_user2[:items_per_category])
        
        # Mélanger et retourner le nombre demandé
        random.shuffle(versus_content)
        return versus_content[:count]


class VersusMatchService:
    """Service pour gérer les matchs versus entre amis"""
    
    def create_versus_match(self, challenger: User, challenged: User, rounds: int = 10) -> FriendMatch:
        """
        Crée un nouveau match versus entre deux amis
        """
        # Vérifier que les utilisateurs sont amis
        if not Friendship.are_friends(challenger, challenged):
            raise ValueError("Les utilisateurs doivent être amis pour créer un match")
        
        # Créer le match
        match = FriendMatch.objects.create(
            user1=challenger,
            user2=challenged,
            match_type=FriendMatch.MatchType.VERSUS_CHALLENGE,
            total_rounds=rounds
        )
        
        # Générer le contenu pour tous les rounds
        compatibility_service = CompatibilityService()
        content_list = compatibility_service.generate_versus_content(
            challenger, challenged, rounds
        )
        
        # Créer les sessions pour chaque round
        for round_num, content in enumerate(content_list, 1):
            MatchSession.objects.create(
                match=match,
                round_number=round_num,
                content_external_id=content['external_id'],
                content_type=content['content_type'],
                content_source=content['source'],
                content_title=content['title'],
                content_metadata=content.get('metadata', {})
            )
        
        return match
    
    def get_current_session(self, match: FriendMatch) -> Optional[MatchSession]:
        """
        Récupère la session actuelle pour un match
        """
        if match.is_completed():
            return None
        
        return match.sessions.filter(
            round_number=match.current_round
        ).first()
    
    def submit_choice(self, match: FriendMatch, user: User, choice: str) -> Dict:
        """
        Enregistre le choix d'un utilisateur pour la session actuelle
        """
        current_session = self.get_current_session(match)
        if not current_session:
            return {'error': 'Aucune session active'}
        
        # Vérifier que l'utilisateur peut jouer ce round
        if current_session.is_completed:
            return {'error': 'Cette session est déjà terminée'}
        
        user_choice = current_session.get_user_choice(user)
        if user_choice is not None:
            return {'error': 'Vous avez déjà fait votre choix pour ce round'}
        
        # Enregistrer le choix
        current_session.set_user_choice(user, choice)
        
        # Vérifier si la session est terminée
        if current_session.is_completed:
            # Passer au round suivant
            match.next_round()
            
            # Si le match est terminé, calculer la compatibilité finale
            if match.is_completed():
                match.calculate_compatibility()
        
        return {
            'success': True,
            'session_completed': current_session.is_completed,
            'match_completed': match.is_completed(),
            'is_match': current_session.is_match if current_session.is_completed else None,
            'scores': {
                'user1': match.score_user1,
                'user2': match.score_user2
            }
        }
    
    def get_match_results(self, match: FriendMatch) -> Dict:
        """
        Récupère les résultats complets d'un match
        """
        sessions = match.sessions.all().order_by('round_number')
        
        results = {
            'match_id': match.id,
            'users': {
                'user1': {
                    'username': match.user1.username,
                    'score': match.score_user1
                },
                'user2': {
                    'username': match.user2.username,
                    'score': match.score_user2
                }
            },
            'compatibility_score': match.compatibility_score,
            'status': match.status,
            'total_rounds': match.total_rounds,
            'completed_rounds': sessions.filter(is_completed=True).count(),
            'sessions': []
        }
        
        for session in sessions:
            results['sessions'].append({
                'round_number': session.round_number,
                'content': {
                    'title': session.content_title,
                    'type': session.content_type,
                    'poster_url': session.content_metadata.get('poster_url')
                },
                'choices': {
                    'user1': session.user1_choice,
                    'user2': session.user2_choice
                },
                'is_match': session.is_match,
                'is_completed': session.is_completed
            })
        
        return results