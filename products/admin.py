from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Product, Rating, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_available', 'has_discount', 'category', 'average_rating', 'rating_count')
    list_filter = ('is_available', 'has_discount', 'category')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('average_rating', 'rating_count', 'created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating')
    list_filter = ('rating',)
    search_fields = ('user__user__username', 'product__name')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('account', 'product', 'created_at', 'short_content')
    search_fields = ('account__user__username', 'product__name', 'content')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)

    def short_content(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    short_content.short_description = 'Content'
