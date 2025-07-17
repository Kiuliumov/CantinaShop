from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    is_available = models.BooleanField(default=True)
    image_url = models.CharField(max_length=255, blank=True, default='https://flightsunglasses.com/cdn/shop/products/ScreenShot2021-01-09at3.49.54PM_2048x.png?v=1610225425');
    quantity = models.PositiveIntegerField(default=1)
    slug = models.SlugField(unique=True, blank=True)
    has_discount = models.BooleanField(default=False)
    tags = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)

