from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        # Importer les signaux pour les feature flags
        from . import signals
        # Les signaux sont dans le service mais doivent être importés
        from .services import feature_flags_service
