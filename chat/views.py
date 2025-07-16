from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from accounts.models import Account



class AdminChatHubView(UserPassesTestMixin, TemplateView):
    template_name = 'chat/hub.html'

    def test_func(self):
        user = self.request.user
        return user.is_staff or user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = Account.objects.filter(user__is_staff=False, user__is_superuser=False).select_related('user')
        context['admin_avatar_url'] = '/static/images/admin.jpg'
        return context


