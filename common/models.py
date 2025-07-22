from django.db import models

# Create your models here.
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib import messages


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.name