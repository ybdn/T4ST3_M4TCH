from django.db import models
from django.contrib.auth.models import User


class List(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom de la liste")
    description = models.TextField(blank=True, verbose_name="Description")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taste_lists', verbose_name="Propriétaire")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    
    class Meta:
        verbose_name = "Liste de goûts"
        verbose_name_plural = "Listes de goûts"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.owner.username}"
