import pytest
from django.urls import reverse

from products.models import Comment, Product, Rating


class TestProductList:
    @pytest.mark.parametrize("query", [{"category": "Books"}, {"availability": "available"}, {"search": "Book"}])
    def test__filter_products__excludes_nonmatching_product(self, client, product, product_factory, query):
        other = product_factory(name="Other", is_available=False)
        if "category" in query:
            from products.models import Category

            other.category = Category.objects.create(name="Other")
            other.save()
        response = client.get(reverse("product-list"), query)
        assert list(response.context["products"]) == [product]

    def test__sort_price_desc__returns_expensive_first(self, client, product, product_factory):
        expensive = product_factory(price="99.00")
        response = client.get(reverse("product-list"), {"sort": "price_desc"})
        assert list(response.context["products"]) == [expensive, product]


class TestProductDetail:
    def test__get_product__renders_product(self, client, product):
        response = client.get(reverse("product-details", args=[product.slug]))
        assert response.status_code == 200
        assert response.context["product"] == product

    def test__post_comment__persists_author_and_content(self, auth_client, product, user):
        response = auth_client.post(reverse("product-details", args=[product.slug]), {"content": "Nice product!"})
        assert response.status_code == 200
        assert Comment.objects.filter(product=product, account=user.account, content="Nice product!").exists()


class TestProductManagement:
    def test__add_product_as_customer__forbidden(self, auth_client):
        assert auth_client.get(reverse("product-add")).status_code == 403

    def test__add_product_as_staff__creates_product(self, staff_client, product_data):
        response = staff_client.post(reverse("product-add"), product_data)
        assert response.status_code == 302
        assert Product.objects.filter(name=product_data["name"]).exists()

    def test__edit_product_as_staff__updates_product(self, staff_client, product, product_data):
        response = staff_client.post(reverse("product-edit", args=[product.slug]), product_data)
        product.refresh_from_db()
        assert response.status_code == 302
        assert product.name == product_data["name"]

    def test__delete_product_as_staff__removes_product(self, staff_client, product):
        assert staff_client.post(reverse("product-delete", args=[product.slug])).status_code == 302
        assert not Product.objects.filter(pk=product.pk).exists()


class TestCommentManagement:
    def test__delete_own_comment__removes_comment(self, auth_client, comment):
        assert auth_client.post(reverse("comment-delete", args=[comment.pk])).status_code == 302
        assert not Comment.objects.filter(pk=comment.pk).exists()

    def test__delete_other_comment__forbidden(self, client, user_factory, comment):
        client.force_login(user_factory())
        assert client.post(reverse("comment-delete", args=[comment.pk])).status_code == 403
        assert Comment.objects.filter(pk=comment.pk).exists()


class TestRating:
    def test__rate_twice__updates_single_vote(self, auth_client, product, user):
        url = reverse("rate", args=[product.slug])
        auth_client.post(url, {"rating": 2})
        assert auth_client.post(url, {"rating": 4}).status_code == 302
        assert list(Rating.objects.filter(product=product, user=user.account).values_list("rating", flat=True)) == [4]

    @pytest.mark.parametrize("rating", ["", "0", "6", "bad"])
    def test__rate_invalid_value__does_not_create_vote(self, auth_client, product, rating):
        assert auth_client.post(reverse("rate", args=[product.slug]), {"rating": rating}).status_code == 302
        assert not Rating.objects.exists()
