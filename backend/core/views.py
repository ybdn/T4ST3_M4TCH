from rest_framework.decorators import api_view, permission_classes, action, throttle_classes
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets, serializers
from django.db import models
from django.db.models import Q, Count
from django.core.cache import cache
from .serializers import RegisterSerializer, ListSerializer, ListItemSerializer
from .models import List, ListItem, ExternalReference
from .permissions import IsOwnerOrReadOnly
from .services.external_enrichment_service import ExternalEnrichmentService
from .match_services import CompatibilityService
import json
import hashlib
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([ScopedRateThrottle])
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
@throttle_classes([ScopedRateThrottle])
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

        # Enrichissement automatique après création (forcé pour assurer la cohérence)
        try:
            created_item = serializer.instance
            if created_item and created_item.list.category in ['FILMS', 'SERIES', 'MUSIQUE', 'LIVRES']:
                enrichment_service = ExternalEnrichmentService()
                enrichment_service.enrich_list_item(created_item, force_refresh=True)
        except Exception as e:
            # Ne pas bloquer la création en cas d'erreur d'enrichissement
            logger.warning(f"Could not enrich item {created_item.id if 'created_item' in locals() else 'unknown'}: {e}")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
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
@throttle_classes([ScopedRateThrottle])
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
@throttle_classes([ScopedRateThrottle])
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
        
        # Enrichissement automatique (forcé pour assurer la cohérence)
        try:
            enrichment_service = ExternalEnrichmentService()
            enrichment_service.enrich_list_item(new_item, force_refresh=True)
        except Exception as e:
            logger.warning(f"Could not enrich item {new_item.id}: {e}")

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
    # Suggestions intelligentes basées sur la requête et la catégorie
    generic_suggestions = {
        'FILMS': [
            {'title': f'{query} - Film', 'description': f'Film sur le thème de {query}'},
            {'title': f'Le {query}', 'description': f'Film intitulé {query}'},
            {'title': f'{query} : L\'histoire', 'description': f'Documentaire sur {query}'},
        ],
        'SERIES': [
            {'title': f'{query} - Série', 'description': f'Série sur le thème de {query}'},
            {'title': f'{query} : La série', 'description': f'Série intitulée {query}'},
        ],
        'MUSIQUE': [
            {'title': f'{query} - Album', 'description': f'Album de {query}'},
            {'title': f'{query} - Single', 'description': f'Chanson de {query}'},
        ],
        'LIVRES': [
            {'title': f'{query} - Livre', 'description': f'Livre sur {query}'},
            {'title': f'Le {query}', 'description': f'Livre intitulé {query}'},
        ]
    }
    
    suggestions = generic_suggestions.get(category, [])[:limit]
    return [
        {
            'title': item['title'],
            'description': item['description'],
            'category': category,
            'category_display': dict(List.Category.choices)[category],
            'popularity': 0,
            'type': 'suggestion'
        }
        for item in suggestions
    ]


