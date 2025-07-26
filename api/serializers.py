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


from rest_framework import serializers

class ProductSerializer(serializers.ModelSerializer):
    average_rating = serializers.FloatField(read_only=True)
    rating_count = serializers.IntegerField(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'is_available', 'image_url',
             'slug', 'has_discount', 'created_at', 'updated_at',
            'category', 'category_name', 'average_rating', 'rating_count',
        ]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']