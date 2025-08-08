"""
Service pour l'intégration avec les APIs de livres
Combine OpenLibrary et Google Books pour enrichissement maximal
"""

import requests
from typing import Dict, List, Optional, Any
from django.conf import settings
from ..models import APICache
import hashlib
import logging

logger = logging.getLogger(__name__)


class BooksService:
    """Service pour les APIs de livres (OpenLibrary + Google Books)"""
    
    OPENLIBRARY_BASE_URL = "https://openlibrary.org"
    GOOGLE_BOOKS_BASE_URL = "https://www.googleapis.com/books/v1"
    
    def __init__(self):
        self.google_api_key = getattr(settings, 'GOOGLE_BOOKS_API_KEY', None)
        if not self.google_api_key:
            logger.warning("GOOGLE_BOOKS_API_KEY not configured, using basic access")
    
    def _make_request(self, url: str, params: Dict = None, service: str = "openlibrary") -> Optional[Dict]:
        """Effectue une requête avec gestion d'erreur et cache"""
        if params is None:
            params = {}
        
        # Clé de cache
        cache_key = f"books_{service}_{hashlib.md5(f'{url}_{str(params)}'.encode()).hexdigest()}"
        
        # Vérifier le cache
        cached_data = APICache.get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Mettre en cache pour 12 heures
            APICache.set_cached_data(cache_key, data, ttl_hours=12)
            
            return data
            
        except requests.RequestException as e:
            logger.error(f"{service} API error for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error with {service} API: {e}")
            return None
    
    def search_books(self, query: str, limit: int = 10) -> List[Dict]:
        """Recherche de livres combinant OpenLibrary et Google Books"""
        results = []
        
        # Rechercher sur OpenLibrary d'abord
        ol_results = self._search_openlibrary(query, limit // 2)
        results.extend(ol_results)
        
        # Compléter avec Google Books
        remaining = limit - len(results)
        if remaining > 0:
            gb_results = self._search_google_books(query, remaining)
            results.extend(gb_results)
        
        # Dédupliquer par titre (approximatif)
        seen_titles = set()
        unique_results = []
        for book in results:
            title_key = book['title'].lower().strip()
            if title_key not in seen_titles and title_key:
                seen_titles.add(title_key)
                unique_results.append(book)
        
        return unique_results[:limit]
    
    def get_popular_books(self, limit: int = 20) -> List[Dict]:
        """Récupère des livres populaires (basé sur des listes prédéfinies)"""
        popular_books = [
            {
                'title': 'Le Seigneur des Anneaux',
                'author': 'J.R.R. Tolkien',
                'description': 'Épopée fantasy classique',
                'isbn': '9782070612880',
                'source': 'openlibrary'
            },
            {
                'title': '1984',
                'author': 'George Orwell',
                'description': 'Roman dystopique',
                'isbn': '9782070368228',
                'source': 'openlibrary'
            },
            {
                'title': 'Harry Potter à l\'école des sorciers',
                'author': 'J.K. Rowling',
                'description': 'Premier tome de la série Harry Potter',
                'isbn': '9782070541270',
                'source': 'openlibrary'
            },
            {
                'title': 'L\'Étranger',
                'author': 'Albert Camus',
                'description': 'Roman philosophique',
                'isbn': '9782070360024',
                'source': 'openlibrary'
            },
            {
                'title': 'Le Petit Prince',
                'author': 'Antoine de Saint-Exupéry',
                'description': 'Conte philosophique',
                'isbn': '9782070612758',
                'source': 'openlibrary'
            }
        ]
        
        results = []
        for book in popular_books[:limit]:
            results.append(self._format_book(book))
        
        return results
    
    def get_books_by_author(self, author: str, limit: int = 10) -> List[Dict]:
        """Récupère les livres d'un auteur"""
        # Recherche par nom d'auteur
        query = f"author:{author}"
        return self.search_books(query, limit)
    
    def get_books_by_genre(self, genre: str, limit: int = 10) -> List[Dict]:
        """Récupère les livres d'un genre"""
        # Recherche par genre
        query = f"subject:{genre}"
        return self.search_books(query, limit)
    
    def _search_openlibrary(self, query: str, limit: int = 10) -> List[Dict]:
        """Recherche spécifique sur OpenLibrary"""
        url = f"{self.OPENLIBRARY_BASE_URL}/search.json"
        params = {
            'q': query,
            'limit': limit,
            'fields': 'key,title,author_name,first_publish_year,isbn,cover_i,publisher,subject,language,number_of_pages_median'
        }
        
        data = self._make_request(url, params, "openlibrary")
        if not data:
            return []
        
        results = []
        for book in data.get('docs', []):
            formatted = self._format_openlibrary_book(book)
            if formatted:
                results.append(formatted)
        
        return results
    
    def _search_google_books(self, query: str, limit: int = 10) -> List[Dict]:
        """Recherche spécifique sur Google Books"""
        url = f"{self.GOOGLE_BOOKS_BASE_URL}/volumes"
        params = {
            'q': query,
            'maxResults': min(limit, 40),  # Max 40 pour Google Books
            'langRestrict': 'fr',  # Privilégier le français
            'orderBy': 'relevance'
        }
        
        if self.google_api_key:
            params['key'] = self.google_api_key
        
        data = self._make_request(url, params, "google_books")
        if not data:
            return []
        
        results = []
        for book in data.get('items', []):
            formatted = self._format_google_book(book)
            if formatted:
                results.append(formatted)
        
        return results
    
    def get_book_details_by_isbn(self, isbn: str) -> Optional[Dict]:
        """Récupère les détails d'un livre via ISBN"""
        # Essayer OpenLibrary d'abord
        ol_result = self._get_openlibrary_by_isbn(isbn)
        if ol_result:
            return ol_result
        
        # Essayer Google Books
        gb_result = self._get_google_book_by_isbn(isbn)
        return gb_result
    
    def _get_openlibrary_by_isbn(self, isbn: str) -> Optional[Dict]:
        """Récupère un livre d'OpenLibrary par ISBN"""
        url = f"{self.OPENLIBRARY_BASE_URL}/isbn/{isbn}.json"
        data = self._make_request(url, service="openlibrary")
        
        if data:
            return self._format_openlibrary_book_details(data)
        return None
    
    def _get_google_book_by_isbn(self, isbn: str) -> Optional[Dict]:
        """Récupère un livre de Google Books par ISBN"""
        url = f"{self.GOOGLE_BOOKS_BASE_URL}/volumes"
        params = {
            'q': f'isbn:{isbn}'
        }
        
        if self.google_api_key:
            params['key'] = self.google_api_key
        
        data = self._make_request(url, params, "google_books")
        
        if data and data.get('items'):
            return self._format_google_book(data['items'][0])
        return None
    
    def _format_openlibrary_book(self, book_data: Dict) -> Optional[Dict]:
        """Formate les données d'OpenLibrary"""
        if not book_data.get('title'):
            return None
        
        # Construire l'URL de couverture
        cover_url = None
        if book_data.get('cover_i'):
            cover_url = f"https://covers.openlibrary.org/b/id/{book_data['cover_i']}-L.jpg"
        
        # Récupérer les auteurs
        authors = book_data.get('author_name', [])
        author_str = ', '.join(authors) if authors else 'Auteur inconnu'
        
        # Récupérer les sujets/genres
        subjects = book_data.get('subject', [])
        genres = subjects[:3] if subjects else []
        
        return {
            'external_id': book_data.get('key', '').replace('/works/', ''),
            'title': book_data.get('title', ''),
            'authors': authors,
            'description': f"Par {author_str}" + (f" - Genres: {', '.join(genres)}" if genres else ""),
            'poster_url': cover_url,
            'first_publish_year': book_data.get('first_publish_year'),
            'publishers': book_data.get('publisher', []),
            'isbn': book_data.get('isbn', []),
            'subjects': subjects,
            'languages': book_data.get('language', []),
            'page_count': book_data.get('number_of_pages_median'),
            'source': 'openlibrary',
            'type': 'book'
        }
    
    def _format_google_book(self, book_data: Dict) -> Optional[Dict]:
        """Formate les données de Google Books"""
        volume_info = book_data.get('volumeInfo', {})
        
        if not volume_info.get('title'):
            return None
        
        # Récupérer la meilleure image de couverture
        images = volume_info.get('imageLinks', {})
        cover_url = (images.get('large') or 
                    images.get('medium') or 
                    images.get('small') or 
                    images.get('thumbnail'))
        
        # Convertir en HTTPS si nécessaire
        if cover_url and cover_url.startswith('http://'):
            cover_url = cover_url.replace('http://', 'https://')
        
        authors = volume_info.get('authors', [])
        author_str = ', '.join(authors) if authors else 'Auteur inconnu'
        
        # Description enrichie
        description = volume_info.get('description', '')
        if not description:
            description = f"Par {author_str}"
            if volume_info.get('categories'):
                description += f" - Genre: {', '.join(volume_info['categories'][:2])}"
        
        return {
            'external_id': book_data.get('id'),
            'title': volume_info.get('title', ''),
            'authors': authors,
            'description': description[:200] + '...' if len(description) > 200 else description,
            'poster_url': cover_url,
            'published_date': volume_info.get('publishedDate'),
            'publisher': volume_info.get('publisher'),
            'page_count': volume_info.get('pageCount'),
            'categories': volume_info.get('categories', []),
            'language': volume_info.get('language'),
            'isbn': self._extract_isbn(volume_info.get('industryIdentifiers', [])),
            'rating': volume_info.get('averageRating'),
            'ratings_count': volume_info.get('ratingsCount'),
            'preview_link': volume_info.get('previewLink'),
            'info_link': volume_info.get('infoLink'),
            'source': 'google_books',
            'type': 'book'
        }
    
    def _format_openlibrary_book_details(self, book_data: Dict) -> Dict:
        """Formate les détails complets d'un livre OpenLibrary"""
        # Cette méthode peut être étendue pour récupérer plus de détails
        # depuis l'API Works ou Authors d'OpenLibrary
        return {
            'external_id': book_data.get('key', ''),
            'title': book_data.get('title', ''),
            'description': self._get_openlibrary_description(book_data),
            'source': 'openlibrary',
            'type': 'book'
        }
    
    def _get_openlibrary_description(self, book_data: Dict) -> str:
        """Extrait une description d'un livre OpenLibrary"""
        # OpenLibrary peut avoir différents formats de description
        description = book_data.get('description', '')
        
        if isinstance(description, dict):
            return description.get('value', '')
        elif isinstance(description, list) and description:
            return description[0] if isinstance(description[0], str) else description[0].get('value', '')
        elif isinstance(description, str):
            return description
        
        return ''
    
    def _extract_isbn(self, identifiers: List[Dict]) -> List[str]:
        """Extrait les ISBN d'une liste d'identifiants"""
        isbns = []
        for identifier in identifiers:
            if identifier.get('type') in ['ISBN_10', 'ISBN_13']:
                isbns.append(identifier.get('identifier'))
        return isbns