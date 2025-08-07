from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée pour ne permettre aux propriétaires d'un objet 
    que d'en modifier le contenu. Permet la lecture pour tous les utilisateurs authentifiés.
    """

    def has_object_permission(self, request, view, obj):
        # Permissions de lecture pour tous les utilisateurs authentifiés
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Permissions d'écriture seulement pour le propriétaire de l'objet
        return obj.owner == request.user