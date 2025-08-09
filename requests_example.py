import requests
import argparse

parser = argparse.ArgumentParser(description='Test CantinaShop API')
parser.add_argument('--api-key', help='API key for authentication', default='d9abb381d21216998c2c6095302b350a9efef079')
parser.add_argument('--base-url', default='http://localhost:8000/api', help='Base URL of the API')
args = parser.parse_args()

HEADERS = {
    'Authorization': f'Api-Key {args.api_key}',
    'Content-Type': 'application/json'
}

BASE_URL = args.base_url

def test_list_products():
    params = {
        'search': 'T-shirt',
        'min_price': '10',
        'max_price': '100',
        'sort': 'price_asc',
        'limit': 5
    }
    response = requests.get(f'{BASE_URL}/products/', headers=HEADERS, params=params)
    print("List Products:", response.status_code)
    print(response.json())

def test_create_product():
    payload = {
        "name": "Test Product",
        "description": "A sample product created via API",
        "price": "49.99",
        "is_available": True,
        "category": 5
    }
    response = requests.post(f'{BASE_URL}/products/', headers=HEADERS, json=payload)
    print("Create Product:", response.status_code)
    print(response.json())
    return response.json().get("id")

def test_get_product(product_id):
    response = requests.get(f'{BASE_URL}/products/{product_id}/', headers=HEADERS)
    print("Get Product:", response.status_code)
    print(response.json())

def test_update_product(product_id):
    payload = {
        "name": "Updated Product",
        "description": "Updated description",
        "price": "59.99",
        "is_available": False,
        "category": 5
    }
    response = requests.put(f'{BASE_URL}/products/{product_id}/', headers=HEADERS, json=payload)
    print("Update Product:", response.status_code)
    print(response.json())

def test_delete_product(product_id):
    response = requests.delete(f'{BASE_URL}/products/{product_id}/', headers=HEADERS)
    print("Delete Product:", response.status_code)

if __name__ == '__main__':
    test_list_products()
    product_id = test_create_product()
    test_get_product(product_id=product_id)
    test_update_product(product_id=product_id)
    test_delete_product(product_id=product_id)
    test_list_products()

