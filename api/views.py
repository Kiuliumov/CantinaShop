import secrets
from datetime import timedelta

from django.utils.timezone import now, localtime
from rest_framework import status
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from api.authentication import APIKeyAuthentication
from api.serializers import ChatMessageSerializer, ProductSerializer
from api.models import ChatMessage, APIKey
from common.mixins import AdminRequiredMixin
from products.models import Product

class ChatMessagesAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id, **kwargs):
        UserModel = get_user_model()
        user = get_object_or_404(UserModel, id=user_id)


        if not request.user.is_superuser and not request.user.is_staff and user.id != request.user.id:
            raise PermissionDenied

        admins = UserModel.objects.filter(Q(is_staff=True) | Q(is_superuser=True))
        messages_qs = (ChatMessage.objects.filter(
            Q(sender=user, recipient__in=admins) |
            Q(sender__in=admins, recipient=user)
        ).order_by('timestamp'))

        limit = request.GET.get('limit', 100)
        try:
            limit = int(limit)
            if limit <= 0:
                limit = 100
        except ValueError:
            limit = 100

        messages_qs = messages_qs.order_by('-timestamp')[:limit]
        messages_qs = messages_qs.reverse()

        serializer = ChatMessageSerializer(messages_qs, many=True, context={'request': request})

        return Response({'messages': serializer.data})


class ProductListCreateAPIView(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [APIKeyAuthentication, SessionAuthentication]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]

    def get(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())

        product_id = request.GET.get('id')
        if product_id:
            qs = qs.filter(id=product_id)

        search = request.GET.get('search')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))

        category_id = request.GET.get('category')
        if category_id:
            qs = qs.filter(category__id=category_id)

        availability = request.GET.get('availability')
        if availability == 'available':
            qs = qs.filter(is_available=True)
        elif availability == 'unavailable':
            qs = qs.filter(is_available=False)

        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        try:
            if min_price:
                qs = qs.filter(price__gte=float(min_price))
            if max_price:
                qs = qs.filter(price__lte=float(max_price))
        except ValueError:
            pass

        sort = request.GET.get('sort')
        if sort == 'name_asc':
            qs = qs.order_by('name')
        elif sort == 'name_desc':
            qs = qs.order_by('-name')
        elif sort == 'price_asc':
            qs = qs.order_by('price')
        elif sort == 'price_desc':
            qs = qs.order_by('-price')
        else:
            qs = qs.order_by('-created_at')

        limit = request.GET.get('limit', 50)
        try:
            limit = int(limit)
            if limit <= 0:
                limit = 50
        except ValueError:
            limit = 50

        qs = qs[:limit]

        serializer = self.get_serializer(qs, many=True)
        return Response({'products': serializer.data})

class ProductDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [APIKeyAuthentication, SessionAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

class GenerateAPIKeyAPIView(AdminRequiredMixin, APIView):
    """
    Generate a new API key for the authenticated admin user,
    only once per day.
    """

    def post(self, request, *args, **kwargs):
        user = request.user
        today = localtime(now()).date()

        existing_key = APIKey.objects.filter(
            user=user,
            created_at__date=today
        ).first()

        if existing_key:
            return Response({
                'detail': 'You can only generate one API key per day.',
                'api_key': existing_key.key,
                'expires_at': existing_key.expires_at,
                'user': user.username,
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        new_key = secrets.token_hex(20)
        expiry = now() + timedelta(days=30)

        api_key_obj = APIKey.objects.create(
            user=user,
            key=new_key,
            expires_at=expiry,
        )

        return Response({
            'api_key': new_key,
            'expires_at': expiry,
            'user': user.username,
        }, status=status.HTTP_201_CREATED)