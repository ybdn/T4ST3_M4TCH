"""
Services pour le système Match Global + Social (module séparé pour éviter le conflit
avec le package core.services/)
"""

import requests
import random
import time
import logging
import hashlib
from typing import List as TypingList, Dict, Any, Optional
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .models import (
    UserPreference, UserProfile, Friendship, FriendMatch, MatchSession,
    List as TasteList, ListItem, ExternalReference, APICache
)

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service pour générer des recommandations personnalisées"""
    
    def __init__(self):
        self.tmdb_api_key = getattr(settings, 'TMDB_API_KEY', '')
        self.spotify_client_id = getattr(settings, 'SPOTIFY_CLIENT_ID', '')
        self.spotify_client_secret = getattr(settings, 'SPOTIFY_CLIENT_SECRET', '')
        self.google_books_api_key = getattr(settings, 'GOOGLE_BOOKS_API_KEY', '')
    
    def get_recommendations(self, user: User, category: str = None, count: int = 10) -> TypingList[Dict]:
        """Retourne des recommandations hétérogènes filtrant le contenu déjà vu"""
        start_time = time.time()
        logger.info(f"Getting {count} recommendations for user {user.id}, category: {category or 'ALL'}")
        
        # Collecte par catégorie
        per_category = {}
        if category:
            categories = [category]
        else:
            categories = ['FILMS', 'SERIES', 'MUSIQUE', 'LIVRES']
            random.shuffle(categories)
        items_per_category = max(1, max(1, count // len(categories)))

        for cat in categories:
            cat_start_time = time.time()
            try:
                if cat == 'FILMS':
                    items = self._get_movie_recommendations(user, items_per_category * 2)
                elif cat == 'SERIES':
                    items = self._get_tv_recommendations(user, items_per_category * 2)
                elif cat == 'MUSIQUE':
                    items = self._get_music_recommendations(user, items_per_category * 2)
                elif cat == 'LIVRES':
                    items = self._get_book_recommendations(user, items_per_category * 2)
                else:
                    items = []
                filtered_items = self._filter_user_content(user, items)
                # Calculer les scores par item
                for it in filtered_items:
                    it['compatibility_score'] = self._calculate_compatibility_score(user, it)
                # Ordonner par score décroissant à l'intérieur de la catégorie
                filtered_items.sort(key=lambda x: x.get('compatibility_score', 0), reverse=True)
                per_category[cat] = filtered_items[:items_per_category]
                
                cat_time = time.time() - cat_start_time
                logger.info(f"Category {cat}: {len(per_category[cat])} items in {cat_time:.3f}s")
            except requests.RequestException as e:
                cat_time = time.time() - cat_start_time
                logger.error(f"Network error getting {cat} recommendations: {e} (took {cat_time:.3f}s)")
                per_category[cat] = []
            except KeyError as e:
                cat_time = time.time() - cat_start_time
                logger.error(f"Key error getting {cat} recommendations: {e} (took {cat_time:.3f}s)")
                per_category[cat] = []
            except (ValueError, TypeError) as e:
                cat_time = time.time() - cat_start_time
                logger.error(f"Data error getting {cat} recommendations: {e} (took {cat_time:.3f}s)")
                per_category[cat] = []

        # Interleave: alterner les catégories pour éviter la monotonie
        mixed: TypingList[Dict] = []
        max_len = max((len(per_category.get(cat, [])) for cat in categories), default=0)
        for i in range(max_len):
            for cat in categories:
                bucket = per_category.get(cat, [])
                if i < len(bucket):
                    mixed.append(bucket[i])
                if len(mixed) >= count:
                    break
            if len(mixed) >= count:
                break

        # Vérifier l'unicité des external_id (requis par les critères d'acceptation)
        seen_ids = set()
        unique_mixed = []
        for item in mixed:
            if item['external_id'] not in seen_ids:
                seen_ids.add(item['external_id'])
                # Normaliser le DTO avant ajout à la liste finale
                self._apply_normalized_dto(item)
                unique_mixed.append(item)
        
        total_time = time.time() - start_time
        logger.info(f"Returned {len(unique_mixed)} unique recommendations in {total_time:.3f}s")
        return unique_mixed[:count]

    # ----------------------------
    # Normalisation DTO
    # ----------------------------
    def _apply_normalized_dto(self, item: Dict[str, Any]) -> None:
        """Enrichit l'item en place avec un DTO unifié:
        id, title, source, type, year, thumbnail.
        Conserve rétro-compatibilité (n'écrase pas les champs existants utilisés par le reste du code/tests).
        """
        try:
            # id
            if 'id' not in item:
                item['id'] = item.get('external_id')
            # type
            if 'type' not in item:
                item['type'] = item.get('content_type')
            # thumbnail
            if 'thumbnail' not in item:
                thumb = item.get('poster_url') or item.get('metadata', {}).get('poster_url')
                item['thumbnail'] = thumb
            # year
            if 'year' not in item:
                year = None
                md = item.get('metadata', {}) or {}
                # Chercher différentes clés de date
                date_candidates = [
                    md.get('release_date'),
                    md.get('first_air_date'),
                    md.get('published_date'),
                    md.get('first_publish_year'),
                    item.get('metadata', {}).get('publishedDate'),
                    item.get('metadata', {}).get('published_date'),
                ]
                for d in date_candidates:
                    if isinstance(d, str) and len(d) >= 4 and d[:4].isdigit():
                        year = int(d[:4])
                        break
                    if isinstance(d, int) and 1800 < d < 2500:
                        year = d
                        break
                item['year'] = year
        except Exception as e:
            logger.warning(f"DTO normalization failed for item {item.get('external_id')}: {e}")
    
    def _get_movie_recommendations(self, user: User, count: int) -> TypingList[Dict]:
        if not self.tmdb_api_key:
            return self._get_fallback_movies(count)
        cache_key = f"tmdb_popular_movies_{count}"
        cached_data = APICache.get_cached_data(cache_key)
        if cached_data:
            return cached_data
        try:
            url = "https://api.themoviedb.org/3/movie/popular"
            params = {'api_key': self.tmdb_api_key, 'language': 'fr-FR', 'page': random.randint(1, 5)}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            movies = []
            for movie in data.get('results', [])[:count * 2]:
                poster_path = movie.get('poster_path')
                backdrop_path = movie.get('backdrop_path')
                # Préférer poster, sinon backdrop
                img_path = poster_path or backdrop_path
                movies.append({
                    'external_id': str(movie['id']),
                    'content_type': 'FILMS',
                    'source': 'tmdb',
                    'title': movie['title'],
                    'description': movie.get('overview', ''),
                    'poster_url': f"https://image.tmdb.org/t/p/w500{img_path}" if img_path else None,
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
        except Exception:
            return []
    
    def _get_tv_recommendations(self, user: User, count: int) -> TypingList[Dict]:
        if not self.tmdb_api_key:
            return self._get_fallback_tv(count)
        cache_key = f"tmdb_popular_tv_{count}"
        cached_data = APICache.get_cached_data(cache_key)
        if cached_data:
            return cached_data
        try:
            url = "https://api.themoviedb.org/3/tv/popular"
            params = {'api_key': self.tmdb_api_key, 'language': 'fr-FR', 'page': random.randint(1, 3)}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            series = []
            for show in data.get('results', [])[:count * 2]:
                poster_path = show.get('poster_path')
                backdrop_path = show.get('backdrop_path')
                img_path = poster_path or backdrop_path
                series.append({
                    'external_id': str(show['id']),
                    'content_type': 'SERIES',
                    'source': 'tmdb',
                    'title': show['name'],
                    'description': show.get('overview', ''),
                    'poster_url': f"https://image.tmdb.org/t/p/w500{img_path}" if img_path else None,
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
        except Exception:
            return []
    
    def _get_music_recommendations(self, user: User, count: int) -> TypingList[Dict]:
        music_examples = [
            {
                'external_id': 'spotify_001',
                'content_type': 'MUSIQUE',
                'source': 'spotify',
                'title': 'Bohemian Rhapsody - Queen',
                'description': 'Rock classique légendaire',
                'poster_url': 'https://i.scdn.co/image/ab67616d0000b273ce4f1737bc8a646c8c4bd25a',
                'metadata': {'artist': 'Queen', 'album': 'A Night at the Opera', 'duration_ms': 355000, 'genres': ['rock', 'classic rock']}
            },
            {
                'external_id': 'spotify_002',
                'content_type': 'MUSIQUE',
                'source': 'spotify',
                'title': 'Hotel California - Eagles',
                'description': 'Classique rock américain',
                'poster_url': 'https://i.scdn.co/image/ab67616d0000b273268c78b801a9caad6bdf67bb',
                'metadata': {'artist': 'Eagles', 'album': 'Hotel California', 'duration_ms': 391000, 'genres': ['rock', 'soft rock']}
            },
            {
                'external_id': 'spotify_003', 'content_type': 'MUSIQUE', 'source': 'spotify',
                'title': 'Imagine - John Lennon', 'description': 'Folk rock',
                'poster_url': 'https://i.scdn.co/image/ab67616d0000b273e8e4f1c8c8c8c8c8c8c8c8c8', 'metadata': {'artist': 'John Lennon', 'album': 'Imagine', 'genres': ['folk rock']}
            },
            {
                'external_id': 'spotify_004', 'content_type': 'MUSIQUE', 'source': 'spotify',
                'title': 'Smells Like Teen Spirit - Nirvana', 'description': 'Grunge',
                'poster_url': 'https://i.scdn.co/image/ab67616d0000b273f8e4f1c8c8c8c8c8c8c8c8c8', 'metadata': {'artist': 'Nirvana', 'album': 'Nevermind', 'genres': ['grunge']}
            },
            {
                'external_id': 'spotify_005', 'content_type': 'MUSIQUE', 'source': 'spotify',
                'title': 'Billie Jean - Michael Jackson', 'description': 'Pop iconique',
                'poster_url': 'https://i.scdn.co/image/ab67616d0000b273d8e4f1c8c8c8c8c8c8c8c8c8', 'metadata': {'artist': 'Michael Jackson', 'album': 'Thriller', 'genres': ['pop']}
            },
            {
                'external_id': 'spotify_006', 'content_type': 'MUSIQUE', 'source': 'spotify',
                'title': 'Shape of You - Ed Sheeran', 'description': 'Pop moderne',
                'poster_url': 'https://i.scdn.co/image/ab67616d0000b273c8e4f1c8c8c8c8c8c8c8c8c8', 'metadata': {'artist': 'Ed Sheeran', 'album': 'Divide', 'genres': ['pop']}
            },
            {
                'external_id': 'spotify_007', 'content_type': 'MUSIQUE', 'source': 'spotify',
                'title': 'Lose Yourself - Eminem', 'description': 'Rap',
                'poster_url': 'https://i.scdn.co/image/ab67616d0000b273b8e4f1c8c8c8c8c8c8c8c8c8', 'metadata': {'artist': 'Eminem', 'album': '8 Mile', 'genres': ['rap']}
            },
            {
                'external_id': 'spotify_008', 'content_type': 'MUSIQUE', 'source': 'spotify',
                'title': 'Rolling in the Deep - Adele', 'description': 'Soul pop',
                'poster_url': 'https://i.scdn.co/image/ab67616d0000b273a8e4f1c8c8c8c8c8c8c8c8c8', 'metadata': {'artist': 'Adele', 'album': '21', 'genres': ['soul', 'pop']}
            },
            {
                'external_id': 'spotify_009', 'content_type': 'MUSIQUE', 'source': 'spotify',
                'title': 'One - Metallica', 'description': 'Metal',
                'poster_url': 'https://i.scdn.co/image/ab67616d0000b27398e4f1c8c8c8c8c8c8c8c8c8', 'metadata': {'artist': 'Metallica', 'album': '...And Justice for All', 'genres': ['metal']}
            },
            {
                'external_id': 'spotify_010', 'content_type': 'MUSIQUE', 'source': 'spotify',
                'title': 'Le Festin - Camille', 'description': 'Chanson française',
                'poster_url': 'https://i.scdn.co/image/ab67616d0000b27388e4f1c8c8c8c8c8c8c8c8c8', 'metadata': {'artist': 'Camille', 'album': 'Ratatouille', 'genres': ['chanson']}
            }
        ]
        return random.sample(music_examples, min(count * 2, len(music_examples)))
    
    def _get_book_recommendations(self, user: User, count: int) -> TypingList[Dict]:
        if not self.google_books_api_key:
            return self._get_fallback_books(count)
        cache_key = f"google_books_recommendations_{count}"
        cached_data = APICache.get_cached_data(cache_key)
        if cached_data:
            return cached_data
        try:
            search_terms = ['bestseller', 'roman', 'science fiction', 'fantasy', 'thriller']
            search_term = random.choice(search_terms)
            url = "https://www.googleapis.com/books/v1/volumes"
            params = {'q': search_term, 'key': self.google_books_api_key, 'maxResults': count * 2, 'orderBy': 'relevance', 'langRestrict': 'fr'}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            books = []
            for item in data.get('items', []):
                volume_info = item.get('volumeInfo', {})
                if not volume_info.get('title') or not volume_info.get('authors'):
                    continue
                thumbnail = volume_info.get('imageLinks', {}).get('thumbnail', '')
                if thumbnail:
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
        except Exception:
            return self._get_fallback_books(count)
    
    def _get_fallback_books(self, count: int) -> TypingList[Dict]:
        fallback_books = [
            {'external_id': 'fallback_book_001', 'content_type': 'LIVRES', 'source': 'google_books', 'title': 'Dune - Frank Herbert', 'description': 'SF épique', 'poster_url': '', 'metadata': {'authors': ['Frank Herbert'], 'categories': ['Science Fiction'], 'language': 'fr'}},
            {'external_id': 'fallback_book_002', 'content_type': 'LIVRES', 'source': 'google_books', 'title': 'Fondation - Isaac Asimov', 'description': 'Cycle SF', 'poster_url': '', 'metadata': {'authors': ['Isaac Asimov'], 'categories': ['Science Fiction'], 'language': 'fr'}},
            {'external_id': 'fallback_book_003', 'content_type': 'LIVRES', 'source': 'google_books', 'title': '1984 - George Orwell', 'description': 'Dystopie', 'poster_url': '', 'metadata': {'authors': ['George Orwell'], 'categories': ['Dystopie'], 'language': 'fr'}},
            {'external_id': 'fallback_book_004', 'content_type': 'LIVRES', 'source': 'google_books', 'title': 'Le Seigneur des Anneaux - J.R.R. Tolkien', 'description': 'Fantasy', 'poster_url': '', 'metadata': {'authors': ['J.R.R. Tolkien'], 'categories': ['Fantasy'], 'language': 'fr'}},
            {'external_id': 'fallback_book_005', 'content_type': 'LIVRES', 'source': 'google_books', 'title': 'Le Petit Prince - Antoine de Saint-Exupéry', 'description': 'Classique', 'poster_url': '', 'metadata': {'authors': ['Antoine de Saint-Exupéry'], 'categories': ['Conte'], 'language': 'fr'}}
        ]
        return random.sample(fallback_books, min(count * 2, len(fallback_books)))

    def _get_fallback_movies(self, count: int) -> TypingList[Dict]:
        movies = [
            {'external_id': 'fb_movie_001', 'content_type': 'FILMS', 'source': 'tmdb', 'title': 'Inception', 'description': 'Thriller SF', 'poster_url': 'https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg', 'metadata': {'genre_ids': [28, 878], 'popularity': 80}},
            {'external_id': 'fb_movie_002', 'content_type': 'FILMS', 'source': 'tmdb', 'title': 'Interstellar', 'description': 'Space opera', 'poster_url': 'https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg', 'metadata': {'genre_ids': [12, 18, 878], 'popularity': 85}},
            {'external_id': 'fb_movie_003', 'content_type': 'FILMS', 'source': 'tmdb', 'title': 'The Dark Knight', 'description': 'Action', 'poster_url': 'https://image.tmdb.org/t/p/w500/qJ2tW6WMjuxF6m6kXV1jqSXdpFq.jpg', 'metadata': {'genre_ids': [28, 80], 'popularity': 90}},
            {'external_id': 'fb_movie_004', 'content_type': 'FILMS', 'source': 'tmdb', 'title': 'Parasite', 'description': 'Drame', 'poster_url': 'https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg', 'metadata': {'genre_ids': [18, 53], 'popularity': 70}},
            {'external_id': 'fb_movie_005', 'content_type': 'FILMS', 'source': 'tmdb', 'title': 'La La Land', 'description': 'Comédie musicale', 'poster_url': 'https://image.tmdb.org/t/p/w500/uDO8zWDhfWwoFdKS4fzkUJt0Rf0.jpg', 'metadata': {'genre_ids': [35, 18], 'popularity': 65}}
        ]
        return random.sample(movies, min(count * 2, len(movies)))

    def _get_fallback_tv(self, count: int) -> TypingList[Dict]:
        shows = [
            {'external_id': 'fb_tv_001', 'content_type': 'SERIES', 'source': 'tmdb', 'title': 'Breaking Bad', 'description': 'Crime', 'poster_url': 'https://image.tmdb.org/t/p/w500/ggFHVNu6YYI5L9pCfOacjizRGt.jpg', 'metadata': {'genre_ids': [80, 18], 'popularity': 85}},
            {'external_id': 'fb_tv_002', 'content_type': 'SERIES', 'source': 'tmdb', 'title': 'Stranger Things', 'description': 'SF', 'poster_url': 'https://image.tmdb.org/t/p/w500/49WJfeN0moxb9IPfGn8AIqMGskD.jpg', 'metadata': {'genre_ids': [18, 9648, 10765], 'popularity': 90}},
            {'external_id': 'fb_tv_003', 'content_type': 'SERIES', 'source': 'tmdb', 'title': 'Game of Thrones', 'description': 'Fantasy', 'poster_url': 'https://image.tmdb.org/t/p/w500/u3bZgnGQ9T01sWNhyveQz0wH0Hl.jpg', 'metadata': {'genre_ids': [10765, 18], 'popularity': 95}},
            {'external_id': 'fb_tv_004', 'content_type': 'SERIES', 'source': 'tmdb', 'title': 'The Office', 'description': 'Comédie', 'poster_url': 'https://image.tmdb.org/t/p/w500/qWnJzyZhyTh74YkmdT4e8cDl1Yp.jpg', 'metadata': {'genre_ids': [35], 'popularity': 75}},
            {'external_id': 'fb_tv_005', 'content_type': 'SERIES', 'source': 'tmdb', 'title': 'The Mandalorian', 'description': 'Space western', 'poster_url': 'https://image.tmdb.org/t/p/w500/sWgBv7LV2PRoQgkxwlibdGXKz1S.jpg', 'metadata': {'genre_ids': [10765, 10759], 'popularity': 80}}
        ]
        return random.sample(shows, min(count * 2, len(shows)))
    
    def _filter_user_content(self, user: User, items: TypingList[Dict]) -> TypingList[Dict]:
        """Filtre le contenu déjà vu par l'utilisateur (préférences + listes)"""
        if not items:
            return items
        
        external_ids = [item['external_id'] for item in items]
        source = items[0]['source'] if items else ''
        
        # Une seule requête pour récupérer les préférences déjà vues (liked/disliked uniquement)
        seen_preferences = set(
            UserPreference.objects.filter(
                user=user,
                external_id__in=external_ids,
                source=source,
                action__in=['liked', 'disliked']
            ).values_list('external_id', flat=True)
        )
        
        # Une seule requête pour récupérer les contenus déjà dans les listes utilisateur
        seen_in_lists = set(
            ExternalReference.objects.filter(
                list_item__list__owner=user,
                external_id__in=external_ids,
                external_source=source
            ).values_list('external_id', flat=True)
        )
        
        # Union des deux sets pour les IDs à exclure
        all_seen = seen_preferences.union(seen_in_lists)
        
        # Retourner uniquement les items non vus
        filtered_items = [item for item in items if item['external_id'] not in all_seen]
        
        user_hash = hashlib.sha256(str(user.id).encode()).hexdigest()[:8]
        logger.debug(f"Filtered {len(items) - len(filtered_items)} seen items out of {len(items)} for user {user_hash}")
        return filtered_items
    
    def _calculate_compatibility_score(self, user: User, content: Dict) -> float:
        base_score = 50.0
        user_preferences = UserPreference.objects.filter(user=user, content_type=content['content_type'])
        if not user_preferences.exists():
            return base_score
        content_genres = content.get('metadata', {}).get('genre_ids', [])
        if content_genres:
            base_score += random.uniform(0, 20)
        popularity = content.get('metadata', {}).get('popularity', 0)
        if popularity:
            base_score += min(popularity / 100, 15)
        base_score += random.uniform(-10, 10)
        return max(0, min(100, base_score))
    
    def _apply_profile_stats(self, profile: 'UserProfile', action: str, created: bool, changed_action: bool, previous_action: Optional[str]):
        """Met à jour les statistiques du profil utilisateur de manière idempotente.
        Règles:
        - total_matches augmente uniquement lors de la première création de préférence.
        - successful_matches augmente si on passe à ADDED (création avec ADDED ou transition depuis une action différente de ADDED).
        """
        if created:
            profile.total_matches += 1
        if action == UserPreference.Action.ADDED and (created or (changed_action and previous_action != UserPreference.Action.ADDED)):
            profile.successful_matches += 1
        profile.save()

    def mark_content_as_seen(self, user: User, content: Dict, action: str, return_status: bool = False):
        """Upsert d'une UserPreference avec logique idempotente.
        Retourne par défaut l'objet preference. Si return_status=True, retourne
        (preference, created, changed_action, previous_action).
        """
        created = False
        changed_action = False
        prefs_qs = UserPreference.objects.filter(
            user=user,
            external_id=content['external_id'],
            source=content['source']
        )
        preference = prefs_qs.first()
        previous_action = None
        if preference is None:
            preference = UserPreference.objects.create(
                user=user,
                external_id=content['external_id'],
                source=content['source'],
                content_type=content['content_type'],
                action=action,
                title=content['title'],
                metadata=content.get('metadata', {})
            )
            created = True
            # changed_action = True car il n'y avait pas d'action préalable
            changed_action = True  # création initiale
        else:
            previous_action = preference.action
            # Mettre à jour uniquement si quelque chose change
            if (preference.action != action or
                preference.content_type != content['content_type'] or
                preference.title != content['title'] or
                preference.metadata != content.get('metadata', {})):
                if preference.action != action:
                    changed_action = True
                preference.content_type = content['content_type']
                preference.action = action
                preference.title = content['title']
                preference.metadata = content.get('metadata', {})
                preference.save()

        # Gestion stats profil via helper idempotent
        profile, _ = UserProfile.objects.get_or_create(user=user)
        self._apply_profile_stats(profile, action, created, changed_action, previous_action)

        if return_status:
            return preference, created, changed_action, previous_action
        return preference


class CompatibilityService:
    def calculate_friend_compatibility(self, user1: User, user2: User) -> float:
        user1_prefs = UserPreference.objects.filter(user=user1)
        user2_prefs = UserPreference.objects.filter(user=user2)
        if not user1_prefs.exists() or not user2_prefs.exists():
            return 50.0
        common_likes = self._find_common_content(user1_prefs, user2_prefs, 'liked')
        common_dislikes = self._find_common_content(user1_prefs, user2_prefs, 'disliked')
        opposite_tastes = self._find_opposite_tastes(user1_prefs, user2_prefs)
        category_compatibility = self._calculate_category_overlap(user1_prefs, user2_prefs)
        compatibility_score = (
            len(common_likes) * 10 + len(common_dislikes) * 5 + category_compatibility * 20 - len(opposite_tastes) * 15
        )
        compatibility_score = max(0, min(100, compatibility_score))
        return round(compatibility_score, 2)
    
    def _find_common_content(self, user1_prefs, user2_prefs, action: str) -> TypingList[str]:
        user1_content = set(user1_prefs.filter(action=action).values_list('external_id', flat=True))
        user2_content = set(user2_prefs.filter(action=action).values_list('external_id', flat=True))
        return list(user1_content.intersection(user2_content))
    
    def _find_opposite_tastes(self, user1_prefs, user2_prefs) -> TypingList[str]:
        user1_likes = set(user1_prefs.filter(action='liked').values_list('external_id', flat=True))
        user1_dislikes = set(user1_prefs.filter(action='disliked').values_list('external_id', flat=True))
        user2_likes = set(user2_prefs.filter(action='liked').values_list('external_id', flat=True))
        user2_dislikes = set(user2_prefs.filter(action='disliked').values_list('external_id', flat=True))
        opposite = user1_likes.intersection(user2_dislikes)
        opposite.update(user1_dislikes.intersection(user2_likes))
        return list(opposite)
    
    def _calculate_category_overlap(self, user1_prefs, user2_prefs) -> float:
        user1_categories = set(user1_prefs.filter(action='liked').values_list('content_type', flat=True))
        user2_categories = set(user2_prefs.filter(action='liked').values_list('content_type', flat=True))
        if not user1_categories or not user2_categories:
            return 0.0
        intersection = len(user1_categories.intersection(user2_categories))
        union = len(user1_categories.union(user2_categories))
        return intersection / union if union > 0 else 0.0
    
    def get_matching_content(self, user1: User, user2: User) -> TypingList[Dict]:
        common_likes_user1 = set(UserPreference.objects.filter(user=user1, action='liked').values_list('external_id', 'source'))
        common_likes_user2 = set(UserPreference.objects.filter(user=user2, action='liked').values_list('external_id', 'source'))
        common = common_likes_user1.intersection(common_likes_user2)
        matching_content = []
        for external_id, source in common:
            pref = UserPreference.objects.filter(external_id=external_id, source=source, action='liked').first()
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
        recommendation_service = RecommendationService()
        categories = ['FILMS', 'SERIES', 'MUSIQUE', 'LIVRES']
        items_per_category = max(1, count // len(categories))
        versus_content = []
        for category in categories:
            recommendations = recommendation_service.get_recommendations(user1, category, items_per_category * 2)
            filtered_for_user2 = recommendation_service._filter_user_content(user2, recommendations)
            versus_content.extend(filtered_for_user2[:items_per_category])
        random.shuffle(versus_content)
        return versus_content[:count]


class VersusMatchService:
    def create_versus_match(self, challenger: User, challenged: User, rounds: int = 10) -> FriendMatch:
        if not Friendship.are_friends(challenger, challenged):
            raise ValueError("Les utilisateurs doivent être amis pour créer un match")
        match = FriendMatch.objects.create(
            user1=challenger,
            user2=challenged,
            match_type=FriendMatch.MatchType.VERSUS_CHALLENGE,
            total_rounds=rounds
        )
        compatibility_service = CompatibilityService()
        content_list = compatibility_service.generate_versus_content(challenger, challenged, rounds)
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
        if match.is_completed():
            return None
        return match.sessions.filter(round_number=match.current_round).first()
    
    def submit_choice(self, match: FriendMatch, user: User, choice: str) -> Dict:
        current_session = self.get_current_session(match)
        if not current_session:
            return {'error': 'Aucune session active'}
        if current_session.is_completed:
            return {'error': 'Cette session est déjà terminée'}
        user_choice = current_session.get_user_choice(user)
        if user_choice is not None:
            return {'error': 'Vous avez déjà fait votre choix pour ce round'}
        current_session.set_user_choice(user, choice)
        if current_session.is_completed:
            match.next_round()
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
        sessions = match.sessions.all().order_by('round_number')
        results = {
            'match_id': match.id,
            'users': {
                'user1': {'username': match.user1.username, 'score': match.score_user1},
                'user2': {'username': match.user2.username, 'score': match.score_user2}
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
                'choices': {'user1': session.user1_choice, 'user2': session.user2_choice},
                'is_match': session.is_match,
                'is_completed': session.is_completed
            })
        return results


