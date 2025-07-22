from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView, CreateView
from pyexpat.errors import messages

from common.forms import ContactMessageForm


# Create your views here.


class Index(TemplateView):
    template_name = 'index/index.html'

class About(TemplateView):
    template_name = 'index/about.html'

class ContactView(CreateView):
    template_name = 'index/contacts.html'
    form_class = ContactMessageForm
    success_url = reverse_lazy('index')
