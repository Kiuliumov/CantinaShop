from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Account
from .models import ChatMessage
from .serializers import ChatMessageSerializer
from common.mixins import AdminRequiredMixin


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
        messages_qs = reversed(messages_qs)

        serializer = ChatMessageSerializer(messages_qs, many=True, context={'request': request})

        return Response({'messages': serializer.data})


class AdminChatHubView(AdminRequiredMixin, TemplateView):
    template_name = 'chat/hub.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = Account.objects.filter(user__is_staff=False, user__is_superuser=False).select_related('user')
        context['admin_avatar_url'] = static('images/admin.jpg')
        return context

class ChatFrontendConfigAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        return Response({
            "userId": user.id,
            "wsProtocol": "wss" if request.is_secure() else "ws",
            "host": request.get_host(),
            "apiMessagesUrl": reverse('chat-messages-api-base', args=[user.id]),
            "adminAvatarUrl": static('images/admin.jpg'),
            "defaultAvatarUrl": static('images/avatar.png'),
            "userIsStaffOrSuperuser": user.is_staff or user.is_superuser,
            "userIsChatBanned": getattr(user, "is_chat_banned", False),
        })


class MarkMessagesReadView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id, *args, **kwargs):
        admin_user = request.user
        ChatMessage.objects.filter(
            sender_id=user_id,
            recipient=admin_user,
            is_read=False
        ).update(is_read=True)
        return Response({'status': 'success'})


class UnreadMessageCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        unread = (
            ChatMessage.objects
            .filter(recipient=user, is_read=False)
            .values('sender_id')
            .annotate(unread=Count('id'))
        )
        return Response({str(item['sender_id']): item['unread'] for item in unread})


