from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View

User = get_user_model()


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.is_superuser)

    def handle_no_permission(self):
        raise PermissionDenied


class ToggleChatBanView(AdminRequiredMixin, View):
    def post(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise Http404

        user.is_chat_banned = not user.is_chat_banned
        user.save()

        status = 'banned' if user.is_chat_banned else 'unbanned'
        messages.success(request, f'User chat has been {status}.')

        return redirect(request.META.get('HTTP_REFERER', reverse('admin:user_list')))


class ToggleActiveStatusView(AdminRequiredMixin, View):
    def post(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise Http404

        user.is_active = not user.is_active
        user.save()

        status = 'deactivated' if not user.is_active else 'activated'
        messages.success(request, f'User account has been {status}.')

        return redirect(request.META.get('HTTP_REFERER', reverse('admin:user_list')))
