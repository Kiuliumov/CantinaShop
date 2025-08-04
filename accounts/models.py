from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.core.validators import MinLengthValidator, EmailValidator
from accounts.validators import NoProfanityValidator, PhoneNumberValidator


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email must be provided')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(email, password, **extra_fields)


class UserModel(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        error_messages={'unique': 'A user with that email already exists.'}
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[NoProfanityValidator()],
    )
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_chat_banned = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.username or self.email

    def get_full_name(self):
        return self.username or self.email

    def get_short_name(self):
        return self.username or self.email

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
