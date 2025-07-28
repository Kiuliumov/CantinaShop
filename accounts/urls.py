from django.urls import path, include, reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from .views import (
    RegisterView, ActivateAccount, Login, Logout,
    AccountUpdateView, AccountDeactivateView,
    CustomPasswordResetView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('deactivate/', AccountDeactivateView.as_view(), name='account_deactivate'),
    path('', AccountUpdateView.as_view(), name='account'),

    path('activate/<uidb64>/<token>/', ActivateAccount.as_view(), name='activate'),
    path('email-confirmation-sent/', TemplateView.as_view(
        template_name='accounts/authentication/email_confirm.html'),
        name='email_confirmation_sent'
    ),
    path('activation-invalid/', TemplateView.as_view(
        template_name='accounts/authentication/invalid_activation.html'),
        name='activation_invalid'
    ),
    path('activation-success/', TemplateView.as_view(
        template_name='accounts/authentication/activation_success.html'),
        name='activation_success'
    ),

    path('reset/', include([
        path('', CustomPasswordResetView.as_view(), name='password_reset'),
        path('done/', auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/reset/password_reset_done.html'
        ), name='password_reset_done'),
        path('confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/reset/password_reset.html',
            success_url=reverse_lazy('password_reset_complete')
        ), name='password_reset_confirm'),
        path('complete/', auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/reset/password_reset_complete.html'
        ), name='password_reset_complete'),
    ])),
]
