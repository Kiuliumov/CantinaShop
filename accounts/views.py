from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.contrib import messages

from common.email_service import EmailService
from .forms import RegistrationForm, LoginForm, AccountForm
from .models import Account

User = get_user_model()
EMAIL_SENDER = 'no-reply@cantinashop.com'

class ProfileProhibitedMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)

class RegisterView(ProfileProhibitedMixin, FormView):
    template_name = 'accounts/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('email_confirmation_sent')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        EmailService.send_confirmation_email(self.request, user)
        messages.success(self.request, "Registration successful. Please check your email to activate your account.")
        return super().form_valid(form)


class ActivateAccount(View):
    def get(self, request, uidb64: str, token: str):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, "Your account has been activated successfully.")
            return redirect('activation_success')

        messages.error(request, "Activation link is invalid or expired.")
        return redirect('activation_invalid')

class Login(ProfileProhibitedMixin, LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('index')

    def get_success_url(self):
        return self.success_url

class Logout(LogoutView):
    next_page = reverse_lazy('index')

class AccountUpdateView(LoginRequiredMixin, UpdateView):
    model = Account
    form_class = AccountForm
    template_name = 'accounts/account_info.html'
    success_url = reverse_lazy('account')

    def get_object(self, queryset=None):
        return Account.objects.get(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']
        context['address_fields'] = [
            form['street_address'],
            form['city'],
            form['state'],
            form['postal_code'],
            form['country'],
        ]
        return context