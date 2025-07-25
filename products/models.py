from django.db import models
from django.core.validators import MaxValueValidator
from django.db.models import Avg, Count
from django.template.defaultfilters import slugify

from accounts.models import Account
from common.profanity_utils import smart_censor

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

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
    slug = models.SlugField(unique=True, blank=True)
    has_discount = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    @property
    def average_rating(self):
        avg = self.rating_set.aggregate(avg=Avg('rating'))['avg']
        return float(avg) if avg is not None else 0

    @property
    def rating_count(self):
        return self.rating_set.aggregate(count=Count('id'))['count'] or 0

    def save(self, *args, **kwargs):
        self.name = smart_censor(self.name)
        self.description = smart_censor(self.description)

        if not self.pk and not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Rating(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MaxValueValidator(5)])

class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    content = models.TextField(max_length=500, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.account.user.username} on {self.product.name}"

    def save(self, *args, **kwargs):
        self.content = smart_censor(self.content)
        super().save(*args, **kwargs)
