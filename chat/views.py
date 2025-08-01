from django.core.exceptions import PermissionDenied
from django.templatetags.static import static
from django.views.generic import TemplateView
from accounts.models import Account
from common.mixins import AdminRequiredMixin


class AdminChatHubView(AdminRequiredMixin, TemplateView):
    template_name = 'chat/hub.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = Account.objects.filter(user__is_staff=False, user__is_superuser=False).select_related('user')
        context['admin_avatar_url'] = static('images/admin.jpg')
        return context


