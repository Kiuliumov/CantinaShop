import pytest

from products.forms import CategoryForm, CommentForm, ProductForm


class TestProductForm:
    def test__save_valid_product__persists(self, product_data):
        form = ProductForm(product_data)
        assert form.is_valid(), form.errors
        assert form.save().name == product_data["name"]


class TestCommentForm:
    @pytest.mark.parametrize("content", ["", "x" * 501])
    def test__validate_invalid_content__rejects(self, content):
        form = CommentForm({"content": content})
        assert not form.is_valid()
        assert "content" in form.errors


class TestCategoryForm:
    def test__validate_duplicate_name__rejects(self, category):
        form = CategoryForm({"name": category.name})
        assert not form.is_valid()
        assert "name" in form.errors
