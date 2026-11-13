import pytest
from django.db import IntegrityError, transaction

from products.models import Category, Comment, Rating


class TestProduct:
    def test__str__returns_name(self, product):
        assert str(product) == product.name

    def test__ratings_without_votes__returns_zero(self, product):
        assert (product.average_rating, product.rating_count) == (0, 0)

    def test__ratings_with_votes__returns_average_and_count(self, product, user, staff):
        Rating.objects.create(user=user.account, product=product, rating=4)
        Rating.objects.create(user=staff.account, product=product, rating=2)
        assert (product.average_rating, product.rating_count) == (3.0, 2)

    def test__save_colliding_slug__adds_suffix(self, product_factory):
        first = product_factory(name="Blue Book")
        second = product_factory(name="Blue-Book")
        assert (first.slug, second.slug) == ("blue-book", "blue-book-1")

    def test__rename_product__preserves_slug(self, product):
        slug = product.slug
        product.name = "Renamed"
        product.save()
        assert product.slug == slug


class TestCategory:
    def test__str__returns_name(self, category):
        assert str(category) == "Books"

    def test__create_duplicate__raises_integrity_error(self, category):
        with pytest.raises(IntegrityError), transaction.atomic():
            Category.objects.create(name=category.name)


class TestComment:
    def test__save__censors_profanity(self, product, user):
        comment = Comment.objects.create(product=product, account=user.account, content="shit")
        comment.refresh_from_db()
        assert comment.content == "****"
        assert str(comment) == f"{user.username} on {product.name}"
