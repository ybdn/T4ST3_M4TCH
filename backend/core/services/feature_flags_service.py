"""
Service pour la gestion des feature flags avec cache local
"""
import logging
import hashlib
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from ..models import FeatureFlag

logger = logging.getLogger(__name__)


class FeatureFlagsService:
    """Service de gestion des feature flags avec cache local O(1)"""
    
    CACHE_PREFIX = "feature_flag:"
    ALL_FLAGS_CACHE_KEY = "feature_flags:all"

    @classmethod
    def get_cache_timeout(cls):
        """
        Returns the cache timeout for feature flags, configurable via Django settings.
        """
        return getattr(settings, "FEATURE_FLAGS_CACHE_TIMEOUT", 300)
    
    @classmethod
    def is_enabled(cls, flag_name, user_id=None):
        """
        Vérifie si un feature flag est activé (lecture O(1) avec cache)
        
        Args:
            flag_name (str): Nom du feature flag
            user_id (int, optional): ID utilisateur pour rollout progressif
            
        Returns:
            bool: True si le flag est activé pour cet utilisateur
        """
        # Récupérer depuis le cache d'abord
        cache_key = f"{cls.CACHE_PREFIX}{flag_name}"
        flag_data = cache.get(cache_key)
        
        if flag_data is None:
            # Cache miss - récupérer depuis la DB
            try:
                flag = FeatureFlag.objects.get(name=flag_name)
                flag_data = {
                    'enabled': flag.enabled,
                    'rollout_percentage': flag.rollout_percentage
                }
                # Mettre en cache
                cache.set(cache_key, flag_data, cls.CACHE_TIMEOUT)
            except FeatureFlag.DoesNotExist:
                # Flag inexistant - cacher le résultat négatif
                flag_data = {'enabled': False, 'rollout_percentage': 0}
                cache.set(cache_key, flag_data, cls.CACHE_TIMEOUT)
        
        # Évaluer le flag
        if not flag_data['enabled']:
            return False
        
        # Si rollout à 100% ou pas d'utilisateur spécifique, retourne enabled
        if flag_data['rollout_percentage'] >= 100 or user_id is None:
            return True
        
        # Utilise un hash déterministe pour le rollout progressif
        hash_input = f"{user_id}:{flag_name}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
        user_percentage = hash_value % 100
        
        return user_percentage < flag_data['rollout_percentage']
    
    @classmethod
    def get_all_flags(cls):
        """
        Récupère tous les feature flags actifs (pour l'endpoint config)
        
        Returns:
            dict: Dictionnaire des flags {name: enabled_status}
        """
        cached_flags = cache.get(cls.ALL_FLAGS_CACHE_KEY)
        
        if cached_flags is None:
            # Récupérer tous les flags depuis la DB
            flags = FeatureFlag.objects.all()
            cached_flags = {}
            
            for flag in flags:
                # Pour l'endpoint config, on retourne le status global (pas le rollout)
                cached_flags[flag.name] = flag.enabled
            
            # Cacher le résultat
            cache.set(cls.ALL_FLAGS_CACHE_KEY, cached_flags, cls.CACHE_TIMEOUT)
            
            logger.info(f"Feature flags loaded from DB: {len(cached_flags)} flags")
        
        return cached_flags
    
    @classmethod
    def invalidate_cache(cls, flag_name=None):
        """
        Invalide le cache des feature flags
        
        Args:
            flag_name (str, optional): Nom du flag spécifique à invalider.
                                     Si None, invalide tout le cache.
        """
        if flag_name:
            # Invalider un flag spécifique
            cache_key = f"{cls.CACHE_PREFIX}{flag_name}"
            cache.delete(cache_key)
            logger.info(f"Cache invalidated for flag: {flag_name}")
        else:
            # Invalider tout le cache des flags
            # Note: Django cache n'a pas de pattern delete, donc on invalide par valeurs connues
            # Plus efficace que de faire une requête DB pour tous les flags
            # Récupérer tous les noms de flags directement depuis la DB pour éviter la récursion
            flag_names = FeatureFlag.objects.values_list('name', flat=True)
            for flag_name in flag_names:
                cache_key = f"{cls.CACHE_PREFIX}{flag_name}"
                cache.delete(cache_key)
                logger.info(f"Cache invalidated for flag: {flag_name}")
        
        # Invalider le cache des flags globaux dans tous les cas
        cache.delete(cls.ALL_FLAGS_CACHE_KEY)
        logger.info("All flags cache invalidated")
    
    @classmethod
    def get_flag_stats(cls):
        """
        Récupère des statistiques sur les feature flags (pour monitoring)
        
        Returns:
            dict: Statistiques des flags
        """
        all_flags = FeatureFlag.objects.all()
        
        stats = {
            'total_flags': all_flags.count(),
            'enabled_flags': all_flags.filter(enabled=True).count(),
            'rollout_flags': all_flags.filter(enabled=True, rollout_percentage__lt=100).count(),
        }
        
        return stats


# ========================================
# SIGNAUX POUR INVALIDATION AUTOMATIQUE
# ========================================

@receiver(post_save, sender=FeatureFlag)
def invalidate_flag_cache_on_save(sender, instance, created, **kwargs):
    """Invalide le cache quand un flag est créé ou modifié"""
    FeatureFlagsService.invalidate_cache(instance.name)
    
    if created:
        logger.info(f"Feature flag created: {instance.name} (enabled: {instance.enabled})")
    else:
        logger.info(f"Feature flag updated: {instance.name} (enabled: {instance.enabled})")


@receiver(post_delete, sender=FeatureFlag)
def invalidate_flag_cache_on_delete(sender, instance, **kwargs):
    """Invalide le cache quand un flag est supprimé"""
    FeatureFlagsService.invalidate_cache(instance.name)
    logger.info(f"Feature flag deleted: {instance.name}")


# ========================================
# RACCOURCIS POUR L'USAGE COURANT
# ========================================

def is_enabled(flag_name, user_id=None):
    """Raccourci pour vérifier un feature flag"""
    return FeatureFlagsService.is_enabled(flag_name, user_id)


def get_all_flags():
    """Raccourci pour récupérer tous les flags"""
    return FeatureFlagsService.get_all_flags()