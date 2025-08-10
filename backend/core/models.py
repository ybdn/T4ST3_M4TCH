from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import secrets
import string


class List(models.Model):
    class Category(models.TextChoices):
        FILMS = 'FILMS', 'Films'
        SERIES = 'SERIES', 'Séries'
        MUSIQUE = 'MUSIQUE', 'Musique'
        LIVRES = 'LIVRES', 'Livres'

    name = models.CharField(max_length=100, verbose_name="Nom de la liste")
    description = models.TextField(blank=True, verbose_name="Description")
    category = models.CharField(
        max_length=20, 
        choices=Category.choices,
        default=Category.FILMS,
        verbose_name="Catégorie"
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taste_lists', verbose_name="Propriétaire")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    
    class Meta:
        verbose_name = "Liste de goûts"
        verbose_name_plural = "Listes de goûts"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'category'], 
                name='unique_list_per_category_per_user'
            ),
        ]
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.owner.username}"
    
    @classmethod
    def get_default_name(cls, category):
        """Retourne le nom par défaut pour une catégorie donnée"""
        defaults = {
            cls.Category.FILMS: "Mes Films",
            cls.Category.SERIES: "Mes Séries", 
            cls.Category.MUSIQUE: "Ma Musique",
            cls.Category.LIVRES: "Mes Livres"
        }
        return defaults.get(category, f"Ma liste {category}")
    
    @classmethod 
    def get_default_description(cls, category):
        """Retourne la description par défaut pour une catégorie donnée"""
        defaults = {
            cls.Category.FILMS: "Mes films et documentaires préférés",
            cls.Category.SERIES: "Mes séries et documentaires préférés",
            cls.Category.MUSIQUE: "Mes artistes, albums et chansons préférés", 
            cls.Category.LIVRES: "Mes livres, BD et mangas préférés"
        }
        return defaults.get(category, f"Ma collection {category}")


class ListItem(models.Model):
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description/Commentaire")
    position = models.PositiveIntegerField(default=0, verbose_name="Position dans la liste")
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='items', verbose_name="Liste")
    is_watched = models.BooleanField(default=False, verbose_name="Vu/Lu")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    
    class Meta:
        verbose_name = "Élément de liste"
        verbose_name_plural = "Éléments de liste" 
        ordering = ['list', 'position']
        constraints = [
            models.UniqueConstraint(
                fields=['list', 'position'], 
                name='unique_position_per_list'
            ),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.list.get_category_display()})"


class ExternalReference(models.Model):
    """Référence vers une API externe pour enrichir un élément"""
    
    class Source(models.TextChoices):
        TMDB = 'tmdb', 'The Movie Database'
        SPOTIFY = 'spotify', 'Spotify'
        OPENLIBRARY = 'openlibrary', 'Open Library'
        GOOGLE_BOOKS = 'google_books', 'Google Books'
    
    list_item = models.OneToOneField(
        ListItem, 
        on_delete=models.CASCADE, 
        related_name='external_ref',
        verbose_name="Élément de liste"
    )
    external_id = models.CharField(
        max_length=100, 
        verbose_name="ID externe"
    )
    external_source = models.CharField(
        max_length=20, 
        choices=Source.choices,
        verbose_name="Source API"
    )
    poster_url = models.URLField(
        blank=True, 
        null=True,
        verbose_name="URL du poster/pochette"
    )
    backdrop_url = models.URLField(
        blank=True, 
        null=True,
        verbose_name="URL de l'image de fond"
    )
    metadata = models.JSONField(
        default=dict, 
        blank=True,
        verbose_name="Métadonnées enrichies"
    )
    rating = models.FloatField(
        blank=True, 
        null=True,
        verbose_name="Note (TMDB, etc.)"
    )
    release_date = models.DateField(
        blank=True, 
        null=True,
        verbose_name="Date de sortie/publication"
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière mise à jour"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    class Meta:
        verbose_name = "Référence externe"
        verbose_name_plural = "Références externes"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['external_id', 'external_source'], 
                name='unique_external_reference'
            ),
        ]
    
    def __str__(self):
        return f"{self.list_item.title} → {self.get_external_source_display()} ({self.external_id})"

    def needs_refresh(self, days=7):
        """Vérifie si les données doivent être actualisées"""
        return self.last_updated < timezone.now() - timedelta(days=days)


