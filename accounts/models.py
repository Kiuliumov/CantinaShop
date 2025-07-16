from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.exceptions import ValidationError


class UserModel(AbstractUser):
    is_active = models.BooleanField(default=False)
    is_chat_banned = models.BooleanField(default=False)
    email = models.EmailField(unique=True, error_messages={'unique': 'A user with that email already exists.'})
    def __str__(self):
        return self.username


class Account(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE)
    profile_picture_url = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    default_shipping = models.ForeignKey(
        'Address',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='shipping_for'
    )
    default_billing = models.ForeignKey(
        'Address',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='billing_for'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Account"


class Address(models.Model):
    ADDRESS_TYPE_CHOICES = [
        ('shipping', 'Shipping'),
        ('billing', 'Billing'),
        ('other', 'Other'),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default='shipping')
    label = models.CharField(max_length=30, blank=True, null=True)

    street_address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=50, blank=True)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        errors = {}

        if self.address_type in ['shipping', 'billing'] and not self.street_address:
            errors['street_address'] = _('Street address is required for shipping or billing addresses.')

        if self.address_type in ['shipping', 'billing'] and not self.city:
            errors['city'] = _('City is required for shipping or billing addresses.')

        if self.address_type in ['shipping', 'billing'] and not self.country:
            errors['country'] = _('Country is required for shipping or billing addresses.')

        if self.postal_code and len(self.postal_code) > 20:
            errors['postal_code'] = _('Postal code cannot be longer than 20 characters.')

        if self.label and len(self.label) > 30:
            errors['label'] = _('Label cannot be longer than 30 characters.')

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.label or self.address_type} address for {self.account.user.username}"