from rest_framework.decorators import api_view, permission_classes, action
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
import json
import hashlib
import logging

logger = logging.getLogger(__name__)

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

@api_view(['GET'])
@permission_classes([AllowAny])
def sentry_test_error(request):
    """
    Test endpoint to generate an error for Sentry monitoring validation.
    """
    logger.info("Sentry test error endpoint called")
    raise Exception("Test error for Sentry integration - this is intentional for monitoring purposes")

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

        # Enrichissement automatique après création (best-effort, non bloquant)
        try:
            created_item = serializer.instance
            if created_item and created_item.list.category in ['FILMS', 'SERIES', 'MUSIQUE', 'LIVRES']:
                enrichment_service = ExternalEnrichmentService()
                enrichment_service.enrich_list_item(created_item, force_refresh=False)
        except Exception:
            # Ne pas bloquer la création en cas d'erreur d'enrichissement
            pass


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
        
        # Enrichissement automatique (best-effort)
        try:
            enrichment_service = ExternalEnrichmentService()
            enrichment_service.enrich_list_item(new_item, force_refresh=False)
        except Exception:
            pass

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