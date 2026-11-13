from decimal import Decimal

import pytest

from orders.cart_utils import get_cart_items_and_total


class TestCartItems:
    @pytest.mark.parametrize("cookie", ["", "invalid", "%5B%5D"])
    def test__read_empty_or_invalid_cart__returns_zero(self, rf, cookie):
        request = rf.get("/")
        request.COOKIES["cart"] = cookie
        assert get_cart_items_and_total(request) == ([], Decimal("0.00"))

    def test__read_cart__totals_valid_products_and_skips_unknown_entries(self, rf, product, encode_cart):
        request = rf.get("/")
        request.COOKIES["cart"] = encode_cart([None, {}, {"slug": "missing"}, {"slug": product.slug, "quantity": 2}])
        items, total = get_cart_items_and_total(request)
        assert items == [{"product": product, "quantity": 2, "subtotal": product.price * 2}]
        assert total == Decimal("39.98")
