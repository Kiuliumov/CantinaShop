import json
import urllib.parse
from products.models import Product
from decimal import Decimal



def get_cart_items_and_total(request):
    cart_cookie = request.COOKIES.get('cart')
    items = []
    total = Decimal('0.00')

    if not cart_cookie:
        return items, total

    try:
        decoded_cart = urllib.parse.unquote(cart_cookie)
        raw_cart = json.loads(decoded_cart)
    except (json.JSONDecodeError, TypeError):
        raw_cart = []

    for entry in raw_cart:
        slug = entry.get('slug') if isinstance(entry, dict) else None
        quantity = entry.get('quantity', 1) if isinstance(entry, dict) else 1

        if not slug:
            continue

        product = Product.objects.filter(slug=slug).first()
        if not product:
            continue

        subtotal = product.price * quantity
        items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })
        total += subtotal

    return items, total

