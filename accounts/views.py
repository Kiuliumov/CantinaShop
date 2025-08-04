from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.contrib import messages
from common.mixins import ProfileProhibitedMixin
from .forms import RegistrationForm, LoginForm, AccountForm
from .models import Account
from common.tasks import send_confirmation_email_task, send_password_reset_email_task

User = get_user_model()


class RegisterView(ProfileProhibitedMixin, FormView):
    template_name = 'accounts/authentication/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('email_confirmation_sent')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        domain = self.request.get_host()
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = self.request.build_absolute_uri(
            reverse_lazy('activate', kwargs={'uidb64': uidb64, 'token': token})
        )
        subject = "Activate your account"

        send_confirmation_email_task.delay(user.id, domain, activation_link, subject)

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

        return redirect('activation_invalid')

class Login(ProfileProhibitedMixin, LoginView):
    template_name = 'accounts/authentication/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('index')

    def get_success_url(self):
        return self.success_url

    def form_valid(self, form):
        messages.success(self.request, "Login successful!")
        return super().form_valid(form)

class Logout(LogoutView):
    next_page = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You have been logged out.")
        return super().dispatch(request, *args, **kwargs)

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

    def form_valid(self, form):
        messages.success(self.request, "Your account information has been updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error with your account information. Please try again.")
        return super().form_valid(form)

class AccountDeactivateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        user.is_active = False
        user.save()
        logout(request)
        messages.success(request, "Your account has been deactivated.")
        return redirect('index')

class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/reset/password_reset_form.html'
    email_template_name = None
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        for user in form.get_users(form.cleaned_data["email"]):
            domain = self.request.get_host()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_path = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            reset_link = f"http://{domain}{reset_path}"

            send_password_reset_email_task.delay(user.id, domain, reset_link)
        return redirect(self.success_url)