from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import List, ListItem, ExternalReference, VersusMatch, VersusParticipant, VersusRound, VersusVote

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


class VersusParticipantSerializer(serializers.ModelSerializer):
    """Serializer pour les participants d'un match versus"""
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    
    class Meta:
        model = VersusParticipant
        fields = ('user_id', 'username', 'score', 'joined_at')
        read_only_fields = ('user_id', 'username', 'score', 'joined_at')


class VersusRoundItemSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour les éléments dans un round"""
    external_ref = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = ListItem
        fields = ('id', 'title', 'description', 'external_ref')
    
    def get_external_ref(self, obj):
        """Récupère les données de référence externe filtrées"""
        if hasattr(obj, 'external_ref'):
            return {
                'poster_url': obj.external_ref.poster_url,
                'rating': obj.external_ref.rating,
                'source': obj.external_ref.external_source
            }
        return None


class VersusRoundSerializer(serializers.ModelSerializer):
    """Serializer pour un round de versus"""
    item1 = VersusRoundItemSerializer(read_only=True)
    item2 = VersusRoundItemSerializer(read_only=True)
    winner_item = VersusRoundItemSerializer(read_only=True)
    votes_count = serializers.SerializerMethodField(read_only=True)
    user_vote = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = VersusRound
        fields = ('id', 'round_number', 'status', 'item1', 'item2', 'winner_item', 
                 'votes_count', 'user_vote', 'created_at', 'completed_at')
        read_only_fields = ('id', 'created_at', 'completed_at')
    
    def get_votes_count(self, obj):
        """Compte les votes pour chaque élément"""
        return {
            'item1': obj.votes.filter(chosen_item=obj.item1).count(),
            'item2': obj.votes.filter(chosen_item=obj.item2).count(),
            'total': obj.votes.count()
        }
    
    def get_user_vote(self, obj):
        """Récupère le vote de l'utilisateur actuel pour ce round"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                participant = obj.match.participants.get(user=request.user)
                vote = obj.votes.filter(participant=participant).first()
                if vote:
                    return vote.chosen_item.id
            except VersusParticipant.DoesNotExist:
                pass
        return None


class VersusMatchStateSerializer(serializers.ModelSerializer):
    """Serializer pour l'état d'un match versus avec filtrage sécurisé"""
    participants = VersusParticipantSerializer(many=True, read_only=True)
    current_round_data = serializers.SerializerMethodField(read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    can_vote = serializers.SerializerMethodField(read_only=True)
    is_participant = serializers.SerializerMethodField(read_only=True)
    participants_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = VersusMatch
        fields = ('id', 'category', 'category_display', 'status', 'status_display',
                 'current_round', 'max_rounds', 'completed', 'participants',
                 'current_round_data', 'can_vote', 'is_participant', 'participants_count',
                 'created_at', 'updated_at', 'completed_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'completed_at')
    
    def get_current_round_data(self, obj):
        """Récupère les données du round actuel"""
        if obj.status == VersusMatch.Status.ACTIVE:
            current_round = obj.rounds.filter(round_number=obj.current_round).first()
            if current_round:
                return VersusRoundSerializer(current_round, context=self.context).data
        return None
    
    def get_can_vote(self, obj):
        """Vérifie si l'utilisateur peut voter dans le round actuel"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        # Vérifier si l'utilisateur est participant
        if not obj.is_participant(request.user):
            return False
        
        # Vérifier si le match est actif
        if obj.status != VersusMatch.Status.ACTIVE:
            return False
        
        # Vérifier s'il y a un round actuel et si l'utilisateur n'a pas encore voté
        current_round = obj.rounds.filter(round_number=obj.current_round, status=VersusRound.Status.ACTIVE).first()
        if current_round:
            try:
                participant = obj.participants.get(user=request.user)
                return not current_round.votes.filter(participant=participant).exists()
            except VersusParticipant.DoesNotExist:
                pass
        
        return False
    
    def get_is_participant(self, obj):
        """Vérifie si l'utilisateur actuel est participant au match"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_participant(request.user)
        return False
    
    def get_participants_count(self, obj):
        """Retourne le nombre de participants"""
        return obj.participants.count()
    
    def to_representation(self, instance):
        """Filtre les données selon les permissions de l'utilisateur"""
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        # Si l'utilisateur n'est pas participant, filtrer certaines informations sensibles
        if not self.get_is_participant(instance):
            # Retirer les détails complets des participants (garder seulement username et score)
            if 'participants' in data:
                filtered_participants = []
                for participant in data['participants']:
                    filtered_participants.append({
                        'username': participant['username'],
                        'score': participant['score']
                    })
                data['participants'] = filtered_participants
            
            # Retirer les détails de vote du round actuel si non participant
            if data.get('current_round_data'):
                current_round = data['current_round_data']
                if 'user_vote' in current_round:
                    del current_round['user_vote']
        
        return data
