from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView, CreateView
from pyexpat.errors import messages

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
