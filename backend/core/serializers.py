from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import List, ListItem

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
    class Meta:
        model = ListItem
        fields = ('id', 'title', 'description', 'position', 'list', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si on est dans un contexte de route imbriquée, exclure le champ list
        request = self.context.get('request')
        if request and hasattr(request, 'resolver_match'):
            url_name = request.resolver_match.url_name
            if url_name and 'list-items' in url_name:
                self.fields.pop('list', None)


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
