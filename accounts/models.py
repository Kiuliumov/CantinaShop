from django.contrib.auth.models import AbstractUser
from django.db import models
from typing import Optional


class UserModel(AbstractUser):
    pass


class Account(models.Model):
    user: UserModel = models.OneToOneField(UserModel, on_delete=models.CASCADE)

    street_address: str = models.CharField(max_length=100)
    city: str = models.CharField(max_length=50)
    state: str = models.CharField(max_length=50)
    postal_code: str = models.CharField(max_length=20)
    country: str = models.CharField(max_length=50)

    profile_picture: Optional[models.ImageField] = models.ImageField(
        upload_to='profiles/', blank=True
    )

    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.username}'s Account"
