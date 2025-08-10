# Cache API Externe - Documentation

## Vue d'ensemble

Le système de cache des APIs externes a été optimisé pour réduire la latence et améliorer les performances. Il fournit un cache TTL configurable avec suivi des métriques hits/miss.

## Fonctionnalités

### 1. Wrapper centralisé get_external
- Service `CachedExternalAPIService` pour toutes les requêtes HTTP externes
- Cache automatique avec clés basées sur l'URL, paramètres et headers
- Gestion d'erreur robuste avec fallbacks

### 2. TTL configurable par environnement
Variables d'environnement pour configurer les TTL (en heures):
```bash
CACHE_TTL_TMDB_HOURS=6        # Cache TMDB (défaut: 6h)
CACHE_TTL_SPOTIFY_HOURS=2     # Cache Spotify (défaut: 2h) 
CACHE_TTL_BOOKS_HOURS=12      # Cache Google Books (défaut: 12h)
CACHE_TTL_DEFAULT_HOURS=4     # TTL par défaut (défaut: 4h)
```

### 3. Métriques hits/miss
- Suivi global des hits/miss de cache
- Calcul automatique du taux de réussite
- Objectif: >40% hit rate après warming

## Utilisation

### Services existants
Les services TMDB, Spotify et Books utilisent automatiquement le nouveau cache:
```python
from core.services.tmdb_service import TMDBService
from core.services.spotify_service import SpotifyService
from core.services.books_service import BooksService

# Les services utilisent automatiquement le cache optimisé
tmdb = TMDBService()
results = tmdb.search_movies("Inception")  # Utilise le cache
```

### Service de cache direct
```python
from core.services.cached_external_api_service import CachedExternalAPIService

# Créer un service de cache
cache_service = CachedExternalAPIService('mon_service')

# Faire une requête avec cache
data = cache_service.get_external(
    url="https://api.example.com/data",
    params={"query": "test"},
    headers={"Authorization": "Bearer token"},
    ttl_hours=6  # TTL optionnel spécifique
)
```

### Métriques
```python
from core.services.cached_external_api_service import CachedExternalAPIService

# Obtenir les métriques globales
metrics = CachedExternalAPIService.get_global_metrics()
print(f"Hit rate: {metrics['hit_rate']}%")
print(f"Total requests: {metrics['total_requests']}")

# Remettre à zéro les métriques
CachedExternalAPIService.reset_global_metrics()
```

## Commandes de management

### Voir les métriques
```bash
python manage.py cache_metrics
```

### Nettoyer le cache expiré
```bash
python manage.py cache_metrics --clean-expired
```

### Remettre à zéro les métriques
```bash
python manage.py cache_metrics --reset
```

### Test de warming du cache
```bash
python manage.py test_cache_warming --iterations=50
```

### Démonstration avec données mockées
```bash
python manage.py demo_cache
```

## Tests

### Lancer les tests de cache
```bash
python manage.py test core.tests.CachedExternalAPIServiceTests
python manage.py test core.tests.IntegrationCacheTests
python manage.py test core.tests.CacheMetricsTests
```

### Validation du hit rate
Les tests valident automatiquement que le hit rate atteint >40% après warming.

## Architecture

### Avant (sans optimisation)
```
Service → requests.get() → API externe
         ↓
         Cache individuel (code dupliqué)
```

### Après (avec optimisation)
```
Service → CachedExternalAPIService → Cache centralisé → API externe
                                  ↓
                              Métriques globales
```

## Bénéfices

1. **Latence réduite**: Cache TTL intelligent
2. **Code unifié**: Wrapper centralisé sans duplication
3. **Configuration flexible**: TTL par environnement
4. **Monitoring**: Métriques hits/miss en temps réel
5. **Objectif atteint**: >40% hit rate validé par les tests

## Migration

L'implémentation est **rétrocompatible**. Les services existants continuent de fonctionner sans modification du code utilisateur.