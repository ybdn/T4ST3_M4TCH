from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
import string
import hashlib


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


# ========================================
# MODÈLES SYSTÈME MATCH GLOBAL + SOCIAL
# ========================================

class UserProfile(models.Model):
    """Profil utilisateur étendu avec gamertag et infos sociales"""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile',
        verbose_name="Utilisateur"
    )
    gamertag = models.CharField(
        max_length=20, 
        unique=True,
        verbose_name="Gamertag unique"
    )
    display_name = models.CharField(
        max_length=50, 
        verbose_name="Nom d'affichage"
    )
    bio = models.TextField(
        blank=True, 
        verbose_name="Biographie"
    )
    avatar_url = models.URLField(
        blank=True, 
        verbose_name="URL de l'avatar"
    )
    is_public = models.BooleanField(
        default=True, 
        verbose_name="Profil public"
    )
    total_matches = models.PositiveIntegerField(
        default=0, 
        verbose_name="Nombre total de matchs"
    )
    successful_matches = models.PositiveIntegerField(
        default=0, 
        verbose_name="Matchs ayant mené à un ajout"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Date de modification"
    )
    
    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateur"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.display_name} ({self.gamertag})"
    
    @classmethod
    def generate_unique_gamertag(cls):
        """Génère un gamertag unique au format TM_XXXX"""
        while True:
            # Génère 4 caractères alphanumériques aléatoirement
            suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            gamertag = f"TM_{suffix}"
            
            # Vérifie que le gamertag n'existe pas déjà
            if not cls.objects.filter(gamertag=gamertag).exists():
                return gamertag
    
    def save(self, *args, **kwargs):
        # Génère automatiquement un gamertag si non défini
        if not self.gamertag:
            self.gamertag = self.generate_unique_gamertag()
        
        # Utilise le username comme display_name par défaut
        if not self.display_name:
            self.display_name = self.user.username
        
        super().save(*args, **kwargs)


class UserPreference(models.Model):
    """Actions utilisateur sur du contenu externe (likes, dislikes, ajouts)"""
    
    class ContentType(models.TextChoices):
        FILMS = 'FILMS', 'Films'
        SERIES = 'SERIES', 'Séries'
        MUSIQUE = 'MUSIQUE', 'Musique'
        LIVRES = 'LIVRES', 'Livres'
    
    class Source(models.TextChoices):
        TMDB = 'tmdb', 'The Movie Database'
        SPOTIFY = 'spotify', 'Spotify'
        GOOGLE_BOOKS = 'google_books', 'Google Books'
        OPENLIBRARY = 'openlibrary', 'Open Library'
    
    class Action(models.TextChoices):
        LIKED = 'liked', 'Aimé'
        DISLIKED = 'disliked', 'Pas aimé'
        ADDED = 'added', 'Ajouté à une liste'
        SKIPPED = 'skipped', 'Ignoré'
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='preferences',
        verbose_name="Utilisateur"
    )
    external_id = models.CharField(
        max_length=100, 
        verbose_name="ID externe du contenu"
    )
    content_type = models.CharField(
        max_length=20, 
        choices=ContentType.choices,
        verbose_name="Type de contenu"
    )
    source = models.CharField(
        max_length=20, 
        choices=Source.choices,
        verbose_name="Source API"
    )
    action = models.CharField(
        max_length=20, 
        choices=Action.choices,
        verbose_name="Action utilisateur"
    )
    title = models.CharField(
        max_length=200, 
        verbose_name="Titre du contenu"
    )
    metadata = models.JSONField(
        default=dict, 
        blank=True,
        verbose_name="Métadonnées du contenu"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date de l'action"
    )
    
    class Meta:
        verbose_name = "Préférence utilisateur"
        verbose_name_plural = "Préférences utilisateur"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'external_id', 'source'], 
                name='unique_user_content_preference'
            ),
        ]
        indexes = [
            models.Index(fields=['user', 'content_type']),
            models.Index(fields=['user', 'action']),
            models.Index(fields=['external_id', 'source']),
        ]
    
    def __str__(self):
        return f"{self.user.username} → {self.get_action_display()} : {self.title}"


