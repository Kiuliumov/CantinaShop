from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class UserModel(AbstractUser):
    pass


class Account(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE)
    subscription_status = models.CharField(max_length=20)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)