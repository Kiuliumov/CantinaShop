from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import ChatMessageSerializer
from api.models import ChatMessage


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