class Friendship(models.Model):
    """Système d'amitié entre utilisateurs"""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        ACCEPTED = 'accepted', 'Acceptée'
        BLOCKED = 'blocked', 'Bloquée'
        DECLINED = 'declined', 'Refusée'
    
    requester = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='friend_requests_sent',
        verbose_name="Demandeur"
    )
    addressee = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='friend_requests_received',
        verbose_name="Destinataire"
    )
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING,
        verbose_name="Statut de l'amitié"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date de la demande"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Date de mise à jour"
    )
    
    class Meta:
        verbose_name = "Amitié"
        verbose_name_plural = "Amitiés"
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['requester', 'addressee'], 
                name='unique_friendship_request'
            ),
        ]
        indexes = [
            models.Index(fields=['requester', 'status']),
            models.Index(fields=['addressee', 'status']),
        ]
    
    def __str__(self):
        return f"{self.requester.username} → {self.addressee.username} ({self.get_status_display()})"
    
    def accept(self):
        """Accepte la demande d'amitié"""
        self.status = self.Status.ACCEPTED
        self.save()
    
    def decline(self):
        """Refuse la demande d'amitié"""
        self.status = self.Status.DECLINED
        self.save()
    
    def block(self):
        """Bloque l'utilisateur"""
        self.status = self.Status.BLOCKED
        self.save()
    
    @classmethod
    def are_friends(cls, user1, user2):
        """Vérifie si deux utilisateurs sont amis"""
        return cls.objects.filter(
            models.Q(requester=user1, addressee=user2) | 
            models.Q(requester=user2, addressee=user1),
            status=cls.Status.ACCEPTED
        ).exists()
    
    @classmethod
    def get_friends(cls, user):
        """Récupère tous les amis d'un utilisateur"""
        friendships = cls.objects.filter(
            models.Q(requester=user) | models.Q(addressee=user),
            status=cls.Status.ACCEPTED
        ).select_related('requester', 'addressee')
        
        friends = []
        for friendship in friendships:
            if friendship.requester == user:
                friends.append(friendship.addressee)
            else:
                friends.append(friendship.requester)
        
        return friends


class FriendMatch(models.Model):
    """Matchs et défis entre amis"""
    
    class MatchType(models.TextChoices):
        TASTE_COMPATIBILITY = 'taste_compatibility', 'Compatibilité des goûts'
        VERSUS_CHALLENGE = 'versus_challenge', 'Défi Versus'
        DISCOVERY_SYNC = 'discovery_sync', 'Découverte synchrone'
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Actif'
        COMPLETED = 'completed', 'Terminé'
        ABANDONED = 'abandoned', 'Abandonné'
    
    user1 = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='matches_as_user1',
        verbose_name="Utilisateur 1"
    )
    user2 = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='matches_as_user2',
        verbose_name="Utilisateur 2"
    )
    match_type = models.CharField(
        max_length=30, 
        choices=MatchType.choices,
        default=MatchType.VERSUS_CHALLENGE,
        verbose_name="Type de match"
    )
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.ACTIVE,
        verbose_name="Statut du match"
    )
    score_user1 = models.PositiveIntegerField(
        default=0, 
        verbose_name="Score utilisateur 1"
    )
    score_user2 = models.PositiveIntegerField(
        default=0, 
        verbose_name="Score utilisateur 2"
    )
    compatibility_score = models.FloatField(
        null=True, 
        blank=True,
        verbose_name="Score de compatibilité (%)"
    )
    total_rounds = models.PositiveIntegerField(
        default=10, 
        verbose_name="Nombre de rounds total"
    )
    current_round = models.PositiveIntegerField(
        default=1, 
        verbose_name="Round actuel"
    )
    last_activity = models.DateTimeField(
        auto_now=True, 
        verbose_name="Dernière activité"
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name="Match actif"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date de création"
    )
    
    class Meta:
        verbose_name = "Match entre amis"
        verbose_name_plural = "Matchs entre amis"
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user1', 'status']),
            models.Index(fields=['user2', 'status']),
            models.Index(fields=['is_active', 'last_activity']),
        ]
    
    def __str__(self):
        return f"Match {self.get_match_type_display()}: {self.user1.username} vs {self.user2.username}"
    
    def get_opponent(self, user):
        """Retourne l'adversaire pour un utilisateur donné"""
        if self.user1 == user:
            return self.user2
        elif self.user2 == user:
            return self.user1
        return None
    
    def get_user_score(self, user):
        """Retourne le score d'un utilisateur"""
        if self.user1 == user:
            return self.score_user1
        elif self.user2 == user:
            return self.score_user2
        return 0
    
    def increment_user_score(self, user, points=1):
        """Incrémente le score d'un utilisateur"""
        if self.user1 == user:
            self.score_user1 += points
        elif self.user2 == user:
            self.score_user2 += points
        self.save()
    
    def is_completed(self):
        """Vérifie si le match est terminé"""
        return self.current_round > self.total_rounds or self.status == self.Status.COMPLETED
    
    def next_round(self):
        """Passe au round suivant"""
        if not self.is_completed():
            self.current_round += 1
            if self.current_round > self.total_rounds:
                self.status = self.Status.COMPLETED
            self.save()
    
    def calculate_compatibility(self):
        """Calcule le score de compatibilité basé sur les sessions"""
        sessions = self.sessions.all()
        if not sessions.exists():
            return 0.0
        
        total_sessions = sessions.count()
        matching_sessions = sessions.filter(is_match=True).count()
        
        compatibility = (matching_sessions / total_sessions) * 100
        self.compatibility_score = round(compatibility, 2)
        self.save()
        return self.compatibility_score


