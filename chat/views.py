from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.template.context_processors import static
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from accounts.models import Account, UserModel
from chat.models import ChatMessage

class AdminChatHubView(UserPassesTestMixin, TemplateView):
    template_name = 'chat/hub.html'

    def test_func(self):
        user = self.request.user
        return user.is_staff or user.is_superuser

    def handle_no_permission(self):
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(self.request.get_full_path())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = Account.objects.filter(user__is_staff=False, user__is_superuser=False).select_related('user')
        context['admin_avatar_url'] = '/static/images/admin.jpg'
        return context


class ChatMessagesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, **kwargs):
        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(id=user_id)
        except UserModel.DoesNotExist:
            raise Http404("User not found")

        try:
            limit = int(request.GET.get('limit', 100))
            if limit <= 0:
                limit = 100
        except ValueError:
            limit = 100

        admins = UserModel.objects.filter(Q(is_staff=True) | Q(is_superuser=True))

        messages_qs = ChatMessage.objects.filter(
            Q(sender__id=user_id, recipient__in=admins) |
            Q(sender__in=admins, recipient__id=user_id)
        ).order_by('-timestamp')[:limit]

        messages = reversed(messages_qs)

        messages_data = []
        for msg in messages:
            if request.user.is_staff or request.user.is_superuser:
                sender_username = "Admin" if msg.sender.is_staff or msg.sender.is_superuser else msg.sender.username
                avatar_url = static('images/admin.jpg') if msg.sender.is_staff or msg.sender.is_superuser else getattr(msg.sender.account, 'profile_picture_url', '') or '/static/images/avatar.png'
                from_admin = msg.sender.is_staff or msg.sender.is_superuser
            else:
                sender_username = msg.sender.username
                avatar_url = getattr(msg.sender.account, 'profile_picture_url', '') or '/static/images/avatar.png'
                from_admin = msg.sender.is_staff or msg.sender.is_superuser

            messages_data.append({
                'id': msg.id,
                'message': msg.message,
                'sender_id': msg.sender_id,
                'sender_username': sender_username,
                'avatar_url': avatar_url,
                'timestamp': msg.timestamp.isoformat(),
                'from_admin': from_admin,
            })

        return Response({'messages': messages_data})