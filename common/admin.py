# Register your models here.
from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'short_message', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('name', 'email', 'message', 'created_at')
    ordering = ('-created_at',)

    def short_message(self, obj):
        return (obj.message[:75] + '...') if len(obj.message) > 75 else obj.message
    short_message.short_description = 'Message Preview'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
