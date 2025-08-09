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
        # Pour les ListItem, vérifier le propriétaire de la liste parent
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'list') and hasattr(obj.list, 'owner'):
            return obj.list.owner == request.user
        else:
            return False