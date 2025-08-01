from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView
from pyexpat.errors import messages
from django.contrib import messages

from api.models import APIKey
from common.forms import ContactMessageForm
from common.mixins import AdminRequiredMixin


# Create your views here.


class Index(TemplateView):
    template_name = 'index/index.html'


class About(TemplateView):
    template_name = 'index/about.html'


class GenerateAPIKeyREST(AdminRequiredMixin, TemplateView):
    template_name = 'api/generate_api_key.html'


class ContactView(CreateView):
    template_name = 'index/contacts.html'
    form_class = ContactMessageForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        messages.success(self.request, "Your message has been sent successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error submitting the form. Please check the fields and try again.")
        return super().form_invalid(form)


class APIKeyListView(AdminRequiredMixin, View):
    template_name = "api/key-list.html"

    def get(self, request):
        if request.user.is_superuser:
            api_keys = APIKey.objects.all().order_by('-created_at')
        else:
            api_keys = APIKey.objects.filter(user=request.user)
        return render(request, self.template_name, {"api_keys": api_keys})

    def post(self, request):
        key_id = request.POST.get("key_id")
        if request.user.is_superuser:
            api_key = get_object_or_404(APIKey, id=key_id)
        else:
            api_key = get_object_or_404(APIKey, id=key_id, user=request.user)

        if request.user.is_superuser or (request.user.is_staff and api_key.user == request.user):
            api_key.delete()
        else:
            messages.error(request, "You are not allowed to delete this API key!")
            return redirect('index')
        messages.success(request, "API key deleted successfully.")
        return redirect("apikey-list")