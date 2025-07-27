from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinLengthValidator
from accounts.validators import NoProfanityValidator, PhoneNumberValidator


class UserModel(AbstractUser):
    is_active = models.BooleanField(default=False)
    is_chat_banned = models.BooleanField(default=False)
    email = models.EmailField(
        unique=True,
        error_messages={'unique': 'A user with that email already exists.'}
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[NoProfanityValidator()],
    )

    def __str__(self):
        return self.username


class Account(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE)
    first_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        validators=[MinLengthValidator(2)]
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        validators=[MinLengthValidator(2)]
    )
    profile_picture_url = models.CharField(max_length=255, blank=True, null=True)
    country_code = models.CharField(max_length=15, blank=True, null=True)
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[PhoneNumberValidator(), MinLengthValidator(7)]
    )

    default_shipping = models.ForeignKey(
        'Address',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='shipping_for'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Account"


class Address(models.Model):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='addresses',
        blank=True,
        null=True
    )

    street_address = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        validators=[NoProfanityValidator(), MinLengthValidator(5)]
    )
    city = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        validators=[NoProfanityValidator(), MinLengthValidator(2)]
    )
    state = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        validators=[NoProfanityValidator(), MinLengthValidator(2)]
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[MinLengthValidator(3)]
    )
    country = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        validators=[NoProfanityValidator(), MinLengthValidator(2)]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{'Shipping Address'} for {self.account.user.username}"
