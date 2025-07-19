from django.urls import path
from .views import RegisterView, ActivateAccount, Login, Logout, AccountUpdateView, AccountDeactivateView, \
    AccountBanView
from django.views.generic import TemplateView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),

    path('activate/<uidb64>/<token>/', ActivateAccount.as_view(), name='activate'),
    path('email-confirmation-sent/', TemplateView.as_view(
        template_name='accounts/authentication/email_confirm.html'),
        name='email_confirmation_sent'),
    path('activation-invalid/', TemplateView.as_view(
        template_name='accounts/authentication/invalid_activation.html'),
        name='activation_invalid'),
    path('activation-success/', TemplateView.as_view(
        template_name='accounts/authentication/activation_success.html'),
        name='activation_success'),

    path('', AccountUpdateView.as_view(), name='account'),
    path('deactivate/', AccountDeactivateView.as_view(), name='account_deactivate'),
    path('ban/<int:user_id>/', AccountBanView.as_view(), name='account_deactivate_user'),
]