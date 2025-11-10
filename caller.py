import os
import django


# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CantinaShop.settings')
django.setup()
import requests
import time

API_KEY = "cf47d26efc1ef29f74545fc956f1f75747186918"
API_URL = "http://localhost:8000/api/products"
HEADERS = {
    "Authorization": f"Api-Key {API_KEY}",
    "Content-Type": "application/json"
}

category_image_map = {
    "Glasses": "https://t4.ftcdn.net/jpg/02/75/59/67/360_F_275596704_zEbwscKfJpbFlIfc9qNzyQXdaPqFKwFA.jpg",
    "Rings": "https://t4.ftcdn.net/jpg/00/71/67/87/360_F_71678766_kPinbw5YXRSJrlwwT8SmA90TgjBu64Ng.jpg",
    "Necklaces": "https://media.istockphoto.com/id/516134632/photo/golden-chain-with-diamond-dollar-symbol.jpg?s=612x612&w=0&k=20&c=6d3nFYXi_JDD1IPp-2zFj-jlFHFziazNlOVycZYk0nk=",
    "Bracelets": "https://eu-images.contentstack.com/v3/assets/blt7dcd2cfbc90d45de/bltca81f71186c56e20/649edc0a68c5bf5a28e030ff/square_box_chain_2mm_-_30349_f1.jpg?format=pjpg&auto=webp&quality=75%2C90&width=3840",
    "Earrings": "https://media.istockphoto.com/id/1390616610/photo/round-diamond-earrings.jpg?s=612x612&w=0&k=20&c=x9KxBbapmuOwYbOlZujjPkLy27amt7AUYMmQguEdF6U=",
    "Jewelry": 'https://media.istockphoto.com/id/1131752930/photo/diamond-jewelry-design.jpg?s=2048x2048&w=is&k=20&c=-_DC6jpSMdSlBd87ZNjxB-ZPzIu4csAyvpVsArRr0z4=',
    'Other Accessories': 'https://t3.ftcdn.net/jpg/01/10/24/34/360_F_110243449_7SHALLFfuzJq2j33dsfRWTElxxKOag9Y.jpg'
}

def patch_product_image(product_id, image_url):
    patch_data = {"image_url": image_url}
    url = f"{API_URL}/{product_id}/"
    response = requests.patch(url, json=patch_data, headers=HEADERS)
    if response.status_code in (200, 202):
        print(f"Updated product {product_id} with image_url")
    else:
        print(f"Failed to update product {product_id}: {response.status_code} {response.text}")

def main():
    # Fetch all products first
    response = requests.get(API_URL, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch products list: {response.status_code} {response.text}")
        return

    products = response.json().get('products', [])
    filtered = Product.objects.all().filter(category_id=5)

    for product in filtered:
        patch_product_image(product.id, 'https://eu-images.contentstack.com/v3/assets/blt7dcd2cfbc90d45de/bltca81f71186c56e20/649edc0a68c5bf5a28e030ff/square_box_chain_2mm_-_30349_f1.jpg?format=pjpg&auto=webp&quality=75%2C90&width=3840')
        time.sleep(0.1)

if __name__ == "__main__":
    from products.models import Product
    main()
