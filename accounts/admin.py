from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import UserModel, Account, Address


@admin.register(UserModel)
class UserAdmin(BaseUserAdmin):
    model = UserModel
    list_display = (
        'profile_image',
        'username_link',
        'email',
        'is_active',
        'is_chat_banned',
        'is_staff',
        'is_superuser'
    )
    list_editable = ('is_active', 'is_chat_banned')
    list_filter = ('is_active', 'is_chat_banned', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_chat_banned', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )


    def profile_image(self, obj):
        try:
            url = obj.account.profile_picture_url
            if url:
                return format_html(
                    '<a href="{0}" target="_blank">'
                    '<img src="{0}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />'
                    '</a>', url
                )
        except Account.DoesNotExist:
            pass
        return "—"


    profile_image.short_description = "Profile"


    def username_link(self, obj):
        return format_html('<a href="/admin/accounts/usermodel/{}/change/">{}</a>', obj.pk, obj.username)


    username_link.short_description = "Username"
    username_link.admin_order_field = "username"


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
    raw_id_fields = ('user', 'default_shipping')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('account', 'city', 'state')
    list_filter = ('country', 'city', 'state')
    search_fields = ('state', 'city', 'postal_code', 'country')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('account',)
