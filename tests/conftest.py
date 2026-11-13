import itertools
import json
from decimal import Decimal
from unittest.mock import Mock
from urllib.parse import quote

import pytest
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from model_bakery import baker
from rest_framework.test import APIClient

from accounts.models import Address
from common import tasks
from products.models import Category, Product


@pytest.fixture(autouse=True)
def clean_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def user_factory(db, django_user_model):
    sequence = itertools.count()

    def create(**kwargs):
        number = next(sequence)
        data = dict(username=f"buyer{number}", email=f"buyer{number}@example.com", is_active=True)
        data.update(kwargs)
        data["password"] = make_password(data.pop("password", "SecurePass123!"))
        return baker.make(django_user_model, **data)

    return create


@pytest.fixture
def user(user_factory):
    return user_factory()


@pytest.fixture
def staff(user_factory):
    return user_factory(is_staff=True)


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def staff_client(client, staff):
    client.force_login(staff)
    return client


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def category(db):
    return baker.make(Category, name="Books")


@pytest.fixture
def product_factory(db, category):
    sequence = itertools.count()

    def create(**kwargs):
        data = dict(name=f"Book {next(sequence)}", description="A good read", price=Decimal("19.99"), category=category)
        data.update(kwargs)
        return baker.make(Product, slug="", **data)

    return create


@pytest.fixture
def product(product_factory):
    return product_factory()


@pytest.fixture
def product_data(category):
    return dict(name="New Book", description="A new read", price="29.99", category=category.pk, is_available=True)


@pytest.fixture
def shipping_account(user):
    account = user.account
    account.first_name, account.last_name = "Jane", "Doe"
    account.country_code, account.phone_number = "+1", "1234567890"
    account.default_shipping = baker.make(
        Address,
        account=account,
        street_address="123 Main St",
        city="Sofia",
        state="Sofia",
        postal_code="1000",
        country="Bulgaria",
    )
    account.save()
    return account


@pytest.fixture
def encode_cart():
    return lambda items: quote(json.dumps(items))


@pytest.fixture
def cart_client(auth_client, product, encode_cart):
    auth_client.cookies["cart"] = encode_cart([{"slug": product.slug, "quantity": 2}])
    return auth_client


@pytest.fixture
def queued_emails(monkeypatch):
    mocks = {}
    for name in (
        "send_confirmation_email_task",
        "send_password_reset_email_task",
        "send_order_confirmation_email_task",
    ):
        mocks[name] = Mock()
        monkeypatch.setattr(getattr(tasks, name), "delay", mocks[name])
    return mocks
