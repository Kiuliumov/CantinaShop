from django.contrib.auth.models import User
from django.db import models

from accounts.models import Account


# Create your models here.
class Order(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    produc