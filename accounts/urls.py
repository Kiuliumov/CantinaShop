from django.urls import path
from .views import RegisterView, ActivateAccount, Login, Logout, AccountUpdateView
from django.views.generic import TemplateView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', ActivateAccount.as_view(), name='activate'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),

    path('email-confirmation-sent/',
         TemplateView.as_view(template_name='accounts/email_confirm.html'),
         name='email_confirmation_sent'),

    path('activation-invalid/',
         TemplateView.as_view(template_name='accounts/invalid_activation.html'),
         name='activation_invalid'),
    path('activation-success/',
             TemplateView.as_view(template_name='accounts/activation_success.html'),
             name='activation_success'),

    path('', AccountUpdateView.as_view(), name='account'),
]