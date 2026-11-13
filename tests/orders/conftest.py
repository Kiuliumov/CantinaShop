import pytest
from model_bakery import baker

from orders.models import Order


@pytest.fixture
def order(shipping_account):
    return baker.make(Order, account=shipping_account, payment_option="credit_card", order_data=[], total_price="19.99")
