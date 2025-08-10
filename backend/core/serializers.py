from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import List, ListItem, ExternalReference
import logging

logger = logging.getLogger(__name__)


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=150,
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    )
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        help_text="Required. A valid email address."
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text="Required. Your password can't be too similar to your other personal information."
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        style={'input_type': 'password'},
        label="Confirm password",
        help_text="Required. Enter the same password as before, for verification."
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate_username(self, value):
        """Validate username field."""
        if not value or not value.strip():
            logger.debug(f"Invalid username validation: empty or whitespace-only: '{value}'")
            raise serializers.ValidationError("Username cannot be empty or contain only whitespace.")
        
        # Check if username already exists
        if User.objects.filter(username=value).exists():
            logger.debug(f"Username validation failed: '{value}' already exists")
            raise serializers.ValidationError("A user with that username already exists.")
        
        return value.strip()

    def validate_email(self, value):
        """Validate email field."""
        if not value or not value.strip():
            logger.debug(f"Invalid email validation: empty or whitespace-only: '{value}'")
            raise serializers.ValidationError("Email cannot be empty or contain only whitespace.")
        
        # Additional email validation can be added here
        return value.strip().lower()

    def validate_password(self, value):
        """Validate password field."""
        if not value:
            logger.debug("Password validation failed: empty password")
            raise serializers.ValidationError("Password cannot be empty.")
        return value

    def validate_password2(self, value):
        """Validate password confirmation field."""
        if not value:
            logger.debug("Password confirmation validation failed: empty")
            raise serializers.ValidationError("Password confirmation cannot be empty.")
        return value

    def validate(self, attrs):
        """Cross-field validation."""
        password = attrs.get('password')
        password2 = attrs.get('password2')
        
        if password != password2:
            logger.debug("Password validation failed: passwords don't match")
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Pop the confirmation password field as it's not part of the User model
        attrs.pop('password2')
        return attrs

    def create(self, validated_data):
        """Create a new user."""
        user = User.objects.create_user(**validated_data)
        return user


class ListItemSerializer(serializers.ModelSerializer):
    external_ref = serializers.SerializerMethodField(read_only=True)
    title = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=200,
        help_text="Required. The title of the list item (max 200 characters)."
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional description or comment about the item."
    )
    position = serializers.IntegerField(
        required=False,
        min_value=0,
        help_text="Position in the list (auto-generated if not provided)."
    )
    is_watched = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Whether the item has been watched/read."
    )
    
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

    def validate_title(self, value):
        """Validate title field."""
        if not value or not value.strip():
            logger.debug(f"Invalid title validation: empty or whitespace-only: '{value}'")
            raise serializers.ValidationError("Title cannot be empty or contain only whitespace.")
        
        if len(value.strip()) > 200:
            logger.debug(f"Title validation failed: too long ({len(value.strip())} characters)")
            raise serializers.ValidationError("Title cannot exceed 200 characters.")
        
        return value.strip()

    def validate_position(self, value):
        """Validate position field."""
        if value is not None and value < 0:
            logger.debug(f"Position validation failed: negative value {value}")
            raise serializers.ValidationError("Position must be a non-negative integer.")
        return value

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
    name = serializers.CharField(
        required=False,  # Optional because defaults are provided
        allow_blank=True,
        max_length=100,
        help_text="Name of the list (auto-generated if not provided)."
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Description of the list (auto-generated if not provided)."
    )
    category = serializers.ChoiceField(
        choices=List.Category.choices,
        required=True,
        help_text=f"Required. Must be one of: {', '.join([choice[0] for choice in List.Category.choices])}"
    )
    
    class Meta:
        model = List
        fields = ('id', 'name', 'description', 'category', 'category_display', 'owner', 'items', 'items_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'owner', 'created_at', 'updated_at')
    
    def validate_name(self, value):
        """Validate name field."""
        if value and len(value.strip()) > 100:
            logger.debug(f"List name validation failed: too long ({len(value.strip())} characters)")
            raise serializers.ValidationError("List name cannot exceed 100 characters.")
        return value.strip() if value else value

    def validate_category(self, value):
        """Validate category field."""
        if not value:
            logger.debug("Category validation failed: empty category")
            raise serializers.ValidationError("Category is required.")
        
        valid_choices = [choice[0] for choice in List.Category.choices]
        if value not in valid_choices:
            logger.debug(f"Category validation failed: '{value}' not in {valid_choices}")
            raise serializers.ValidationError(
                f"Invalid category. Must be one of: {', '.join(valid_choices)}"
            )
        return value
    
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


class QuickAddItemSerializer(serializers.Serializer):
    """Serializer for quick add item endpoint."""
    title = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=200,
        help_text="Required. The title of the item to add."
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional description of the item."
    )
    category = serializers.ChoiceField(
        choices=List.Category.choices,
        required=True,
        help_text=f"Required. Must be one of: {', '.join([choice[0] for choice in List.Category.choices])}"
    )

    def validate_title(self, value):
        """Validate title field."""
        if not value or not value.strip():
            logger.debug(f"Quick add title validation failed: empty or whitespace-only: '{value}'")
            raise serializers.ValidationError("Title cannot be empty or contain only whitespace.")
        return value.strip()

    def validate_category(self, value):
        """Validate category field."""
        if not value:
            logger.debug("Quick add category validation failed: empty category")
            raise serializers.ValidationError("Category is required.")
        
        valid_choices = [choice[0] for choice in List.Category.choices]
        if value not in valid_choices:
            logger.debug(f"Quick add category validation failed: '{value}' not in {valid_choices}")
            raise serializers.ValidationError(
                f"Invalid category. Must be one of: {', '.join(valid_choices)}"
            )
        return value


class ImportExternalSerializer(serializers.Serializer):
    """Serializer for external import endpoint."""
    external_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=100,
        help_text="Required. The external ID from the source API."
    )
    source = serializers.ChoiceField(
        choices=ExternalReference.Source.choices,
        required=True,
        help_text=f"Required. Must be one of: {', '.join([choice[0] for choice in ExternalReference.Source.choices])}"
    )
    category = serializers.ChoiceField(
        choices=List.Category.choices,
        required=True,
        help_text=f"Required. Must be one of: {', '.join([choice[0] for choice in List.Category.choices])}"
    )

    def validate_external_id(self, value):
        """Validate external_id field."""
        if not value or not value.strip():
            logger.debug(f"External ID validation failed: empty or whitespace-only: '{value}'")
            raise serializers.ValidationError("External ID cannot be empty or contain only whitespace.")
        return value.strip()

    def validate_source(self, value):
        """Validate source field."""
        if not value:
            logger.debug("External import source validation failed: empty source")
            raise serializers.ValidationError("Source is required.")
        
        valid_choices = [choice[0] for choice in ExternalReference.Source.choices]
        if value not in valid_choices:
            logger.debug(f"External import source validation failed: '{value}' not in {valid_choices}")
            raise serializers.ValidationError(
                f"Invalid source. Must be one of: {', '.join(valid_choices)}"
            )
        return value

    def validate_category(self, value):
        """Validate category field."""
        if not value:
            logger.debug("External import category validation failed: empty category")
            raise serializers.ValidationError("Category is required.")
        
        valid_choices = [choice[0] for choice in List.Category.choices]
        if value not in valid_choices:
            logger.debug(f"External import category validation failed: '{value}' not in {valid_choices}")
            raise serializers.ValidationError(
                f"Invalid category. Must be one of: {', '.join(valid_choices)}"
            )
        return value
