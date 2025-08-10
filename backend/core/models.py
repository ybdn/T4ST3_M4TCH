from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random


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
    """Match entre deux utilisateurs pour comparer leurs goûts"""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        ACTIVE = 'active', 'En cours'
        COMPLETED = 'completed', 'Terminé'
        CANCELLED = 'cancelled', 'Annulé'
    
    player1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='matches_as_player1',
        verbose_name="Joueur 1"
    )
    player2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='matches_as_player2',
        verbose_name="Joueur 2"
    )
    category = models.CharField(
        max_length=20,
        choices=List.Category.choices,
        verbose_name="Catégorie"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Statut"
    )
    current_round = models.PositiveIntegerField(
        default=1,
        verbose_name="Round actuel"
    )
    total_rounds = models.PositiveIntegerField(
        default=10,
        verbose_name="Nombre total de rounds"
    )
    player1_score = models.PositiveIntegerField(
        default=0,
        verbose_name="Score joueur 1"
    )
    player2_score = models.PositiveIntegerField(
        default=0,
        verbose_name="Score joueur 2"
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
        return f"{self.player1.username} vs {self.player2.username} ({self.get_category_display()})"
    
    def get_players(self):
        """Retourne les deux joueurs"""
        return [self.player1, self.player2]
    
    def get_current_round_obj(self):
        """Retourne l'objet du round actuel"""
        return self.rounds.filter(round_number=self.current_round).first()
    
    def is_player(self, user):
        """Vérifie si l'utilisateur participe à ce match"""
        return user in [self.player1, self.player2]
    
    def advance_to_next_round(self):
        """Passe au round suivant ou termine le match"""
        if self.current_round < self.total_rounds:
            self.current_round += 1
            self.save()
        else:
            self.status = self.Status.COMPLETED
            self.completed_at = timezone.now()
            self.save()
    
    def get_winner(self):
        """Retourne le gagnant du match"""
        if self.status != self.Status.COMPLETED:
            return None
        if self.player1_score > self.player2_score:
            return self.player1
        elif self.player2_score > self.player1_score:
            return self.player2
        return None  # Égalité


class VersusRound(models.Model):
    """Round individuel dans un match versus"""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        ACTIVE = 'active', 'En cours'
        COMPLETED = 'completed', 'Terminé'
    
    match = models.ForeignKey(
        VersusMatch,
        on_delete=models.CASCADE,
        related_name='rounds',
        verbose_name="Match"
    )
    round_number = models.PositiveIntegerField(
        verbose_name="Numéro du round"
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
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Statut"
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
        ordering = ['match', 'round_number']
        constraints = [
            models.UniqueConstraint(
                fields=['match', 'round_number'],
                name='unique_round_per_match'
            ),
        ]
    
    def __str__(self):
        return f"Round {self.round_number} - {self.item1.title} vs {self.item2.title}"
    
    def get_items(self):
        """Retourne les deux éléments du round"""
        return [self.item1, self.item2]
    
    def has_player_chosen(self, user):
        """Vérifie si un joueur a déjà fait son choix"""
        return self.choices.filter(player=user).exists()
    
    def get_player_choice(self, user):
        """Retourne le choix d'un joueur"""
        return self.choices.filter(player=user).first()
    
    def is_complete(self):
        """Vérifie si les deux joueurs ont fait leur choix"""
        return self.choices.count() == 2
    
    def complete_round(self):
        """Marque le round comme terminé et calcule les scores"""
        if not self.is_complete():
            return False
        
        choices = list(self.choices.all())
        choice1, choice2 = choices[0], choices[1]
        
        # Détection like/like (même élément choisi)
        if choice1.chosen_item == choice2.chosen_item:
            # Point pour chaque joueur si ils ont choisi le même élément
            self.match.player1_score += 1
            self.match.player2_score += 1
        
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save()
        
        self.match.save()
        return True


class VersusChoice(models.Model):
    """Choix d'un joueur dans un round"""
    
    round = models.ForeignKey(
        VersusRound,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name="Round"
    )
    player = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Joueur"
    )
    chosen_item = models.ForeignKey(
        ListItem,
        on_delete=models.CASCADE,
        verbose_name="Élément choisi"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date du choix"
    )
    
    class Meta:
        verbose_name = "Choix Versus"
        verbose_name_plural = "Choix Versus"
        ordering = ['created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['round', 'player'],
                name='unique_choice_per_player_per_round'
            ),
        ]
    
    def __str__(self):
        return f"{self.player.username} choisit {self.chosen_item.title}"
    
    def clean(self):
        """Validation personnalisée"""
        from django.core.exceptions import ValidationError
        
        # Vérifier que le joueur fait partie du match
        if not self.round.match.is_player(self.player):
            raise ValidationError("Ce joueur ne fait pas partie de ce match")
        
        # Vérifier que l'élément choisi fait partie du round
        if self.chosen_item not in self.round.get_items():
            raise ValidationError("L'élément choisi ne fait pas partie de ce round")
