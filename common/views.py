from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from pyexpat.errors import messages
from django.contrib import messages
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