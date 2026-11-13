import pytest
from model_bakery import baker

from products.models import Comment


@pytest.fixture
def comment(product, user):
    return baker.make(Comment, product=product, account=user.account, content="Nice product")
