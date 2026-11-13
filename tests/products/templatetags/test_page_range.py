import pytest
from django.core.paginator import Paginator

from products.templatetags.page_range import page_range


class TestPageRange:
    @pytest.mark.parametrize("current, expected", [(1, [1, 2, 3, 4, 5]), (5, [3, 4, 5, 6, 7]), (10, [6, 7, 8, 9, 10])])
    def test__page_range__keeps_window_within_bounds(self, current, expected):
        assert list(page_range(Paginator(range(100), 10), current)) == expected