class APICache(models.Model):
    """Cache pour les réponses d'APIs externes"""
    
    cache_key = models.CharField(
        max_length=255, 
        unique=True,
        verbose_name="Clé de cache"
    )
    data = models.JSONField(
        verbose_name="Données cachées"
    )
    expires_at = models.DateTimeField(
        verbose_name="Date d'expiration"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    class Meta:
        verbose_name = "Cache API"
        verbose_name_plural = "Cache API"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['cache_key']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Cache: {self.cache_key}"
    
    @classmethod
    def is_expired(cls, cache_key):
        """Vérifie si une entrée de cache est expirée"""
        try:
            cache_obj = cls.objects.get(cache_key=cache_key)
            return timezone.now() > cache_obj.expires_at
        except cls.DoesNotExist:
            return True
    
    @classmethod
    def get_cached_data(cls, cache_key):
        """Récupère les données du cache si valides"""
        try:
            cache_obj = cls.objects.get(cache_key=cache_key)
            if timezone.now() <= cache_obj.expires_at:
                return cache_obj.data
            else:
                # Nettoyer l'entrée expirée
                cache_obj.delete()
                return None
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def set_cached_data(cls, cache_key, data, ttl_hours=24):
        """Sauvegarde les données dans le cache"""
        expires_at = timezone.now() + timedelta(hours=ttl_hours)
        cls.objects.update_or_create(
            cache_key=cache_key,
            defaults={
                'data': data,
                'expires_at': expires_at
            }
        )
    
    @classmethod
    def clean_expired(cls):
        """Nettoie les entrées de cache expirées"""
        return cls.objects.filter(expires_at__lt=timezone.now()).delete()


class BetaInvite(models.Model):
    """Modèle pour gérer les invitations bêta avec contrôle d'accès"""
    
    email = models.EmailField(
        verbose_name="Email de l'invité",
        help_text="Email de la personne invitée"
    )
    token = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="Token d'invitation",
        help_text="Token unique pour valider l'invitation"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    expires_at = models.DateTimeField(
        verbose_name="Date d'expiration",
        help_text="Date à laquelle le token expire"
    )
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date d'utilisation",
        help_text="Date à laquelle l'invitation a été utilisée"
    )
    used_by = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='beta_invitation',
        verbose_name="Utilisateur créé",
        help_text="Utilisateur qui a utilisé cette invitation"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sent_invitations',
        verbose_name="Créé par",
        help_text="Administrateur qui a créé cette invitation"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notes",
        help_text="Notes administratives sur cette invitation"
    )
    
    class Meta:
        verbose_name = "Invitation bêta"
        verbose_name_plural = "Invitations bêta"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['email']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        status = "Utilisée" if self.is_used else ("Expirée" if self.is_expired else "Active")
        return f"{self.email} - {status}"
    
    @property
    def is_expired(self):
        """Vérifie si l'invitation est expirée"""
        return timezone.now() > self.expires_at
    
    @property
    def is_used(self):
        """Vérifie si l'invitation a été utilisée"""
        return self.used_at is not None
    
    @property
    def is_valid(self):
        """Vérifie si l'invitation est valide (non expirée et non utilisée)"""
        return not self.is_expired and not self.is_used
    
    def save(self, *args, **kwargs):
        """Génère automatiquement un token et une date d'expiration si nécessaire"""
        if not self.token:
            self.token = self._generate_unique_token()
        
        if not self.expires_at:
            # Par défaut, le token expire dans 7 jours
            self.expires_at = timezone.now() + timedelta(days=7)
        
        super().save(*args, **kwargs)
    
    def _generate_unique_token(self):
        """Génère un token unique"""
        while True:
            # Génère un token de 32 caractères (lettres et chiffres)
            token = ''.join(secrets.choice(string.ascii_letters + string.digits) 
                          for _ in range(32))
            if not BetaInvite.objects.filter(token=token).exists():
                return token
    
    def mark_as_used(self, user):
        """Marque l'invitation comme utilisée par un utilisateur"""
        if self.is_used:
            raise ValueError("Cette invitation a déjà été utilisée")
        
        if self.is_expired:
            raise ValueError("Cette invitation a expiré")
        
        self.used_at = timezone.now()
        self.used_by = user
        self.save()
    
    @classmethod
    def create_invitation(cls, email, created_by=None, expires_in_days=7, notes=""):
        """Méthode utilitaire pour créer une nouvelle invitation"""
        expires_at = timezone.now() + timedelta(days=expires_in_days)
        return cls.objects.create(
            email=email,
            expires_at=expires_at,
            created_by=created_by,
            notes=notes
        )
    
    @classmethod
    def validate_token(cls, token):
        """Valide un token et retourne l'invitation si valide"""
        try:
            invitation = cls.objects.get(token=token)
            if invitation.is_valid:
                return invitation
            return None
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def clean_expired_invitations(cls):
        """Nettoie les invitations expirées (garde un historique des utilisées)"""
        expired_unused = cls.objects.filter(
            expires_at__lt=timezone.now(),
            used_at__isnull=True
        )
        count = expired_unused.count()
        expired_unused.delete()
        return count
