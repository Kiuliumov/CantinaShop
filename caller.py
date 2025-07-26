import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CantinaShop.settings')
django.setup()

from products.models import Product

def create_sunglasses_products():
    sunglasses_data = [
        {
            "name": "Polarized Pilot Sunglasses",
            "slug": "polarized-pilot-sunglasses",
            "description": "Lightweight pilot sunglasses with polarized lenses for glare reduction and maximum UV protection.",
            "price": 135.00,
            "category_id": 2,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1520975694717-d50a9f8ddfed?auto=format&fit=crop&w=800&q=80",
        },
        {
            "name": "Retro Round Sunglasses",
            "slug": "retro-round-sunglasses",
            "description": "Classic round-shaped sunglasses with a vintage vibe and scratch-resistant lenses.",
            "price": 105.50,
            "category_id": 2,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?auto=format&fit=crop&w=800&q=80",
        },
        {
            "name": "Bold Square Sunglasses",
            "slug": "bold-square-sunglasses",
            "description": "Striking square frame sunglasses with bold lines and UV protection for everyday wear.",
            "price": 120.00,
            "category_id": 2,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80",
        },
        {
            "name": "Classic Black Aviators",
            "slug": "classic-black-aviators",
            "description": "Timeless black aviator sunglasses designed with comfort and style in mind.",
            "price": 130.75,
            "category_id": 2,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1501594907352-04cda38ebc29?auto=format&fit=crop&w=800&q=80",
        },
        {
            "name": "Tortoise Shell Cat Eye",
            "slug": "tortoise-shell-cat-eye",
            "description": "Sophisticated cat eye sunglasses with a tortoise shell frame and anti-glare lenses.",
            "price": 140.00,
            "category_id": 2,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1497991791255-0b9f7ed15760?auto=format&fit=crop&w=800&q=80",
        },
        {
            "name": "Sport Wrap Sunglasses",
            "slug": "sport-wrap-sunglasses",
            "description": "Ergonomic wrap-around sunglasses designed for active lifestyles with UV protection.",
            "price": 95.99,
            "category_id": 2,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80",
        },
        {
            "name": "Gradient Tinted Lens Sunglasses",
            "slug": "gradient-tinted-lens-sunglasses",
            "description": "Elegant sunglasses with gradient tinted lenses offering stylish sun coverage.",
            "price": 125.00,
            "category_id": 2,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1520975905320-46a1f64a6e9f?auto=format&fit=crop&w=800&q=80",
        },
        {
            "name": "Vintage Oval Sunglasses",
            "slug": "vintage-oval-sunglasses",
            "description": "Smooth oval frames with a retro finish, ideal for casual and formal occasions.",
            "price": 99.99,
            "category_id": 2,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1491553895911-0055eca6402d?auto=format&fit=crop&w=800&q=80",
        },
        {
            "name": "Mirrored Sports Sunglasses",
            "slug": "mirrored-sports-sunglasses",
            "description": "High-performance sports sunglasses with mirrored lenses to reduce glare during outdoor activities.",
            "price": 110.00,
            "category_id": 2,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80",
        },
    ]

    for data in sunglasses_data:
        product, created = Product.objects.get_or_create(
            slug=data["slug"],
            defaults={
                "name": data["name"],
                "description": data["description"],
                "price": data["price"],
                "category_id": data["category_id"],
                "is_available": data["is_available"],
                "image_url": data["image_url"],
            },
        )
        if created:
            print(f'Created product: {product.name}')
        else:
            print(f'Product already exists: {product.name}')

if __name__ == '__main__':
    create_sunglasses_products()
