from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic.edit import FormView
from django.contrib import messages
from .forms import RegistrationForm, LoginForm

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
        self.send_confirmation_email(user)
        messages.success(self.request, "Registration successful. Please check your email to activate your account.")
        return super().form_valid(form)

    def send_confirmation_email(self, user):
        current_site = get_current_site(self.request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = self.request.build_absolute_uri(
            reverse('activate', kwargs={'uidb64': uid, 'token': token})
        )
        subject = 'Activate your CantinaShop account'
        context = {
            'user': user,
            'domain': current_site.domain,
            'activation_link': activation_link,
        }

        html_content = render_to_string('accounts/email_for_confirmation.html', context)

        email = EmailMultiAlternatives(subject, '', EMAIL_SENDER, [user.email])
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

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