class MatchSession(models.Model):
    """Session individuelle dans un match entre amis"""
    
    class Choice(models.TextChoices):
        LIKED = 'liked', 'Aimé'
        DISLIKED = 'disliked', 'Pas aimé'
        SKIPPED = 'skipped', 'Ignoré'
    
    match = models.ForeignKey(
        FriendMatch, 
        on_delete=models.CASCADE, 
        related_name='sessions',
        verbose_name="Match"
    )
    round_number = models.PositiveIntegerField(
        verbose_name="Numéro du round"
    )
    content_external_id = models.CharField(
        max_length=100, 
        verbose_name="ID externe du contenu"
    )
    content_type = models.CharField(
        max_length=20, 
        choices=UserPreference.ContentType.choices,
        verbose_name="Type de contenu"
    )
    content_source = models.CharField(
        max_length=20, 
        choices=UserPreference.Source.choices,
        verbose_name="Source du contenu"
    )
    content_title = models.CharField(
        max_length=200, 
        verbose_name="Titre du contenu"
    )
    content_metadata = models.JSONField(
        default=dict, 
        blank=True,
        verbose_name="Métadonnées du contenu"
    )
    user1_choice = models.CharField(
        max_length=20, 
        choices=Choice.choices,
        null=True, 
        blank=True,
        verbose_name="Choix utilisateur 1"
    )
    user2_choice = models.CharField(
        max_length=20, 
        choices=Choice.choices,
        null=True, 
        blank=True,
        verbose_name="Choix utilisateur 2"
    )
    user1_choice_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Date choix utilisateur 1"
    )
    user2_choice_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Date choix utilisateur 2"
    )
    is_match = models.BooleanField(
        default=False, 
        verbose_name="Match (les deux ont aimé)"
    )
    is_completed = models.BooleanField(
        default=False, 
        verbose_name="Session terminée"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date de création"
    )
    
    class Meta:
        verbose_name = "Session de match"
        verbose_name_plural = "Sessions de match"
        ordering = ['match', 'round_number']
        constraints = [
            models.UniqueConstraint(
                fields=['match', 'round_number'], 
                name='unique_round_per_match'
            ),
        ]
        indexes = [
            models.Index(fields=['match', 'is_completed']),
            models.Index(fields=['content_external_id', 'content_source']),
        ]
    
    def __str__(self):
        return f"Session R{self.round_number}: {self.content_title} ({self.match})"
    
    def set_user_choice(self, user, choice):
        """Enregistre le choix d'un utilisateur"""
        now = timezone.now()
        
        if self.match.user1 == user:
            self.user1_choice = choice
            self.user1_choice_at = now
        elif self.match.user2 == user:
            self.user2_choice = choice
            self.user2_choice_at = now
        
        # Vérifier si la session est terminée
        if self.user1_choice and self.user2_choice:
            self.is_completed = True
            
            # Vérifier si c'est un match (les deux ont aimé)
            if (self.user1_choice == self.Choice.LIKED and 
                self.user2_choice == self.Choice.LIKED):
                self.is_match = True
                
                # Incrémenter les scores
                self.match.increment_user_score(self.match.user1)
                self.match.increment_user_score(self.match.user2)
        
        self.save()
    
    def get_user_choice(self, user):
        """Retourne le choix d'un utilisateur"""
        if self.match.user1 == user:
            return self.user1_choice
        elif self.match.user2 == user:
            return self.user2_choice
        return None
    
    def is_waiting_for_user(self, user):
        """Vérifie si on attend le choix d'un utilisateur"""
        user_choice = self.get_user_choice(user)
        return user_choice is None and not self.is_completed


# ========================================
# MODÈLES SYSTÈME FEATURE FLAGS
# ========================================

class FeatureFlag(models.Model):
    """Système de feature flags pour activer/désactiver des fonctionnalités progressivement"""
    
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nom du feature flag"
    )
    enabled = models.BooleanField(
        default=False,
        verbose_name="Activé"
    )
    rollout_percentage = models.PositiveIntegerField(
        default=0,
        verbose_name="Pourcentage de déploiement (0-100)"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description du flag"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    
    class Meta:
        verbose_name = "Feature Flag"
        verbose_name_plural = "Feature Flags"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['enabled']),
        ]
    
    def __str__(self):
        status = "✅" if self.enabled else "❌"
        rollout = f" ({self.rollout_percentage}%)" if self.rollout_percentage < 100 and self.enabled else ""
        return f"{status} {self.name}{rollout}"
    
    # Removed is_enabled classmethod - use FeatureFlagsService.is_enabled() instead
    # to avoid duplication and ensure cache consistency
    
    def clean(self):
        """Validation du modèle"""
        from django.core.exceptions import ValidationError
        
        if not (0 <= self.rollout_percentage <= 100):
            raise ValidationError("Le pourcentage de déploiement doit être entre 0 et 100")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
