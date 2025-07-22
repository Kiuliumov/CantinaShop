from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import UserModel, Account, Address


@admin.register(UserModel)
class UserAdmin(BaseUserAdmin):
    model = UserModel
    list_display = ('username', 'email', 'is_active', 'is_chat_banned', 'is_staff', 'is_superuser')
    list_filter = ('is_active', 'is_chat_banned', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_chat_banned', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'created_at', 'updated_at')
    search_fields = ('user__username', 'phone_number')
    list_filter = ('created_at', 'updated_at')
    inlines = [AddressInline]

    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user', 'default_shipping', 'default_billing')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('account', 'label', 'address_type', 'city', 'state', 'is_default')
    list_filter = ('address_type', 'is_default', 'country')
    search_fields = ('label', 'city', 'state', 'postal_code', 'country')

    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('account',)
