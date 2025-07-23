from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import ChatMessageSerializer, ProductSerializer
from api.models import ChatMessage
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
        messages_qs = messages_qs[:limit]

        serializer = ChatMessageSerializer(messages_qs, many=True, context={'request': request})

        return Response({'messages': serializer.data})


class ProductListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        qs = Product.objects.filter(is_available=True)  # default filter, you can remove if you want all

        category_name = request.GET.get('category')
        if category_name:
            qs = qs.filter(category__name__iexact=category_name)

        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        if min_price:
            try:
                min_price = float(min_price)
                qs = qs.filter(price__gte=min_price)
            except ValueError:
                pass
        if max_price:
            try:
                max_price = float(max_price)
                qs = qs.filter(price__lte=max_price)
            except ValueError:
                pass

        is_available = request.GET.get('is_available')
        if is_available is not None:
            if is_available.lower() in ['true', '1']:
                qs = qs.filter(is_available=True)
            elif is_available.lower() in ['false', '0']:
                qs = qs.filter(is_available=False)

        limit = request.GET.get('limit', 50)
        try:
            limit = int(limit)
            if limit <= 0:
                limit = 50
        except ValueError:
            limit = 50

        qs = qs.order_by('-created_at')[:limit]

        serializer = ProductSerializer(qs, many=True, context={'request': request})
        return Response({'products': serializer.data})