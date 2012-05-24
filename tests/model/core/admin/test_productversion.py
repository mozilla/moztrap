"""
Tests for ProductVersion admin.

"""
from tests import case



class ProductVersionAdminTest(case.admin.AdminTestCase):
    app_label = "core"
    model_name = "productversion"


    def test_changelist(self):
        """ProductVersion changelist page loads without error, contains name."""
        self.F.ProductVersionFactory.create(
            product__name="Foo", version="1.0")

        self.get(self.changelist_url).mustcontain("Foo 1.0")


    def test_change_page(self):
        """ProductVersion change page loads without error, contains name."""
        pv = self.F.ProductVersionFactory.create(
            product__name="Foo", version="1.0")

        self.get(self.change_url(pv)).mustcontain("Foo 1.0")
