from django.db import models
from django.core.validators import MaxValueValidator
from accounts.models import Account
from common.profanity_utils import smart_censor

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = smart_censor(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = smart_censor(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    is_available = models.BooleanField(default=True)
    image_url = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    slug = models.SlugField(unique=True, blank=True)
    has_discount = models.BooleanField(default=False)
    tags = models.CharField(max_length=255, blank=True)
    rating = models.PositiveIntegerField(validators=[MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.name = smart_censor(self.name)
        self.description = smart_censor(self.description)
        super().save(*args, **kwargs)


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.account.user.username} on {self.product.name}"

    def save(self, *args, **kwargs):
        self.content = smart_censor(self.content)
        super().save(*args, **kwargs)
