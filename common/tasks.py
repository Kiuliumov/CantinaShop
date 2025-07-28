from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from CantinaShop import settings
EMAIL_SENDER = settings.DEFAULT_FROM_EMAIL

@shared_task
def send_confirmation_email_task(user_id, domain, activation_link, subject):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(pk=user_id)

    context = {
        'user': user,
        'domain': domain,
        'activation_link': activation_link,
    }
    html_content = render_to_string('accounts/authentication/email_for_confirmation.html', context)

    email = EmailMultiAlternatives(subject, '', EMAIL_SENDER, [user.email])
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)

@shared_task
def send_order_confirmation_email_task(user_id, order_id):
    from django.contrib.auth import get_user_model
    from orders.models import Order

    User = get_user_model()
    user = User.objects.get(pk=user_id)
    order = Order.objects.get(pk=order_id)

    subject = f"Your Order #{order.id} Confirmation"
    context = {
        'user': user,
        'order': order,
    }

    html_content = render_to_string('orders/order_confirmation_email.html', context)
    text_content = 'Thank you for your order!'

    email = EmailMultiAlternatives(subject, text_content, EMAIL_SENDER, [user.email])
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)


@shared_task
def send_password_reset_email_task(user_id, domain, reset_link, subject="Password Reset Request"):
    from django.contrib.auth import get_user_model
    from django.template.loader import render_to_string
    from django.core.mail import EmailMultiAlternatives
    from CantinaShop import settings

    User = get_user_model()
    user = User.objects.get(pk=user_id)

    context = {
        'user': user,
        'domain': domain,
        'reset_link': reset_link,
    }
    html_content = render_to_string('accounts/email/password_reset_email.html', context)
    email = EmailMultiAlternatives(subject, '', settings.DEFAULT_FROM_EMAIL, [user.email])
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)
