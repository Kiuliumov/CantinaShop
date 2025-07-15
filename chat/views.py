from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.template.context_processors import static
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView

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


@method_decorator(login_required, name='dispatch')
class ChatMessagesView(View):
    def get(self, request, user_id, **kwargs):
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(id=user_id)
        except UserModel.DoesNotExist:
            raise Http404("User not found")

        if not (request.user.is_staff or request.user.is_superuser):
            raise Http404("Not permitted")

        try:
            limit = int(request.GET.get('limit', 100))
            if limit <= 0:
                limit = 100
        except ValueError:
            limit = 100

        messages_qs = ChatMessage.objects.filter(
            Q(sender=user, recipient__id=0) |
            Q(sender__id=0, recipient=user) |
            Q(sender=user, recipient=request.user) |
            Q(sender=request.user, recipient=user)
        ).order_by('-timestamp')[:limit]

        messages = reversed(messages_qs)

        messages_data = []
        for msg in messages:
            if msg.sender_id == 0:
                sender_username = "Admin"
                avatar_url = static('images/admin.jpg')
                from_admin = True
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

        return JsonResponse({'messages': messages_data})