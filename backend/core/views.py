from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets, serializers
from django.db import models
from django.db.models import Q, Count
from django.core.cache import cache
from .serializers import RegisterSerializer, ListSerializer, ListItemSerializer
from .models import List, ListItem
from .permissions import IsOwnerOrReadOnly
import json
import hashlib

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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_items(request):
    """
    Recherche d'éléments avec auto-complétion
    Paramètres: 
    - q: terme de recherche
    - category: filtre par catégorie (optionnel)
    - limit: nombre max de résultats (défaut: 10)
    """
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    limit = min(int(request.GET.get('limit', 10)), 50)  # Max 50 résultats
    
    if not query or len(query) < 2:
        return Response({'results': [], 'message': 'Requête trop courte'})
    
    # Créer une clé de cache unique
    cache_key = f"search:{hashlib.md5(f'{query}:{category}:{limit}'.encode()).hexdigest()}"
    cached_results = cache.get(cache_key)
    
    if cached_results:
        return Response(cached_results)
    
    # Recherche dans les éléments existants
    search_filter = Q(title__icontains=query)
    if category and category in ['FILMS', 'SERIES', 'MUSIQUE', 'LIVRES']:
        search_filter &= Q(list__category=category)
    
    # Rechercher dans tous les éléments avec comptage de popularité
    items = (ListItem.objects
             .filter(search_filter)
             .values('title', 'description', 'list__category')
             .annotate(popularity=Count('title'))
             .order_by('-popularity', 'title')
             [:limit])
    
    # Formater les résultats
    results = []
    seen_titles = set()
    
    for item in items:
        title_lower = item['title'].lower()
        if title_lower not in seen_titles:
            seen_titles.add(title_lower)
            results.append({
                'title': item['title'],
                'description': item['description'] or '',
                'category': item['list__category'],
                'category_display': dict(List.Category.choices)[item['list__category']],
                'popularity': item['popularity']
            })
    
    # Ajouter des suggestions génériques si peu de résultats
    if len(results) < 5:
        generic_suggestions = _get_generic_suggestions(query, category, 5 - len(results))
        results.extend(generic_suggestions)
    
    response_data = {
        'results': results,
        'query': query,
        'category': category,
        'total': len(results)
    }
    
    # Cache pendant 10 minutes
    cache.set(cache_key, response_data, 600)
    
    return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_suggestions(request):
    """
    Suggestions d'éléments populaires par catégorie
    Paramètres:
    - category: catégorie ciblée (optionnel)
    - limit: nombre de suggestions (défaut: 6)
    """
    category = request.GET.get('category', '').strip()
    limit = min(int(request.GET.get('limit', 6)), 20)  # Max 20 suggestions
    
    # Clé de cache
    cache_key = f"suggestions:{category}:{limit}"
    cached_suggestions = cache.get(cache_key)
    
    if cached_suggestions:
        return Response(cached_suggestions)
    
    suggestions = []
    
    if category and category in ['FILMS', 'SERIES', 'MUSIQUE', 'LIVRES']:
        # Suggestions pour une catégorie spécifique
        category_suggestions = _get_category_suggestions(category, limit)
        suggestions = category_suggestions
    else:
        # Suggestions mixtes de toutes les catégories
        per_category = max(1, limit // 4)
        for cat in ['FILMS', 'SERIES', 'MUSIQUE', 'LIVRES']:
            cat_suggestions = _get_category_suggestions(cat, per_category)
            suggestions.extend(cat_suggestions)
    
    response_data = {
        'suggestions': suggestions[:limit],
        'category': category or 'all',
        'total': len(suggestions[:limit])
    }
    
    # Cache pendant 30 minutes
    cache.set(cache_key, response_data, 1800)
    
    return Response(response_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quick_add_item(request):
    """
    Ajout rapide d'un élément à une liste
    Body: {
        "title": "Titre de l'élément",
        "description": "Description optionnelle",
        "category": "FILMS|SERIES|MUSIQUE|LIVRES"
    }
    """
    title = request.data.get('title', '').strip()
    description = request.data.get('description', '').strip()
    category = request.data.get('category', '').strip()
    
    # Validation
    if not title:
        return Response(
            {'error': 'Le titre est obligatoire'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if category not in ['FILMS', 'SERIES', 'MUSIQUE', 'LIVRES']:
        return Response(
            {'error': 'Catégorie invalide'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Récupérer ou créer la liste pour cette catégorie
        user_list, created = List.objects.get_or_create(
            owner=request.user,
            category=category,
            defaults={
                'name': List.get_default_name(category),
                'description': List.get_default_description(category)
            }
        )
        
        # Vérifier si l'élément existe déjà
        existing_item = ListItem.objects.filter(
            list=user_list,
            title__iexact=title
        ).first()
        
        if existing_item:
            return Response(
                {'error': 'Cet élément existe déjà dans votre liste'}, 
                status=status.HTTP_409_CONFLICT
            )
        
        # Calculer la prochaine position
        max_position = ListItem.objects.filter(list=user_list).aggregate(
            max_pos=models.Max('position')
        )['max_pos'] or 0
        
        # Créer l'élément
        new_item = ListItem.objects.create(
            title=title,
            description=description,
            list=user_list,
            position=max_position + 1
        )
        
        # Sérialiser la réponse
        serializer = ListItemSerializer(new_item)
        
        # Invalider le cache des suggestions pour cette catégorie
        cache.delete(f"suggestions:{category}:*")
        
        return Response({
            'item': serializer.data,
            'list': {
                'id': user_list.id,
                'name': user_list.name,
                'category': category,
                'category_display': user_list.get_category_display()
            },
            'message': f'"{title}" ajouté à votre liste {user_list.get_category_display()}'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de l\'ajout: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _get_category_suggestions(category, limit):
    """Récupère les suggestions populaires pour une catégorie"""
    # Éléments les plus populaires (apparaissant dans plusieurs listes)
    popular_items = (ListItem.objects
                    .filter(list__category=category)
                    .values('title', 'description')
                    .annotate(count=Count('title'))
                    .filter(count__gte=2)  # Au moins 2 utilisateurs
                    .order_by('-count', 'title')
                    [:limit])
    
    suggestions = []
    for item in popular_items:
        suggestions.append({
            'title': item['title'],
            'description': item['description'] or '',
            'category': category,
            'category_display': dict(List.Category.choices)[category],
            'popularity': item['count'],
            'type': 'popular'
        })
    
    # Si pas assez d'éléments populaires, ajouter des suggestions de base
    if len(suggestions) < limit:
        base_suggestions = _get_base_suggestions(category, limit - len(suggestions))
        suggestions.extend(base_suggestions)
    
    return suggestions


def _get_base_suggestions(category, limit):
    """Suggestions de base par catégorie quand pas assez de données"""
    base_items = {
        'FILMS': [
            {'title': 'Blade Runner 2049', 'description': 'Science-fiction néo-noir'},
            {'title': 'Dune', 'description': 'Épopée de science-fiction'},
            {'title': 'Interstellar', 'description': 'Drame de science-fiction'},
            {'title': 'The Matrix', 'description': 'Action cyberpunk'},
            {'title': 'Inception', 'description': 'Thriller psychologique'},
        ],
        'SERIES': [
            {'title': 'Breaking Bad', 'description': 'Drame criminel'},
            {'title': 'Stranger Things', 'description': 'Science-fiction horreur'},
            {'title': 'The Crown', 'description': 'Drame historique'},
            {'title': 'Game of Thrones', 'description': 'Fantasy épique'},
            {'title': 'The Office', 'description': 'Comédie'},
        ],
        'MUSIQUE': [
            {'title': 'Bohemian Rhapsody - Queen', 'description': 'Rock classique'},
            {'title': 'Hotel California - Eagles', 'description': 'Rock'},
            {'title': 'Billie Jean - Michael Jackson', 'description': 'Pop'},
            {'title': 'Imagine - John Lennon', 'description': 'Folk rock'},
            {'title': 'Smells Like Teen Spirit - Nirvana', 'description': 'Grunge'},
        ],
        'LIVRES': [
            {'title': 'Le Seigneur des Anneaux', 'description': 'Fantasy épique'},
            {'title': '1984', 'description': 'Dystopie'},
            {'title': 'Harry Potter à l\'école des sorciers', 'description': 'Fantasy jeunesse'},
            {'title': 'L\'Étranger', 'description': 'Roman philosophique'},
            {'title': 'Le Petit Prince', 'description': 'Conte philosophique'},
        ]
    }
    
    items = base_items.get(category, [])[:limit]
    suggestions = []
    
    for item in items:
        suggestions.append({
            'title': item['title'],
            'description': item['description'],
            'category': category,
            'category_display': dict(List.Category.choices)[category],
            'popularity': 0,
            'type': 'suggestion'
        })
    
    return suggestions


def _get_generic_suggestions(query, category, limit):
    """Suggestions génériques basées sur la requête"""
    # Pour l'instant, retourner une liste vide
    # Peut être étendu avec de l'IA/ML plus tard
    return []