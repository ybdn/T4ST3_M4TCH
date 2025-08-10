"""
Service pour l'intégration avec Google Books API
Utilise exclusivement Google Books pour les recherches et données de livres
"""

import requests
from typing import Dict, List, Optional, Any
from django.conf import settings
from ..models import APICache
from .cached_external_api_service import CachedExternalAPIService
import hashlib
import logging

logger = logging.getLogger(__name__)


class BooksService:
    """Service pour Google Books API"""
    
    GOOGLE_BOOKS_BASE_URL = "https://www.googleapis.com/books/v1"
    
    def __init__(self):
        self.google_api_key = getattr(settings, 'GOOGLE_BOOKS_API_KEY', None)
        if not self.google_api_key:
            logger.warning("GOOGLE_BOOKS_API_KEY not configured, using basic access")
        
        # Utiliser le nouveau service de cache centralisé
        self.cache_service = CachedExternalAPIService('books')
    
    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Effectue une requête avec gestion d'erreur et cache"""
        if params is None:
            params = {}
        
        # Utiliser le service de cache centralisé
        return self.cache_service.get_external(url, params)
    
    def search_books(self, query: str, limit: int = 10) -> List[Dict]:
        """Recherche de livres via Google Books API"""
        return self._search_google_books(query, limit)
    
    def get_popular_books(self, limit: int = 20) -> List[Dict]:
        """Récupère des livres populaires via Google Books API"""
        popular_queries = [
            'Le Seigneur des Anneaux Tolkien',
            '1984 George Orwell',
            'Harry Potter école sorciers Rowling',
            'Le Petit Prince Saint-Exupéry',
            'L\'Étranger Albert Camus',
            'Dune Frank Herbert',
            'Les Misérables Victor Hugo',
            'Germinal Émile Zola',
            'Pride and Prejudice Jane Austen',
            'To Kill a Mockingbird Harper Lee'
        ]
        
        results = []
        
        # Rechercher chaque livre populaire dans Google Books
        for query in popular_queries:
            try:
                gb_results = self._search_google_books(query, 1)
                if gb_results:
                    results.extend(gb_results)
                    
                # Arrêter si on a assez de résultats
                if len(results) >= limit:
                    break
                    
            except Exception as e:
                logger.error(f"Erreur lors de la recherche du livre populaire '{query}': {e}")
                continue
        
        return results[:limit]
    
    def get_books_by_author(self, author: str, limit: int = 10) -> List[Dict]:
        """Récupère les livres d'un auteur via Google Books"""
        query = f"inauthor:{author}"
        return self._search_google_books(query, limit)
    
    def get_books_by_genre(self, genre: str, limit: int = 10) -> List[Dict]:
        """Récupère les livres d'un genre via Google Books"""
        query = f"subject:{genre}"
        return self._search_google_books(query, limit)
    
    def get_book_details_by_isbn(self, isbn: str) -> Optional[Dict]:
        """Récupère les détails d'un livre via ISBN avec Google Books"""
        return self._get_google_book_by_isbn(isbn)
    
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
        
        data = self._make_request(url, params)
        if not data:
            return []
        
        results = []
        for book in data.get('items', []):
            formatted = self._format_google_book(book)
            if formatted:
                results.append(formatted)
        
        return results
    
    def _get_high_quality_cover_url(self, image_links: Dict) -> Optional[str]:
        """Récupère la meilleure URL de couverture disponible, sans la modifier."""
        if not image_links:
            return None
        
        # Ordre de préférence des formats d'image
        priority_order = ['extraLarge', 'large', 'medium', 'small', 'thumbnail', 'smallThumbnail']
        
        for format_type in priority_order:
            if format_type in image_links:
                cover_url = image_links[format_type]
                # S'assurer que l'URL est en HTTPS
                if cover_url.startswith('http://'):
                    return cover_url.replace('http://', 'https://')
                return cover_url
        
        return None
    
    def _get_google_book_by_isbn(self, isbn: str) -> Optional[Dict]:
        """Récupère un livre de Google Books par ISBN"""
        url = f"{self.GOOGLE_BOOKS_BASE_URL}/volumes"
        params = {
            'q': f'isbn:{isbn}'
        }
        
        if self.google_api_key:
            params['key'] = self.google_api_key
        
        data = self._make_request(url, params)
        
        if data and data.get('items'):
            return self._format_google_book(data['items'][0])
        return None
    
    def _format_google_book(self, book_data: Dict) -> Optional[Dict]:
        """Formate les données de Google Books"""
        volume_info = book_data.get('volumeInfo', {})
        
        if not volume_info.get('title'):
            return None
        
        # Récupérer la meilleure image de couverture avec zoom optimal
        images = volume_info.get('imageLinks', {})
        cover_url = self._get_high_quality_cover_url(images)
        
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
    
    
    def _extract_isbn(self, identifiers: List[Dict]) -> List[str]:
        """Extrait les ISBN d'une liste d'identifiants"""
        isbns = []
        for identifier in identifiers:
            if identifier.get('type') in ['ISBN_10', 'ISBN_13']:
                isbns.append(identifier.get('identifier'))
        return isbns
    
    def get_book_details(self, book_id: str) -> Optional[Dict]:
        """Récupère les détails d'un livre par son ID Google Books"""
        url = f"{self.GOOGLE_BOOKS_BASE_URL}/volumes/{book_id}"
        params = {}
        
        if self.google_api_key:
            params['key'] = self.google_api_key
        
        data = self._make_request(url, params)
        
        if data:
            return data  # Retourner les données brutes de Google Books API
        return None