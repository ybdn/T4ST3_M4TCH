from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import List, ListItem, ExternalReference, UserPreference, UserProfile, Friendship

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label="Confirm password"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Pop the confirmation password field as it's not part of the User model
        attrs.pop('password2')
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ListItemSerializer(serializers.ModelSerializer):
    external_ref = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = ListItem
        fields = ('id', 'title', 'description', 'position', 'list', 'is_watched', 'created_at', 'updated_at', 'external_ref')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si on est dans un contexte de route imbriquée, exclure le champ list
        request = self.context.get('request')
        if request and hasattr(request, 'resolver_match'):
            url_name = request.resolver_match.url_name
            if url_name and 'list-items' in url_name:
                self.fields.pop('list', None)

    def get_external_ref(self, obj):
        external = getattr(obj, 'external_ref', None)
        if not external:
            return None
        
        # Normaliser les données pour une structure cohérente
        metadata = external.metadata or {}
        
        # Extraire les informations principales avec fallbacks
        poster_url = external.poster_url or metadata.get('poster_url')
        backdrop_url = external.backdrop_url or metadata.get('backdrop_url')
        rating = external.rating or metadata.get('vote_average') or metadata.get('rating')
        release_date = external.release_date or metadata.get('release_date') or metadata.get('first_air_date')
        
        # Normaliser les genres
        genres = []
        if metadata.get('genres'):
            if isinstance(metadata['genres'], list):
                # Si c'est une liste d'objets avec 'name'
                if metadata['genres'] and isinstance(metadata['genres'][0], dict):
                    genres = [g.get('name', g) for g in metadata['genres'] if g]
                else:
                    # Si c'est une liste de strings
                    genres = [str(g) for g in metadata['genres']]
            elif isinstance(metadata['genres'], str):
                genres = [metadata['genres']]
        
        # Normaliser la description/overview
        overview = (metadata.get('overview') or 
                   metadata.get('description') or 
                   metadata.get('summary') or 
                   obj.description)
        
        # Extraire l'année de la date de sortie
        year = None
        if release_date:
            if isinstance(release_date, str) and len(release_date) >= 4:
                year = int(release_date[:4])
            elif hasattr(release_date, 'year'):
                year = release_date.year
        
        return {
            'source': external.external_source,
            'external_id': external.external_id,
            'poster_url': poster_url,
            'backdrop_url': backdrop_url,
            'rating': rating,
            'release_date': str(release_date) if release_date else None,
            'year': year,
            'genres': genres,
            'overview': overview,
            'metadata': metadata,  # Garder les métadonnées complètes pour référence
        }


class ListSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    items = ListItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = List
        fields = ('id', 'name', 'description', 'category', 'category_display', 'owner', 'items', 'items_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'owner', 'created_at', 'updated_at')
    
    def get_items_count(self, obj):
        return obj.items.count()
    
    def create(self, validated_data):
        # Automatically set the owner to the current user
        validated_data['owner'] = self.context['request'].user
        
        # Si pas de nom fourni, utiliser le nom par défaut
        if not validated_data.get('name'):
            validated_data['name'] = List.get_default_name(validated_data['category'])
        
        # Si pas de description fournie, utiliser la description par défaut
        if not validated_data.get('description'):
            validated_data['description'] = List.get_default_description(validated_data['category'])
        
        return super().create(validated_data)


class MatchActionSerializer(serializers.Serializer):
    """Serializer pour valider une action utilisateur sur une recommandation.
    Accepte des alias front: category -> content_type, like->liked, dislike->disliked, add->added.
    """
    external_id = serializers.CharField(max_length=100)
    source = serializers.ChoiceField(choices=UserPreference.Source.choices)
    # Le front envoie "category"; on accepte aussi content_type.
    content_type = serializers.ChoiceField(choices=UserPreference.ContentType.choices, required=False)
    category = serializers.ChoiceField(choices=UserPreference.ContentType.choices, required=False)
    action = serializers.CharField(max_length=20)
    title = serializers.CharField(max_length=200)
    metadata = serializers.JSONField(required=False, default=dict)
    description = serializers.CharField(required=False, allow_blank=True)
    poster_url = serializers.CharField(required=False, allow_blank=True)

    ACTION_ALIASES = {
        'like': UserPreference.Action.LIKED,
        'liked': UserPreference.Action.LIKED,
        'dislike': UserPreference.Action.DISLIKED,
        'disliked': UserPreference.Action.DISLIKED,
        'add': UserPreference.Action.ADDED,
        'added': UserPreference.Action.ADDED,
        'skip': UserPreference.Action.SKIPPED,
        'skipped': UserPreference.Action.SKIPPED,
    }

    def validate(self, attrs):
        # Harmoniser content_type à partir de category si fourni
        content_type = attrs.get('content_type') or attrs.get('category')
        if not content_type:
            raise serializers.ValidationError({'content_type': 'Champ requis (alias category accepté).'})
        attrs['content_type'] = content_type
        attrs.pop('category', None)

        # Normaliser action
        raw_action = attrs.get('action')
        normalized = self.ACTION_ALIASES.get(raw_action)
        if not normalized:
            raise serializers.ValidationError({'action': f"Action inconnue: {raw_action}"})
        attrs['action'] = normalized
        return attrs

    def to_internal_value(self, data):
        # Laisser Serializer faire le gros du travail
        return super().to_internal_value(data)

    # Pas de create/update: ce serializer est strictement pour validation d'entrée.


class SocialProfileSerializer(serializers.ModelSerializer):
    """Serializer pour exposer le profil social + statistiques agrégées.
    Fournit friends_count & pending_requests dynamiquement (pas stockés dans UserProfile).
    """
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    stats = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = (
            'user_id', 'username', 'gamertag', 'display_name', 'bio', 'avatar_url',
            'is_public', 'stats', 'created_at'
        )
        read_only_fields = fields

    def get_stats(self, obj):  # type: ignore[override]
        # Comptage des amis acceptés
        friends_count = len(Friendship.get_friends(obj.user))
        # Demandes reçues en attente
        pending_requests = Friendship.objects.filter(
            addressee=obj.user,
            status=Friendship.Status.PENDING
        ).count()
        return {
            'total_matches': obj.total_matches,
            'successful_matches': obj.successful_matches,
            'friends_count': friends_count,
            'pending_requests': pending_requests
        }

