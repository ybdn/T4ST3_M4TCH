from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import List, ListItem, ExternalReference, VersusMatch, VersusRound, VersusChoice

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
        return {
            'source': external.external_source,
            'poster_url': external.poster_url,
            'backdrop_url': external.backdrop_url,
            'rating': external.rating,
            'release_date': external.release_date,
            'metadata': external.metadata,
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


class VersusChoiceSerializer(serializers.ModelSerializer):
    """Serializer pour les choix dans un round versus"""
    player_name = serializers.CharField(source='player.username', read_only=True)
    chosen_item_title = serializers.CharField(source='chosen_item.title', read_only=True)
    
    class Meta:
        model = VersusChoice
        fields = ('id', 'player', 'player_name', 'chosen_item', 'chosen_item_title', 'created_at')
        read_only_fields = ('id', 'created_at')


class VersusRoundSerializer(serializers.ModelSerializer):
    """Serializer pour les rounds versus"""
    item1_data = ListItemSerializer(source='item1', read_only=True)
    item2_data = ListItemSerializer(source='item2', read_only=True)
    choices = VersusChoiceSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = VersusRound
        fields = (
            'id', 'round_number', 'item1', 'item2', 'item1_data', 'item2_data',
            'status', 'status_display', 'choices', 'created_at', 'completed_at'
        )
        read_only_fields = ('id', 'created_at', 'completed_at')


class VersusMatchSerializer(serializers.ModelSerializer):
    """Serializer pour les matchs versus"""
    player1_name = serializers.CharField(source='player1.username', read_only=True)
    player2_name = serializers.CharField(source='player2.username', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    current_round_data = serializers.SerializerMethodField()
    winner = serializers.SerializerMethodField()
    
    class Meta:
        model = VersusMatch
        fields = (
            'id', 'player1', 'player1_name', 'player2', 'player2_name',
            'category', 'category_display', 'status', 'status_display',
            'current_round', 'total_rounds', 'player1_score', 'player2_score',
            'current_round_data', 'winner', 'created_at', 'updated_at', 'completed_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'completed_at')
    
    def get_current_round_data(self, obj):
        """Retourne les données du round actuel"""
        current_round = obj.get_current_round_obj()
        if current_round:
            return VersusRoundSerializer(current_round).data
        return None
    
    def get_winner(self, obj):
        """Retourne le gagnant du match"""
        winner = obj.get_winner()
        if winner:
            return {'id': winner.id, 'username': winner.username}
        return None


class VersusChoiceSubmissionSerializer(serializers.Serializer):
    """Serializer pour soumettre un choix dans un round"""
    chosen_item_id = serializers.IntegerField()
    
    def validate_chosen_item_id(self, value):
        """Valide que l'élément choisi existe"""
        try:
            ListItem.objects.get(id=value)
        except ListItem.DoesNotExist:
            raise serializers.ValidationError("L'élément choisi n'existe pas")
        return value
