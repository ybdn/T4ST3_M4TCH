from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


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


class VersusSession(models.Model):
    """Session de match versus pour un utilisateur"""
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Terminée'
        PAUSED = 'paused', 'En pause'
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='versus_sessions',
        verbose_name="Utilisateur"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Statut de la session"
    )
    current_round = models.PositiveIntegerField(
        default=1,
        verbose_name="Round actuel"
    )
    total_rounds = models.PositiveIntegerField(
        default=10,
        verbose_name="Total de rounds"
    )
    score = models.PositiveIntegerField(
        default=0,
        verbose_name="Score total"
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Début de session"
    )
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Fin de session"
    )
    last_activity = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière activité"
    )
    
    class Meta:
        verbose_name = "Session Versus"
        verbose_name_plural = "Sessions Versus"
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Session {self.id} - {self.user.username} ({self.get_status_display()})"
    
    @property
    def progress_percentage(self):
        """Pourcentage de progression de la session"""
        if self.total_rounds == 0:
            return 0
        return min(100, (self.current_round / self.total_rounds) * 100)
    
    @property
    def is_finished(self):
        """Vérifie si la session est terminée"""
        return self.status == self.Status.COMPLETED or self.current_round > self.total_rounds
    
    def complete_session(self):
        """Marque la session comme terminée"""
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save()


class VersusRound(models.Model):
    """Round individuel d'une session versus"""
    
    class Choice(models.TextChoices):
        LIKE = 'like', 'J\'aime'
        DISLIKE = 'dislike', 'Je n\'aime pas'
        SKIP = 'skip', 'Passer'
    
    session = models.ForeignKey(
        VersusSession,
        on_delete=models.CASCADE,
        related_name='rounds',
        verbose_name="Session"
    )
    round_number = models.PositiveIntegerField(
        verbose_name="Numéro du round"
    )
    item_title = models.CharField(
        max_length=200,
        verbose_name="Titre de l'élément"
    )
    item_description = models.TextField(
        blank=True,
        verbose_name="Description de l'élément"
    )
    item_category = models.CharField(
        max_length=50,
        verbose_name="Catégorie"
    )
    item_poster_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL du poster"
    )
    compatibility_score = models.PositiveIntegerField(
        default=0,
        verbose_name="Score de compatibilité"
    )
    user_choice = models.CharField(
        max_length=10,
        choices=Choice.choices,
        blank=True,
        null=True,
        verbose_name="Choix de l'utilisateur"
    )
    answered_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Répondu le"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le"
    )
    
    class Meta:
        verbose_name = "Round Versus"
        verbose_name_plural = "Rounds Versus"
        ordering = ['session', 'round_number']
        constraints = [
            models.UniqueConstraint(
                fields=['session', 'round_number'],
                name='unique_round_per_session'
            )
        ]
    
    def __str__(self):
        return f"Round {self.round_number} - {self.item_title}"
    
    @property
    def is_answered(self):
        """Vérifie si le round a été répondu"""
        return self.user_choice is not None
    
    def submit_choice(self, choice):
        """Enregistre le choix de l'utilisateur"""
        self.user_choice = choice
        self.answered_at = timezone.now()
        self.save()
        
        # Incrémenter le round de la session
        if not self.session.is_finished:
            self.session.current_round += 1
            if self.session.current_round > self.session.total_rounds:
                self.session.complete_session()
            else:
                self.session.save()
