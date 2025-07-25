from django.contrib.auth.models import User
from django.db import models

from accounts.models import Account
from products.models import Product


# Create your models here.
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('unpaid', 'Unpaid'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_option = models.CharField(max_length=50)
    product_quantities = models.JSONField()

    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Order #{self.id} by {self.account.user.username}"