from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from chat.models import ChatMessage


# Create your views here.
class RecentChatMessagesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        messages = ChatMessage.objects.order_by('-timestamp')[:40]
        messages = reversed(messages)
        data = [{
            'username': msg.user.username if msg.user else 'Anonymous',
            'message': msg.message,
            'avatar_url': getattr(msg.user, 'profile_picture_url', '') if msg.user else '',
            'timestamp': msg.timestamp.isoformat(),
        } for msg in messages]

        return JsonResponse(data, safe=False)