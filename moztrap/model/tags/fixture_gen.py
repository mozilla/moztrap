"""Sample cases and suites fixture generator."""
from fixture_generator import fixture_generator

from ..core.auth import User
from ..core.models import Product

from .models import Tag


@fixture_generator(Tag, requires=["core.sample_products", "core.sample_users"])
def sample_tags():
    admin = User.objects.get(username="admin")
    manager = User.objects.get(username="manager")

    cc = Product.objects.get(name="MozTrap")

    Tag.objects.create(name="registration", product=cc, user=manager)

    Tag.objects.create(name="key", user=admin)
