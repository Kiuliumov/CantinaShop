from django.contrib.auth.models import User
from django.db import models

from accounts.models import Account
from products.models import Product


# Create your models here.
class Order(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_option = models.CharField(max_length=50)
    products = models.ManyToManyField(Product)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)