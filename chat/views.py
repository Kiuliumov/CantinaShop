from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, Max
from django.db.models.functions import Greatest
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ChatMessage
from .serializers import ChatMessageSerializer
from common.mixins import AdminRequiredMixin

UserModel = get_user_model()


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

        admin_user = self.request.user

        users = UserModel.objects.filter(
            is_staff=False,
            is_superuser=False
        ).select_related('account')

        users = users.annotate(
            last_sent=Max(
                'sent_messages__timestamp',
                filter=Q(sent_messages__recipient=admin_user)
            ),
            last_received=Max(
                'received_messages__timestamp',
                filter=Q(received_messages__sender=admin_user)
            )
        ).annotate(
            last_interaction=Greatest('last_sent', 'last_received')
        ).order_by('-last_interaction')
        unread_counts = ChatMessage.objects.filter(
            recipient=admin_user,
            is_read=False,
            sender__in=users,
        ).values('sender').annotate(
            unread_count=Count('id')
        )
        unread_map = {item['sender']: item['unread_count'] for item in unread_counts}

        for user in users:
            user.unread_count = unread_map.get(user.id, 0)

        context['users'] = users
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
