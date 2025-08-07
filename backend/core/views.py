from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets, serializers
from django.db import models
from .serializers import RegisterSerializer, ListSerializer, ListItemSerializer
from .models import List, ListItem
from .permissions import IsOwnerOrReadOnly

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Returns a simple JSON response to indicate that the API is running.
    """
    return Response(
        {"status": "ok", "message": "API is running"},
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email
    })


class ListViewSet(viewsets.ModelViewSet):
    serializer_class = ListSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        # Un utilisateur ne peut voir que ses propres listes
        return List.objects.filter(owner=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """Retourne les 4 listes fixes, en les créant automatiquement si nécessaire"""
        user = request.user
        lists_data = []
        
        # Créer automatiquement toutes les listes manquantes
        for category_value, category_label in List.Category.choices:
            user_list, created = List.objects.get_or_create(
                owner=user,
                category=category_value,
                defaults={
                    'name': List.get_default_name(category_value),
                    'description': List.get_default_description(category_value)
                }
            )
            lists_data.append(user_list)
        
        # Sérialiser et retourner les listes
        serializer = self.get_serializer(lists_data, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Désactiver la création de nouvelles listes"""
        return Response(
            {'detail': 'La création de listes n\'est pas autorisée. Les 4 listes fixes sont créées automatiquement.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def destroy(self, request, *args, **kwargs):
        """Vider la liste au lieu de la supprimer"""
        list_obj = self.get_object()
        # Supprimer tous les éléments de la liste
        list_obj.items.all().delete()
        return Response(
            {'detail': f'La liste "{list_obj.name}" a été vidée avec succès.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Retourne les catégories disponibles"""
        categories = [
            {'value': choice[0], 'label': choice[1]} 
            for choice in List.Category.choices
        ]
        return Response(categories)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Retourne toutes les listes organisées par catégorie (avec auto-création)"""
        user = request.user
        result = {}
        
        for category_value, category_label in List.Category.choices:
            user_list, created = List.objects.get_or_create(
                owner=user,
                category=category_value,
                defaults={
                    'name': List.get_default_name(category_value),
                    'description': List.get_default_description(category_value)
                }
            )
            result[category_value] = {
                'category_label': category_label,
                'list': ListSerializer(user_list).data
            }
        
        return Response(result)


class ListItemViewSet(viewsets.ModelViewSet):
    serializer_class = ListItemSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        # Filtrer par liste si on est dans une route imbriquée
        if hasattr(self, 'list_pk') or 'list_pk' in self.kwargs:
            list_pk = getattr(self, 'list_pk', self.kwargs.get('list_pk'))
            return ListItem.objects.filter(
                list__pk=list_pk, 
                list__owner=self.request.user
            )
        # Sinon, retourner tous les éléments de l'utilisateur
        return ListItem.objects.filter(list__owner=self.request.user)
    
    def perform_create(self, serializer):
        # Dans le cas d'une route imbriquée, utiliser la liste de l'URL
        if 'list_pk' in self.kwargs:
            try:
                list_obj = List.objects.get(
                    pk=self.kwargs['list_pk'], 
                    owner=self.request.user
                )
                # Définir automatiquement la position si elle n'est pas fournie
                if not serializer.validated_data.get('position'):
                    max_position = ListItem.objects.filter(list=list_obj).aggregate(
                        max_pos=models.Max('position')
                    )['max_pos'] or 0
                    serializer.validated_data['position'] = max_position + 1
                
                serializer.save(list=list_obj)
                
            except List.DoesNotExist:
                raise serializers.ValidationError("Liste non trouvée ou vous n'êtes pas le propriétaire")
        else:
            # Vérifier que la liste appartient à l'utilisateur
            list_obj = serializer.validated_data.get('list')
            if not list_obj or list_obj.owner != self.request.user:
                raise serializers.ValidationError("Vous ne pouvez ajouter des éléments qu'à vos propres listes")
            
            # Définir automatiquement la position si elle n'est pas fournie
            if not serializer.validated_data.get('position'):
                max_position = ListItem.objects.filter(list=list_obj).aggregate(
                    max_pos=models.Max('position')
                )['max_pos'] or 0
                serializer.validated_data['position'] = max_position + 1
            
            serializer.save()