from django.db import models
from django.contrib.auth.models import User


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
