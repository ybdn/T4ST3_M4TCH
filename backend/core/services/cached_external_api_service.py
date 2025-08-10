"""
Service de cache centralisé pour les APIs externes
Fournit un wrapper unifié avec TTL configurable et métriques hits/miss
"""

import requests
import hashlib
import logging
from typing import Dict, Optional, Any
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from ..models import APICache

logger = logging.getLogger(__name__)


class CacheMetrics:
    """Classe pour suivre les métriques de cache"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.total_requests = 0
    
    def record_hit(self):
        """Enregistre un cache hit"""
        self.hits += 1
        self.total_requests += 1
    
    def record_miss(self):
        """Enregistre un cache miss"""
        self.misses += 1
        self.total_requests += 1
    
    def get_hit_rate(self) -> float:
        """Calcule le taux de cache hit"""
        if self.total_requests == 0:
            return 0.0
        return (self.hits / self.total_requests) * 100
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de cache"""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'total_requests': self.total_requests,
            'hit_rate': round(self.get_hit_rate(), 2)
        }
    
    def reset(self):
        """Remet à zéro les métriques"""
        self.hits = 0
        self.misses = 0
        self.total_requests = 0


class CachedExternalAPIService:
    """Service de cache centralisé pour toutes les APIs externes"""
    
    # Instance globale pour partager les métriques
    _metrics = CacheMetrics()
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        # Configuration TTL depuis l'environnement avec fallbacks
        self.default_ttl_hours = self._get_ttl_config()
    
    def _get_ttl_config(self) -> Dict[str, int]:
        """Récupère la configuration TTL depuis l'environnement"""
        return {
            'tmdb': int(getattr(settings, 'CACHE_TTL_TMDB_HOURS', 
                              settings.__dict__.get('CACHE_TTL_TMDB_HOURS', 6))),
            'spotify': int(getattr(settings, 'CACHE_TTL_SPOTIFY_HOURS', 
                                 settings.__dict__.get('CACHE_TTL_SPOTIFY_HOURS', 2))),
            'books': int(getattr(settings, 'CACHE_TTL_BOOKS_HOURS', 
                               settings.__dict__.get('CACHE_TTL_BOOKS_HOURS', 12))),
            'default': int(getattr(settings, 'CACHE_TTL_DEFAULT_HOURS', 
                                 settings.__dict__.get('CACHE_TTL_DEFAULT_HOURS', 4)))
        }
    
    def get_external(self, url: str, params: Optional[Dict] = None, 
                    headers: Optional[Dict] = None, timeout: int = 10,
                    ttl_hours: Optional[int] = None) -> Optional[Dict]:
        """
        Wrapper principal pour les requêtes externes avec cache
        
        Args:
            url: URL de l'API externe
            params: Paramètres de la requête
            headers: Headers HTTP 
            timeout: Timeout de la requête
            ttl_hours: TTL spécifique (optionnel)
        
        Returns:
            Données JSON ou None en cas d'erreur
        """
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        
        # Générer la clé de cache
        cache_key = self._generate_cache_key(url, params, headers)
        
        # Vérifier le cache d'abord
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            self._metrics.record_hit()
            logger.debug(f"Cache HIT for {self.service_name}: {cache_key[:16]}...")
            return cached_data
        
        # Cache miss - faire la requête externe
        self._metrics.record_miss()
        logger.debug(f"Cache MISS for {self.service_name}: {cache_key[:16]}...")
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Mettre en cache avec TTL approprié
            if ttl_hours is None:
                ttl_hours = self.default_ttl_hours.get(self.service_name, 
                                                     self.default_ttl_hours['default'])
            
            self._set_cache(cache_key, data, ttl_hours)
            
            logger.info(f"External API success for {self.service_name}: {url}")
            return data
            
        except requests.RequestException as e:
            logger.error(f"External API error for {self.service_name} [{url}]: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in {self.service_name} external call: {e}")
            return None
    
    def _generate_cache_key(self, url: str, params: Dict, headers: Dict) -> str:
        """Génère une clé de cache unique basée sur l'URL, params et headers pertinents"""
        # Exclure les headers sensibles de la clé de cache
        cache_headers = {k: v for k, v in headers.items() 
                        if k.lower() not in ['authorization', 'x-api-key']}
        
        # Créer une chaîne unique pour le cache
        cache_string = f"{self.service_name}_{url}_{str(sorted(params.items()))}_{str(sorted(cache_headers.items()))}"
        
        # Utiliser MD5 pour générer une clé compacte
        return f"{self.service_name}_{hashlib.md5(cache_string.encode()).hexdigest()}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Récupère les données du cache"""
        return APICache.get_cached_data(cache_key)
    
    def _set_cache(self, cache_key: str, data: Dict, ttl_hours: int):
        """Sauvegarde les données dans le cache"""
        APICache.set_cached_data(cache_key, data, ttl_hours)
    
    @classmethod
    def get_global_metrics(cls) -> Dict[str, Any]:
        """Retourne les métriques globales de cache"""
        return cls._metrics.get_stats()
    
    @classmethod
    def reset_global_metrics(cls):
        """Remet à zéro les métriques globales"""
        cls._metrics.reset()
    
    def invalidate_cache_pattern(self, pattern: str):
        """Invalide le cache pour un pattern donné"""
        # Cette méthode pourrait être étendue pour invalider des patterns spécifiques
        logger.info(f"Cache invalidation requested for pattern: {pattern}")
        # Pour l'instant, on peut nettoyer les caches expirés
        APICache.clean_expired()