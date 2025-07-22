from django.db import models

# Create your models here.
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)

class ContactView(FormView):
    template_name = 'contacts.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        messages.success(self.request, "Thanks for reaching out! We'll get back to you soon.")
        return super().form_valid(form)
