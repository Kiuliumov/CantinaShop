from django.db import models

from accounts.models import Account


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
    order_data = models.JSONField()
    order_address = models.CharField(max_length=100)
    order_phone_number = models.CharField(max_length=100)
    order_first_name = models.CharField(max_length=100)
    order_last_name = models.CharField(max_length=100)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.order_address = (
                f"{self.account.default_shipping.street_address}, "
                f"{self.account.default_shipping.city}, "
                f"{self.account.default_shipping.state} "
                f"{self.account.default_shipping.postal_code}, "
                f"{self.account.default_shipping.country}"
            )
            self.order_phone_number = f'{self.account.country_code} {self.account.phone_number}'
            self.order_first_name = self.account.first_name
            self.order_last_name = self.account.last_name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} by {self.account.user.username}"
