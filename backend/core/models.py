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


class VersusMatch(models.Model):
    """Modèle pour une session de versus entre utilisateurs"""
    
    class Status(models.TextChoices):
        WAITING = 'WAITING', 'En attente'
        ACTIVE = 'ACTIVE', 'En cours'
        COMPLETED = 'COMPLETED', 'Terminé'
        CANCELLED = 'CANCELLED', 'Annulé'
    
    category = models.CharField(
        max_length=20,
        choices=List.Category.choices,
        verbose_name="Catégorie"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.WAITING,
        verbose_name="Statut"
    )
    current_round = models.PositiveIntegerField(
        default=1,
        verbose_name="Round actuel"
    )
    max_rounds = models.PositiveIntegerField(
        default=10,
        verbose_name="Nombre maximum de rounds"
    )
    completed = models.BooleanField(
        default=False,
        verbose_name="Terminé"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_matches',
        verbose_name="Créé par"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de fin"
    )
    
    class Meta:
        verbose_name = "Match Versus"
        verbose_name_plural = "Matchs Versus"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Match {self.get_category_display()} - {self.get_status_display()}"
    
    def get_participants(self):
        """Retourne les participants au match"""
        return User.objects.filter(versus_participations__match=self)
    
    def is_participant(self, user):
        """Vérifie si un utilisateur est participant au match"""
        return self.participants.filter(user=user).exists()
    
    def can_start(self):
        """Vérifie si le match peut commencer"""
        return (self.status == self.Status.WAITING and 
                self.participants.count() >= 2)
    
    def mark_completed(self):
        """Marque le match comme terminé"""
        self.status = self.Status.COMPLETED
        self.completed = True
        self.completed_at = timezone.now()
        self.save()


class VersusParticipant(models.Model):
    """Modèle pour les participants d'un match versus"""
    
    match = models.ForeignKey(
        VersusMatch,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name="Match"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='versus_participations',
        verbose_name="Utilisateur"
    )
    score = models.PositiveIntegerField(
        default=0,
        verbose_name="Score"
    )
    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de participation"
    )
    
    class Meta:
        verbose_name = "Participant Versus"
        verbose_name_plural = "Participants Versus"
        unique_together = ['match', 'user']
        ordering = ['-score', 'joined_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.match} (Score: {self.score})"


class VersusRound(models.Model):
    """Modèle pour un round d'un match versus"""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'En attente'
        ACTIVE = 'ACTIVE', 'En cours'
        COMPLETED = 'COMPLETED', 'Terminé'
    
    match = models.ForeignKey(
        VersusMatch,
        on_delete=models.CASCADE,
        related_name='rounds',
        verbose_name="Match"
    )
    round_number = models.PositiveIntegerField(
        verbose_name="Numéro du round"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Statut"
    )
    item1 = models.ForeignKey(
        ListItem,
        on_delete=models.CASCADE,
        related_name='rounds_as_item1',
        verbose_name="Élément 1"
    )
    item2 = models.ForeignKey(
        ListItem,
        on_delete=models.CASCADE,
        related_name='rounds_as_item2',
        verbose_name="Élément 2"
    )
    winner_item = models.ForeignKey(
        ListItem,
        on_delete=models.CASCADE,
        related_name='won_rounds',
        null=True,
        blank=True,
        verbose_name="Élément gagnant"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de fin"
    )
    
    class Meta:
        verbose_name = "Round Versus"
        verbose_name_plural = "Rounds Versus"
        unique_together = ['match', 'round_number']
        ordering = ['match', 'round_number']
    
    def __str__(self):
        return f"Round {self.round_number} - {self.match}"
    
    def mark_completed(self, winner_item):
        """Marque le round comme terminé avec un gagnant"""
        self.winner_item = winner_item
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save()


class VersusVote(models.Model):
    """Modèle pour les votes dans un round versus"""
    
    round = models.ForeignKey(
        VersusRound,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name="Round"
    )
    participant = models.ForeignKey(
        VersusParticipant,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name="Participant"
    )
    chosen_item = models.ForeignKey(
        ListItem,
        on_delete=models.CASCADE,
        related_name='received_votes',
        verbose_name="Élément choisi"
    )
    voted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date du vote"
    )
    
    class Meta:
        verbose_name = "Vote Versus"
        verbose_name_plural = "Votes Versus"
        unique_together = ['round', 'participant']
        ordering = ['voted_at']
    
    def __str__(self):
        return f"Vote de {self.participant.user.username} pour {self.chosen_item.title}"