# =====================================
# EXTERNAL APIS ENDPOINTS
# =====================================


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def get_trending_external(request):
    """
    Récupère le contenu tendance des APIs externes
    Paramètres:
    - category: filtre par catégorie (optionnel)
    - time_window: day/week pour TMDB (défaut: week)
    - limit: nombre de résultats (défaut: 20)
    """
    category = request.GET.get('category', '').strip()
    time_window = request.GET.get('time_window', 'week')
    limit = min(int(request.GET.get('limit', 20)), 50)
    
    try:
        enrichment_service = ExternalEnrichmentService()
        results = enrichment_service.get_trending_content(category, limit)
        
        return Response({
            'results': results,
            'category': category or 'all',
            'total': len(results)
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la récupération du contenu tendance: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def enrich_list_item(request, list_pk, item_pk):
    """
    Enrichit un élément de liste existant avec des métadonnées externes
    """
    try:
        # Vérifier que l'élément appartient à l'utilisateur
        list_item = ListItem.objects.get(
            pk=item_pk,
            list__pk=list_pk,
            list__owner=request.user
        )
        
        force_refresh = request.data.get('force_refresh', False)
        
        enrichment_service = ExternalEnrichmentService()
        success = enrichment_service.enrich_list_item(list_item, force_refresh)
        
        if success:
            # Récupérer les données enrichies
            external_ref = getattr(list_item, 'external_ref', None)
            if external_ref:
                return Response({
                    'message': f'Élément "{list_item.title}" enrichi avec succès',
                    'external_reference': {
                        'source': external_ref.external_source,
                        'poster_url': external_ref.poster_url,
                        'backdrop_url': external_ref.backdrop_url,
                        'rating': external_ref.rating,
                        'release_date': external_ref.release_date,
                        'metadata': external_ref.metadata
                    }
                })
            else:
                return Response({'message': 'Enrichissement effectué mais aucune donnée trouvée'})
        else:
            return Response(
                {'error': 'Impossible d\'enrichir cet élément'},
                status=status.HTTP_404_NOT_FOUND
            )
            
    except ListItem.DoesNotExist:
        return Response(
            {'error': 'Élément non trouvé ou vous n\'êtes pas le propriétaire'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de l\'enrichissement: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def import_from_external(request):
    """
    Importe directement depuis un ID externe
    Body: {
        "external_id": "550",
        "source": "tmdb|spotify|openlibrary|google_books",
        "category": "FILMS|SERIES|MUSIQUE|LIVRES"
    }
    """
    external_id = request.data.get('external_id', '').strip()
    source = request.data.get('source', '').strip()
    category = request.data.get('category', '').strip()
    
    # Validation
    if not external_id:
        return Response(
            {'error': 'L\'ID externe est obligatoire'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if source not in ['tmdb', 'spotify', 'openlibrary', 'google_books']:
        return Response(
            {'error': 'Source non supportée'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if category not in ['FILMS', 'SERIES', 'MUSIQUE', 'LIVRES']:
        return Response(
            {'error': 'Catégorie invalide'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        enrichment_service = ExternalEnrichmentService()
        result = enrichment_service.import_from_external_id(external_id, source, category, request.user)
        
        if result:
            list_item = result['list_item']
            external_data = result['external_data']
            
            return Response({
                'message': f'"{list_item.title}" importé avec succès',
                'item': ListItemSerializer(list_item).data,
                'external_data': {
                    'title': external_data.get('title'),
                    'description': external_data.get('description'),
                    'poster_url': external_data.get('poster_url'),
                    'rating': external_data.get('rating'),
                    'source': source
                }
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Impossible de trouver cet élément dans l\'API externe'},
                status=status.HTTP_404_NOT_FOUND
            )
            
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de l\'import: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def get_external_details(request, source, external_id):
    """
    Récupère les détails complets d'un élément externe
    """
    try:
        enrichment_service = ExternalEnrichmentService()
        
        if source == 'tmdb':
            # Essayer film puis série
            details = (enrichment_service.tmdb.get_movie_details(external_id) or
                      enrichment_service.tmdb.get_tv_show_details(external_id))
        elif source == 'spotify':
            # Essayer track puis artist puis album
            details = (enrichment_service.spotify.get_track_details(external_id) or
                      enrichment_service.spotify.get_artist_details(external_id) or
                      enrichment_service.spotify.get_album_details(external_id))
        elif source in ['openlibrary', 'google_books']:
            details = enrichment_service.books.get_book_details_by_isbn(external_id)
        else:
            return Response(
                {'error': 'Source non supportée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if details:
            return Response({
                'external_id': external_id,
                'source': source,
                'details': details
            })
        else:
            return Response(
                {'error': 'Élément non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
            
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la récupération des détails: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def get_trending_suggestions(request, category):
    """
    Suggestions basées sur le contenu tendance des APIs externes
    """
    limit = min(int(request.GET.get('limit', 10)), 50)
    time_window = request.GET.get('time_window', 'week')
    
    try:
        enrichment_service = ExternalEnrichmentService()
        results = enrichment_service.get_trending_content(category, limit)
        
        return Response({
            'suggestions': results,
            'category': category,
            'time_window': time_window,
            'total': len(results)
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la récupération des tendances: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def get_similar_suggestions(request, item_id):
    """
    Suggestions similaires basées sur un élément existant
    """
    limit = min(int(request.GET.get('limit', 10)), 50)
    
    try:
        # Récupérer l'élément de référence
        list_item = ListItem.objects.get(
            id=item_id,
            list__owner=request.user
        )
        
        # Utiliser la nouvelle méthode pour obtenir du contenu similaire
        enrichment_service = ExternalEnrichmentService()
        results = enrichment_service.get_similar_content(list_item, limit)
        
        return Response({
            'suggestions': results,
            'reference_item': {
                'id': list_item.id,
                'title': list_item.title,
                'category': list_item.list.category
            },
            'total': len(results)
        })
        
    except ListItem.DoesNotExist:
        return Response(
            {'error': 'Élément de référence non trouvé'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la récupération des suggestions: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def search_external(request):
    """
    Recherche dans les APIs externes (TMDB, Spotify, Google Books)
    """
    query = request.GET.get('q', '').strip()
    limit = min(int(request.GET.get('limit', 10)), 50)
    source = request.GET.get('source', '')  # tmdb, spotify, google_books
    category = request.GET.get('category', '')  # FILMS, SERIES, MUSIQUE, LIVRES
    
    if not query:
        return Response({
            'results': [],
            'query': query,
            'category': category,
            'source': source,
            'total': 0
        })
    
    results = []
    
    try:
        # Import des services
        from .services.tmdb_service import TMDBService
        from .services.spotify_service import SpotifyService
        from .services.books_service import BooksService
        
        # Rechercher selon la catégorie ou source spécifiée
        if not category or category == 'FILMS' or not source or source == 'tmdb':
            tmdb = TMDBService()
            movies = tmdb.search_movies(query, limit=limit//4 if not category else limit)
            for movie in movies:
                results.append({
                    'external_id': movie.get('external_id'),
                    'source': movie.get('source', 'tmdb'),
                    'category': 'FILMS',
                    'category_display': 'Films',
                    'title': movie.get('title', ''),
                    'description': movie.get('description', ''),
                    'poster_url': movie.get('poster_url'),
                    'release_date': movie.get('release_date', '')
                })
        
        if not category or category == 'SERIES' or not source or source == 'tmdb':
            tmdb = TMDBService()
            series = tmdb.search_tv_shows(query, limit=limit//4 if not category else limit)
            for show in series:
                results.append({
                    'external_id': show.get('external_id'),
                    'source': show.get('source', 'tmdb'),
                    'category': 'SERIES',
                    'category_display': 'Séries',
                    'title': show.get('title', ''),
                    'description': show.get('description', ''),
                    'poster_url': show.get('poster_url'),
                    'release_date': show.get('first_air_date', '')
                })
        
        if not category or category == 'MUSIQUE' or not source or source == 'spotify':
            try:
                spotify = SpotifyService()
                # Recherche plus complète : morceaux et albums
                music_results = spotify.search_music(query, limit=limit//4 if not category else limit)
                for item in music_results:
                    if isinstance(item, dict):
                        results.append({
                            'external_id': item.get('external_id'),
                            'source': item.get('source', 'spotify'),
                            'category': 'MUSIQUE',
                            'category_display': 'Musique',
                            'title': item.get('title', ''),
                            'description': item.get('description', ''),
                            'poster_url': item.get('poster_url'),
                            'release_date': item.get('release_date', ''),
                            'item_type': item.get('type')  # Ajout du type: track, album, artist
                        })
            except Exception as e:
                logger.error(f"Spotify search error: {e}")
        
        if not category or category == 'LIVRES' or not source or source == 'google_books':
            try:
                books = BooksService()
                book_results = books.search_books(query, limit=limit//4 if not category else limit)
                for book in book_results:
                    if isinstance(book, dict):
                        results.append({
                            'external_id': book.get('external_id'),
                            'source': book.get('source', 'google_books'),
                            'category': 'LIVRES',
                            'category_display': 'Livres',
                            'title': book.get('title', ''),
                            'description': book.get('description', ''),
                            'poster_url': book.get('poster_url'),
                            'release_date': book.get('published_date', ''),
                            'authors': book.get('authors', [])
                        })
            except Exception as e:
                logger.error(f"Google Books search error: {e}")
                
    except Exception as e:
        logger.error(f"External search error: {e}")
        return Response(
            {'error': f'Erreur lors de la recherche: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Limiter les résultats
    results = results[:limit]
    
    return Response({
        'results': results,
        'query': query,
        'category': category,
        'source': source,
        'total': len(results)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trending_external(request):
    """
    Récupère le contenu tendance depuis les APIs externes
    """
    category = request.GET.get('category', '')
    limit = min(int(request.GET.get('limit', 10)), 50)
    
    results = []
    
    try:
        from .services.tmdb_service import TMDBService
        from .services.spotify_service import SpotifyService
        from .services.books_service import BooksService
        
        if not category or category == 'FILMS':
            tmdb = TMDBService()
            trending_movies = tmdb.get_trending_movies(limit=limit//4 if not category else limit)
            for movie in trending_movies:
                results.append({
                    'external_id': movie.get('external_id'),
                    'source': movie.get('source', 'tmdb'),
                    'category': 'FILMS',
                    'category_display': 'Films',
                    'title': movie.get('title', ''),
                    'description': movie.get('description', ''),
                    'poster_url': movie.get('poster_url'),
                    'release_date': movie.get('release_date', '')
                })
        
        if not category or category == 'SERIES':
            tmdb = TMDBService()
            trending_tv = tmdb.get_trending_tv_shows(limit=limit//4 if not category else limit)
            for show in trending_tv:
                results.append({
                    'external_id': show.get('external_id'),
                    'source': show.get('source', 'tmdb'),
                    'category': 'SERIES',
                    'category_display': 'Séries',
                    'title': show.get('title', ''),
                    'description': show.get('description', ''),
                    'poster_url': show.get('poster_url'),
                    'release_date': show.get('first_air_date', '')
                })
        
        if category == 'MUSIQUE':
            try:
                spotify = SpotifyService()
                # Utiliser une recherche avec des termes populaires comme alternative
                popular_queries = ["pop", "rock", "hip hop", "electronic", "jazz"]
                for query in popular_queries[:2]:  # Limiter à 2 requêtes
                    try:
                        albums = spotify.search_albums(query, limit=limit//2)
                        for album in albums[:limit//2]:  # Limiter encore plus
                            if isinstance(album, dict) and album.get('external_id'):
                                results.append({
                                    'external_id': album.get('external_id'),
                                    'source': album.get('source', 'spotify'),
                                    'category': 'MUSIQUE',
                                    'category_display': 'Musique',
                                    'title': album.get('title', ''),
                                    'description': album.get('description', ''),
                                    'poster_url': album.get('poster_url'),
                                    'release_date': album.get('release_date', '')
                                })
                            if len(results) >= limit:
                                break
                    except Exception as query_error:
                        logger.error(f"Spotify query '{query}' error: {query_error}")
                        continue
                    if len(results) >= limit:
                        break
            except Exception as e:
                logger.error(f"Spotify trending error: {e}")
                
        if category == 'LIVRES':
            try:
                books = BooksService()
                # Pour les tendances, utiliser get_popular_books qui retourne des données formatées
                trending_books = books.get_popular_books(limit=limit)
                for book in trending_books:
                    if isinstance(book, dict) and book.get('external_id'):
                        results.append({
                            'external_id': book.get('external_id'),
                            'source': book.get('source', 'google_books'),
                            'category': 'LIVRES',
                            'category_display': 'Livres',
                            'title': book.get('title', ''),
                            'description': book.get('description', ''),
                            'poster_url': book.get('poster_url'),
                            'release_date': book.get('published_date', ''),
                            'authors': book.get('authors', [])
                        })
            except Exception as e:
                logger.error(f"Google Books trending error: {e}")
                
    except Exception as e:
        logger.error(f"External trending error: {e}")
        return Response(
            {'error': f'Erreur lors de la récupération des tendances: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Limiter les résultats
    results = results[:limit]
    
    return Response({
        'results': results,
        'category': category or 'all',
        'total': len(results)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_from_external(request):
    """
    Importe un élément depuis une API externe vers les listes de l'utilisateur
    """
    external_id = request.data.get('external_id')
    source = request.data.get('source')
    category = request.data.get('category')
    
    if not external_id or not source or not category:
        return Response(
            {'error': 'external_id, source et category sont obligatoires'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Créer ou récupérer la liste pour cette catégorie
        list_obj, created = List.objects.get_or_create(
            owner=request.user,
            category=category,
            defaults={
                'name': List.get_default_name(category),
                'description': List.get_default_description(category)
            }
        )
        
        # Déterminer le prochain numéro de position
        max_position = ListItem.objects.filter(list=list_obj).aggregate(
            max_pos=models.Max('position')
        )['max_pos'] or 0
        
        # Récupérer les détails depuis l'API externe
        from .services.external_enrichment_service import ExternalEnrichmentService
        enrichment_service = ExternalEnrichmentService()
        
        # Créer l'élément de base avec des informations minimales
        if source == 'tmdb':
            from .services.tmdb_service import TMDBService
            tmdb = TMDBService()
            if category == 'FILMS':
                details = tmdb.get_movie_details(external_id)
                if not details:
                    raise Exception('Film non trouvé sur TMDB.')
                title = details.get('title', f'Film {external_id}')
                description = details.get('description', '')
            else:  # SERIES
                details = tmdb.get_tv_show_details(external_id)
                if not details:
                    raise Exception('Série non trouvée sur TMDB.')
                title = details.get('title', f'Série {external_id}')
                description = details.get('description', '')
        elif source == 'spotify':
            from .services.spotify_service import SpotifyService
            spotify = SpotifyService()
            
            # Essayer de récupérer les détails en tant que morceau, puis en tant qu'album
            details = spotify.get_track_details(external_id)
            item_type = 'track'
            if not details:
                details = spotify.get_album_details(external_id)
                item_type = 'album'

            if not details:
                raise Exception('Impossible de trouver les détails sur Spotify.')

            artists = ', '.join(details.get('artists', []))
            if item_type == 'track':
                title = f"{details.get('title', '')} - {artists}"
                description = f"Morceau de {artists} de l'album {details.get('album', '')}"
            else: # album
                title = f"{details.get('title', '')} - {artists}"
                description = f"Album de {artists}"
        elif source == 'google_books':
            from .services.books_service import BooksService
            books = BooksService()
            details = books.get_book_details(external_id)
            volume_info = details.get('volumeInfo', {})
            title = volume_info.get('title', f'Livre {external_id}')
            authors = ', '.join(volume_info.get('authors', []))
            description = f"Par {authors}" if authors else volume_info.get('description', '')[:100]
        else:
            title = f'Élément {external_id}'
            description = f'Importé depuis {source}'
        
        # Créer l'élément de liste
        list_item = ListItem.objects.create(
            title=title,
            description=description,
            position=max_position + 1,
            list=list_obj
        )
        
        # Enrichir l'élément avec les données externes
        enrichment_service.enrich_list_item(list_item, force_refresh=True)
        
        return Response({
            'id': list_item.id,
            'title': list_item.title,
            'description': list_item.description,
            'category': category,
            'list_id': list_obj.id,
            'external_id': external_id,
            'source': source
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Import error: {e}")
        return Response(
            {'error': f'Erreur lors de l\'import: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_external_details(request, source, external_id):
    """
    Récupère les détails d'un élément depuis une API externe
    """
    try:
        if source == 'tmdb':
            from .services.tmdb_service import TMDBService
            tmdb = TMDBService()
            # Essayer d'abord comme un film, puis comme une série
            details = tmdb.get_movie_details(external_id)
            if not details:
                details = tmdb.get_tv_show_details(external_id)
        elif source == 'spotify':
            from .services.spotify_service import SpotifyService
            spotify = SpotifyService()
            details = spotify.get_album_details(external_id)
        elif source == 'google_books':
            from .services.books_service import BooksService
            books = BooksService()
            details = books.get_book_details(external_id)
        else:
            return Response(
                {'error': f'Source {source} non supportée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(details)
        
    except Exception as e:
        logger.error(f"External details error: {e}")
        return Response(
            {'error': f'Erreur lors de la récupération des détails: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ========================================
# ENDPOINTS SYSTÈME MATCH GLOBAL + SOCIAL
# ========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def get_match_recommendations(request):
    """
    Récupère des recommandations personnalisées pour le mode Global
    """
    try:
        # Import tardif depuis un module sans conflit de nom de package
        from .match_services import RecommendationService
        
        category = request.GET.get('category', None)
        count = int(request.GET.get('count', 10))
        
        recommendation_service = RecommendationService()
        recommendations = recommendation_service.get_recommendations(
            user=request.user,
            category=category,
            count=count
        )
        
        return Response({
            'results': recommendations,
            'count': len(recommendations),
            'category': category
        })
        
    except Exception as e:
        logger.error(f"Match recommendations error: {e}")
        return Response(
            {'error': f'Erreur lors de la récupération des recommandations: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Manual enrichment functions removed - enrichment is now automatic


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def submit_match_action(request):
    """
    Enregistre l'action d'un utilisateur sur une recommandation (like, dislike, add)
    """
    try:
        from .match_services import RecommendationService
        from .models import List, ListItem, ExternalReference, UserPreference
        from .serializers import MatchActionSerializer

        serializer = MatchActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data

        external_id = data['external_id']
        source = data['source']
        content_type = data['content_type']
        action = data['action']  # normalisé
        title = data['title']
        metadata = data.get('metadata', {}) or {}
        poster_url = data.get('poster_url') or metadata.get('poster_url')
        description_text = data.get('description') or metadata.get('description', '')

        recommendation_service = RecommendationService()
        content = {
            'external_id': external_id,
            'source': source,
            'content_type': content_type,
            'title': title,
            'metadata': metadata
        }

        preference, created, changed_action, previous_action = recommendation_service.mark_content_as_seen(
            user=request.user,
            content=content,
            action=action,
            return_status=True
        )

        response_data = {
            'success': True,
            'action': action,
            'preference_id': preference.id,
            'updated': changed_action and not created
        }

        # Ajout à la liste si la logique métier le requiert
        def _should_add_to_list(final_action, was_created, did_change, prev_action):
            return (
                final_action == UserPreference.Action.ADDED and (
                    was_created or (did_change and prev_action != UserPreference.Action.ADDED)
                )
            )

        if _should_add_to_list(action, created, changed_action, previous_action):
            try:
                list_obj, _ = List.objects.get_or_create(
                    owner=request.user,
                    category=content_type,
                    defaults={
                        'name': List.get_default_name(content_type),
                        'description': List.get_default_description(content_type)
                    }
                )
                max_position = ListItem.objects.filter(list=list_obj).aggregate(
                    models.Max('position')
                )['position__max'] or 0
                list_item = ListItem.objects.create(
                    title=title,
                    description=description_text,
                    position=max_position + 1,
                    list=list_obj
                )
                ExternalReference.objects.create(
                    list_item=list_item,
                    external_id=external_id,
                    external_source=source,
                    poster_url=poster_url,
                    backdrop_url=metadata.get('backdrop_url'),
                    metadata=metadata,
                    rating=metadata.get('vote_average') or metadata.get('average_rating')
                )
                try:
                    enrichment_service = ExternalEnrichmentService()
                    enrichment_service.enrich_list_item(list_item, force_refresh=True)
                except Exception as enrich_error:
                    logger.warning(f"Could not enrich item {list_item.id}: {enrich_error}")
                response_data['list_item_id'] = list_item.id
                response_data['list_id'] = list_obj.id
            except Exception as add_error:
                logger.warning(f"Could not add to list: {add_error}")

        return Response(response_data, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Match action error: {e}")
        return Response(
            {'error': f"Erreur lors de l'enregistrement de l'action: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def get_user_social_profile(request):
    """
    Récupère le profil social de l'utilisateur connecté
    """
    try:
        from .models import UserProfile, Friendship
        
        # Récupérer ou créer le profil
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'display_name': request.user.username
            }
        )
        
        # Compter les amis
        friends_count = len(Friendship.get_friends(request.user))
        
        # Compter les demandes en attente
        pending_requests = Friendship.objects.filter(
            addressee=request.user,
            status=Friendship.Status.PENDING
        ).count()
        
        return Response({
            'user_id': request.user.id,
            'username': request.user.username,
            'gamertag': profile.gamertag,
            'display_name': profile.display_name,
            'bio': profile.bio,
            'avatar_url': profile.avatar_url,
            'is_public': profile.is_public,
            'stats': {
                'total_matches': profile.total_matches,
                'successful_matches': profile.successful_matches,
                'friends_count': friends_count,
                'pending_requests': pending_requests
            },
            'created_at': profile.created_at
        })
        
    except Exception as e:
        logger.error(f"Social profile error: {e}")
        return Response(
            {'error': f'Erreur lors de la récupération du profil: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def update_user_social_profile(request):
    """
    Met à jour le profil social de l'utilisateur
    """
    try:
        from .models import UserProfile
        
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'display_name': request.user.username}
        )
        
        # Champs modifiables
        if 'display_name' in request.data:
            profile.display_name = request.data['display_name']
        if 'bio' in request.data:
            profile.bio = request.data['bio']
        if 'avatar_url' in request.data:
            profile.avatar_url = request.data['avatar_url']
        if 'is_public' in request.data:
            profile.is_public = request.data['is_public']
            
        profile.save()
        
        return Response({
            'success': True,
            'gamertag': profile.gamertag,
            'display_name': profile.display_name,
            'bio': profile.bio,
            'avatar_url': profile.avatar_url,
            'is_public': profile.is_public
        })
        
    except Exception as e:
        logger.error(f"Update social profile error: {e}")
        return Response(
            {'error': f'Erreur lors de la mise à jour: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def add_friend_by_gamertag(request):
    """
    Envoie une demande d'amitié via gamertag
    """
    try:
        from .models import UserProfile, Friendship
        
        gamertag = request.data.get('gamertag')
        if not gamertag:
            return Response(
                {'error': 'Gamertag requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Chercher l'utilisateur cible
        try:
            target_profile = UserProfile.objects.get(gamertag=gamertag)
            target_user = target_profile.user
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Gamertag introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Vérifier qu'on n'essaie pas de s'ajouter soi-même
        if target_user == request.user:
            return Response(
                {'error': 'Impossible de s\'ajouter soi-même'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier s'il y a déjà une relation
        existing_friendship = Friendship.objects.filter(
            models.Q(requester=request.user, addressee=target_user) |
            models.Q(requester=target_user, addressee=request.user)
        ).first()
        
        if existing_friendship:
            if existing_friendship.status == Friendship.Status.ACCEPTED:
                return Response(
                    {'error': 'Vous êtes déjà amis'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif existing_friendship.status == Friendship.Status.PENDING:
                return Response(
                    {'error': 'Demande déjà envoyée'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif existing_friendship.status == Friendship.Status.BLOCKED:
                return Response(
                    {'error': 'Impossible d\'ajouter cet utilisateur'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Créer la demande d'amitié
        friendship = Friendship.objects.create(
            requester=request.user,
            addressee=target_user,
            status=Friendship.Status.PENDING
        )
        
        return Response({
            'success': True,
            'friendship_id': friendship.id,
            'target_user': {
                'username': target_user.username,
                'gamertag': target_profile.gamertag,
                'display_name': target_profile.display_name
            },
            'status': 'pending'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Add friend error: {e}")
        return Response(
            {'error': f'Erreur lors de l\'ajout d\'ami: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def search_user_by_gamertag(request, gamertag):
    """
    Recherche un utilisateur par gamertag
    """
    try:
        from .models import UserProfile, Friendship
        profile = UserProfile.objects.select_related('user').get(gamertag=gamertag)
        # Déterminer relation actuelle
        relation = Friendship.objects.filter(
            models.Q(requester=request.user, addressee=profile.user) |
            models.Q(requester=profile.user, addressee=request.user)
        ).first()
        relation_status = relation.status if relation else None
        is_friend = relation_status == Friendship.Status.ACCEPTED
        return Response({
            'user_id': profile.user.id,
            'username': profile.user.username,
            'gamertag': profile.gamertag,
            'display_name': profile.display_name,
            'avatar_url': profile.avatar_url,
            'is_public': profile.is_public,
            'relation_status': relation_status,
            'is_friend': is_friend
        })
    except UserProfile.DoesNotExist:
        return Response({'error': 'Gamertag introuvable'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Search gamertag error: {e}")
        return Response({'error': 'Erreur lors de la recherche'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def delete_friend(request, user_id):
    """
    Supprime l'amitié entre l'utilisateur connecté et l'utilisateur cible
    """
    try:
        from django.contrib.auth.models import User
        from .models import Friendship
        target = User.objects.get(id=user_id)
        friendship = Friendship.objects.filter(
            models.Q(requester=request.user, addressee=target) |
            models.Q(requester=target, addressee=request.user),
            status=Friendship.Status.ACCEPTED
        ).first()
        if not friendship:
            return Response({'error': 'Amitié introuvable'}, status=status.HTTP_404_NOT_FOUND)
        friendship.delete()
        return Response({'success': True})
    except User.DoesNotExist:
        return Response({'error': 'Utilisateur introuvable'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Delete friend error: {e}")
        return Response({'error': 'Erreur lors de la suppression'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def get_friends_list(request):
    """
    Récupère la liste des amis de l'utilisateur
    """
    try:
        from .models import Friendship, UserProfile
        
        friends = Friendship.get_friends(request.user)
        compatibility_service = CompatibilityService()
        
        friends_data = []
        for friend in friends:
            try:
                profile = friend.profile
                compatibility = compatibility_service.calculate_friend_compatibility(request.user, friend)
                friends_data.append({
                    'user_id': friend.id,
                    'username': friend.username,
                    'gamertag': profile.gamertag,
                    'display_name': profile.display_name,
                    'avatar_url': profile.avatar_url,
                    'compatibility_score': compatibility
                })
            except UserProfile.DoesNotExist:
                # Créer un profil si il n'existe pas
                profile = UserProfile.objects.create(user=friend)
                compatibility = compatibility_service.calculate_friend_compatibility(request.user, friend)
                friends_data.append({
                    'user_id': friend.id,
                    'username': friend.username,
                    'gamertag': profile.gamertag,
                    'display_name': profile.display_name,
                    'avatar_url': profile.avatar_url,
                    'compatibility_score': compatibility
                })
        
        return Response({
            'friends': friends_data,
            'count': len(friends_data)
        })
        
    except Exception as e:
        logger.error(f"Friends list error: {e}")
        return Response(
            {'error': f'Erreur lors de la récupération des amis: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def get_friend_requests(request):
    """
    Récupère les demandes d'amitié reçues
    """
    try:
        from .models import Friendship, UserProfile
        
        pending_requests = Friendship.objects.filter(
            addressee=request.user,
            status=Friendship.Status.PENDING
        ).select_related('requester').order_by('-created_at')
        
        requests_data = []
        for friendship in pending_requests:
            requester = friendship.requester
            try:
                profile = requester.profile
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=requester)
            
            requests_data.append({
                'friendship_id': friendship.id,
                'requester': {
                    'user_id': requester.id,
                    'username': requester.username,
                    'gamertag': profile.gamertag,
                    'display_name': profile.display_name,
                    'avatar_url': profile.avatar_url
                },
                'created_at': friendship.created_at
            })
        
        return Response({
            'requests': requests_data,
            'count': len(requests_data)
        })
        
    except Exception as e:
        logger.error(f"Friend requests error: {e}")
        return Response(
            {'error': f'Erreur lors de la récupération des demandes: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def respond_friend_request(request, friendship_id):
    """
    Répond à une demande d'amitié (accept/decline)
    """
    try:
        from .models import Friendship
        
        action = request.data.get('action')  # 'accept' ou 'decline'
        
        if action not in ['accept', 'decline']:
            return Response(
                {'error': 'Action invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Récupérer la demande
        try:
            friendship = Friendship.objects.get(
                id=friendship_id,
                addressee=request.user,
                status=Friendship.Status.PENDING
            )
        except Friendship.DoesNotExist:
            return Response(
                {'error': 'Demande d\'amitié introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Traiter l'action
        if action == 'accept':
            friendship.accept()
            status_msg = 'accepted'
        else:
            friendship.decline()
            status_msg = 'declined'
        
        return Response({
            'success': True,
            'friendship_id': friendship.id,
            'action': action,
            'status': status_msg
        })
        
    except Exception as e:
        logger.error(f"Respond friend request error: {e}")
        return Response(
            {'error': f'Erreur lors de la réponse: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def create_versus_match(request):
    """
    Crée un nouveau match versus avec un ami
    """
    try:
        from .match_services import VersusMatchService
        from .models import UserProfile
        
        target_gamertag = request.data.get('target_gamertag')
        rounds = int(request.data.get('rounds', 10))
        
        if not target_gamertag:
            return Response(
                {'error': 'Gamertag de l\'adversaire requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Trouver l'utilisateur cible
        try:
            target_profile = UserProfile.objects.get(gamertag=target_gamertag)
            target_user = target_profile.user
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Utilisateur introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Créer le match via le service
        versus_service = VersusMatchService()
        match = versus_service.create_versus_match(
            challenger=request.user,
            challenged=target_user,
            rounds=rounds
        )
        
        return Response({
            'success': True,
            'match_id': match.id,
            'match_type': match.match_type,
            'total_rounds': match.total_rounds,
            'opponent': {
                'username': target_user.username,
                'gamertag': target_profile.gamertag,
                'display_name': target_profile.display_name
            }
        }, status=status.HTTP_201_CREATED)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Create versus match error: {e}")
        return Response(
            {'error': f'Erreur lors de la création du match: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def get_versus_matches(request):
    """
    Récupère les matchs versus de l'utilisateur
    """
    try:
        from .models import FriendMatch, UserProfile
        
        matches = FriendMatch.objects.filter(
            models.Q(user1=request.user) | models.Q(user2=request.user),
            match_type=FriendMatch.MatchType.VERSUS_CHALLENGE
        ).order_by('-last_activity')
        
        matches_data = []
        for match in matches:
            opponent = match.get_opponent(request.user)
            try:
                opponent_profile = opponent.profile
            except UserProfile.DoesNotExist:
                opponent_profile = UserProfile.objects.create(user=opponent)
            
            matches_data.append({
                'match_id': match.id,
                'opponent': {
                    'username': opponent.username,
                    'gamertag': opponent_profile.gamertag,
                    'display_name': opponent_profile.display_name,
                    'avatar_url': opponent_profile.avatar_url
                },
                'status': match.status,
                'current_round': match.current_round,
                'total_rounds': match.total_rounds,
                'scores': {
                    'your_score': match.get_user_score(request.user),
                    'opponent_score': match.get_user_score(opponent)
                },
                'compatibility_score': match.compatibility_score,
                'last_activity': match.last_activity,
                'is_your_turn': match.sessions.filter(
                    round_number=match.current_round
                ).first() and match.sessions.get(
                    round_number=match.current_round
                ).is_waiting_for_user(request.user) if not match.is_completed() else False
            })
        
        return Response({
            'matches': matches_data,
            'count': len(matches_data)
        })
        
    except Exception as e:
        logger.error(f"Get versus matches error: {e}")
        return Response(
            {'error': f'Erreur lors de la récupération des matchs: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def get_versus_match_session(request, match_id):
    """
    Récupère la session actuelle d'un match versus
    """
    try:
        from .models import FriendMatch
        from .match_services import VersusMatchService
        
        # Vérifier que l'utilisateur participe au match
        try:
            match = FriendMatch.objects.get(
                models.Q(user1=request.user) | models.Q(user2=request.user),
                id=match_id
            )
        except FriendMatch.DoesNotExist:
            return Response(
                {'error': 'Match introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        versus_service = VersusMatchService()
        current_session = versus_service.get_current_session(match)
        
        if not current_session:
            return Response(
                {'error': 'Aucune session active'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'session_id': current_session.id,
            'round_number': current_session.round_number,
            'content': {
                'external_id': current_session.content_external_id,
                'type': current_session.content_type,
                'source': current_session.content_source,
                'title': current_session.content_title,
                'metadata': current_session.content_metadata
            },
            'your_choice': current_session.get_user_choice(request.user),
            'is_completed': current_session.is_completed,
            'is_match': current_session.is_match if current_session.is_completed else None,
            'match_progress': {
                'current_round': match.current_round,
                'total_rounds': match.total_rounds,
                'scores': {
                    'your_score': match.get_user_score(request.user),
                    'opponent_score': match.get_user_score(match.get_opponent(request.user))
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Get versus session error: {e}")
        return Response(
            {'error': f'Erreur lors de la récupération de la session: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def submit_versus_choice(request, match_id):
    """
    Enregistre le choix d'un utilisateur pour la session actuelle d'un match versus
    """
    try:
        from .models import FriendMatch
        from .match_services import VersusMatchService
        
        choice = request.data.get('choice')  # liked, disliked, skipped
        
        if choice not in ['liked', 'disliked', 'skipped']:
            return Response(
                {'error': 'Choix invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier que l'utilisateur participe au match
        try:
            match = FriendMatch.objects.get(
                models.Q(user1=request.user) | models.Q(user2=request.user),
                id=match_id
            )
        except FriendMatch.DoesNotExist:
            return Response(
                {'error': 'Match introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        versus_service = VersusMatchService()
        result = versus_service.submit_choice(match, request.user, choice)
        
        if 'error' in result:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(result)
        
    except Exception as e:
        logger.error(f"Submit versus choice error: {e}")
        return Response(
            {'error': f'Erreur lors de l\'enregistrement du choix: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([ScopedRateThrottle])
def get_versus_match_results(request, match_id):
    """
    Récupère les résultats complets d'un match versus terminé
    """
    try:
        from .models import FriendMatch
        from .match_services import VersusMatchService
        
        # Vérifier que l'utilisateur participe au match
        try:
            match = FriendMatch.objects.get(
                models.Q(user1=request.user) | models.Q(user2=request.user),
                id=match_id
            )
        except FriendMatch.DoesNotExist:
            return Response(
                {'error': 'Match introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        versus_service = VersusMatchService()
        results = versus_service.get_match_results(match)
        
        return Response(results)
        
    except Exception as e:
        logger.error(f"Get versus results error: {e}")
        return Response(
            {'error': f'Erreur lors de la récupération des résultats: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_config(request):
    """
    Endpoint de configuration pour le frontend
    Expose les feature flags, informations de build et version
    """
    import os
    import logging
    from datetime import datetime
    from django.conf import settings
    from .services.feature_flags_service import FeatureFlagsService
    
    # Initialiser le logger au niveau module pour fiabilité
    logger = logging.getLogger(__name__)
    
    # Feature flags depuis la base de données avec fallback
    default_feature_flags = {
        'social_profile': True,
        'friend_system': True,
        'versus_match': True,
        'external_apis': True,
        'recommendations': True
    }
    
    try:
        # Récupérer les feature flags depuis le service (cache + DB)
        db_feature_flags = FeatureFlagsService.get_all_flags()
        
        # Fusionner avec les defaults (les flags de la DB priment)
        feature_flags = {**default_feature_flags, **db_feature_flags}
        
        # Fallback vers settings si la DB est vide
        if not db_feature_flags:
            feature_flags = getattr(settings, 'FEATURE_FLAGS', default_feature_flags)
            
    except Exception as e:
        logger.error(f"Error loading feature flags: {e}")
        # En cas d'erreur, utiliser les defaults
        feature_flags = getattr(settings, 'FEATURE_FLAGS', default_feature_flags)
    
    # Information de build
    build_info = {
        'hash': os.environ.get('GIT_SHA', 'unknown'),
        'timestamp': datetime.now().isoformat()
    }
    
    # Version de l'API
    api_version = '1.0.0'
    
    config_data = {
        'feature_flags': feature_flags,
        'build': build_info,
        'version': api_version
    }
    
    response = Response(config_data, status=status.HTTP_200_OK)
    
    # Ajouter les headers de cache (max-age de 60 secondes)
    response['Cache-Control'] = 'public, max-age=60'
    
    return response

# -----------------------------------------------------------
# Association explicite des scopes de throttling (issue #27)
# -----------------------------------------------------------
# Attribution explicite des scopes de throttling (issue #27)
_throttle_scopes = {
    'register_user': 'register',
    'search_items': 'search',
    'get_suggestions': 'search',
    'quick_add_item': 'match_action',
    'get_match_recommendations': 'match_action',
    'submit_match_action': 'match_action',
    # External / enrichment
    'search_external': 'external',
    'get_trending_external': 'external',
    'import_from_external': 'external',
    'get_external_details': 'external',
    'enrich_list_item': 'external',
    'get_trending_suggestions': 'external',
    'get_similar_suggestions': 'external',
}
for func_name, scope in _throttle_scopes.items():
    func = globals().get(func_name)
    if func is not None:
        setattr(func, 'throttle_scope', scope)