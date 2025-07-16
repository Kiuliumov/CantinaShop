from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.template.context_processors import static
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Account, UserModel
from chat.models import ChatMessage
from chat.serializers import ChatMessageSerializer


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
        user = get_object_or_404(UserModel, id=user_id)

        admins = UserModel.objects.filter(Q(is_staff=True) | Q(is_superuser=True))
        messages_qs = ChatMessage.objects.filter(
            Q(sender=user, recipient__in=admins) |
            Q(sender__in=admins, recipient=user)
        ).order_by('timestamp')

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