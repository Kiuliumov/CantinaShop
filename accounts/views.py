from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from accounts.forms import *

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('login')
