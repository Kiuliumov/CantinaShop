from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import ChatMessageSerializer, ProductSerializer, CategorySerializer
from api.models import ChatMessage
from products.models import Product, Category


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
        messages_qs = messages_qs[:limit]

        serializer = ChatMessageSerializer(messages_qs, many=True, context={'request': request})

        return Response({'messages': serializer.data})


class ProductListCreateAPIView(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

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



class CategoryListCreateAPIView(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]