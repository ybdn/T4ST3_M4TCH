from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import List, ListItem, ExternalReference, BetaInvite

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
    beta_token = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Token d'invitation bêta"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'beta_token')

    def validate_beta_token(self, value):
        """Valide le token d'invitation bêta"""
        invitation = BetaInvite.validate_token(value)
        if not invitation:
            raise serializers.ValidationError("Token d'invitation invalide ou expiré.")
        return value

    def validate_email(self, value):
        """Valide que l'email correspond à celui de l'invitation"""
        beta_token = self.initial_data.get('beta_token')
        if beta_token:
            invitation = BetaInvite.validate_token(beta_token)
            if invitation and invitation.email.lower() != value.lower():
                raise serializers.ValidationError(
                    "L'email doit correspondre à celui de l'invitation."
                )
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Pop the confirmation password field as it's not part of the User model
        attrs.pop('password2')
        return attrs

    def create(self, validated_data):
        beta_token = validated_data.pop('beta_token')
        invitation = BetaInvite.validate_token(beta_token)
        
        if not invitation:
            raise serializers.ValidationError("Token d'invitation invalide.")
        
        # Créer l'utilisateur
        user = User.objects.create_user(**validated_data)
        
        # Marquer l'invitation comme utilisée
        invitation.mark_as_used(user)
        
        return user


class BetaInviteSerializer(serializers.ModelSerializer):
    """Serializer pour les invitations bêta (usage administratif)"""
    
    class Meta:
        model = BetaInvite
        fields = (
            'id', 'email', 'token', 'created_at', 'expires_at', 
            'used_at', 'used_by', 'created_by', 'notes',
            'is_expired', 'is_used', 'is_valid'
        )
        read_only_fields = (
            'id', 'token', 'created_at', 'used_at', 'used_by', 
            'is_expired', 'is_used', 'is_valid'
        )


class ValidateInviteSerializer(serializers.Serializer):
    """Serializer pour valider une invitation sans créer d'utilisateur"""
    token = serializers.CharField(required=True)
    
    def validate_token(self, value):
        invitation = BetaInvite.validate_token(value)
        if not invitation:
            raise serializers.ValidationError("Token d'invitation invalide ou expiré.")
        return value


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
