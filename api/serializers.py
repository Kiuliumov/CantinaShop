from rest_framework import serializers

from api.models import ChatMessage
from products.models import Product, Category


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    from_admin = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ['id', 'message', 'sender_id', 'sender_username', 'avatar_url', 'timestamp', 'from_admin']

    def get_sender_username(self, obj):
        request = self.context.get('request')
        if request and (request.user.is_staff or request.user.is_superuser):
            return "Admin" if obj.sender.is_staff or obj.sender.is_superuser else obj.sender.username
        return obj.sender.username

    def get_avatar_url(self, obj):
        from django.templatetags.static import static
        request = self.context.get('request')

        if obj.sender.is_staff or obj.sender.is_superuser:
            url = static('images/admin.jpg')
        else:
            url = getattr(obj.sender.account, 'profile_picture_url', '') or static('images/avatar.png')

        if request:
            return request.build_absolute_uri(url)
        return url

    def get_from_admin(self, obj):
        return obj.sender.is_staff or obj.sender.is_superuser

class ProductSerializer(serializers.ModelSerializer):
    average_rating = serializers.FloatField(read_only=True)
    rating_count = serializers.IntegerField(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_name_input = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'is_available', 'image_url',
            'slug', 'has_discount', 'created_at', 'updated_at',
            'category', 'category_name', 'category_name_input',
            'average_rating', 'rating_count',
        ]
        extra_kwargs = {
            'category': {'required': False, 'allow_null': True}
        }

    def validate(self, attrs):
        category = attrs.get('category', None)
        category_name = attrs.get('category_name_input', '').strip()

        if not category and not category_name:
            raise serializers.ValidationError("Provide either a category ID or a category_name_input.")

        return attrs

    def create(self, validated_data):
        category_name = validated_data.pop('category_name_input', '').strip()
        if category_name and not validated_data.get('category'):
            category, _ = Category.objects.get_or_create(name=category_name)
            validated_data['category'] = category
        return super().create(validated_data)

    def update(self, instance, validated_data):
        category_name = validated_data.pop('category_name_input', '').strip()
        if category_name and not validated_data.get('category'):
            category, _ = Category.objects.get_or_create(name=category_name)
            validated_data['category'] = category
        return super().update(instance, validated_data)