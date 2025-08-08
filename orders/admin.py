from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'order_first_name', 'order_last_name', 'status', 'total_price', 'created_at')
    readonly_fields = ('order_data_pretty', 'order_address', 'order_phone_number', 'order_first_name', 'order_last_name', 'created_at')

    fieldsets = (
        (None, {
            'fields': ('account', 'payment_option', 'status', 'total_price')
        }),
        ('Customer Snapshot', {
            'fields': ('order_first_name', 'order_last_name', 'order_address', 'order_phone_number'),
        }),
        ('Ordered Products', {
            'fields': ('order_data_pretty',),
        }),
        ('Timestamps', {
            'fields': ('created_at',),
        }),
    )

    def order_data_pretty(self, obj):
        if not obj.order_data:
            return "No product data."

        html = '<div style="padding-top: 1rem;">'
        for item in obj.order_data:
            image_html = f'<img src="{item["image_url"]}" width="50" height="50" style="border-radius:6px; object-fit:cover; margin-right: 10px;" />'
            html += f'''
            <div style="display: flex; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #ddd; padding-bottom: 8px;">
                {image_html}
                <div>
                    <strong>{item["name"]}</strong><br />
                    <small>Quantity: {item["quantity"]} — Price: ${item["price"]}</small>
                </div>
            </div>
            '''
        html += '</div>'
        return mark_safe(html)

    order_data_pretty.short_description = "Order Details"
