class TestOrder:
    def test__create_order__snapshots_shipping_details(self, order, shipping_account):
        assert order.order_address == "123 Main St, Sofia, Sofia 1000, Bulgaria"
        assert order.order_phone_number == "+1 1234567890"
        assert (order.order_first_name, order.order_last_name) == ("Jane", "Doe")
        assert str(order) == f"Order #{order.pk} by {shipping_account.user.username}"

    def test__save_existing_order__preserves_original_address(self, order, shipping_account):
        shipping_account.default_shipping.street_address = "456 New Street"
        shipping_account.default_shipping.save()
        order.status = "shipped"
        order.save()
        order.refresh_from_db()
        assert order.order_address.startswith("123 Main St")
