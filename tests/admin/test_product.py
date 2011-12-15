from django_webtest import WebTest

from .base import AdminTestCase

from ..core.builders import create_product



class ProductAdminTest(AdminTestCase, WebTest):
    app_label = "core"
    model_name = "product"


    def test_changelist(self):
        """Product changelist page loads without error, contains name."""
        create_product(name="Firefox")

        self.get(self.changelist_url).mustcontain("Firefox")


    def test_change(self):
        """Product change page loads without error, contains name."""

        p = create_product(name="Firefox")

        self.get(self.change_url(p)).mustcontain("Firefox")
