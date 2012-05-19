"""
Tests for ProductResource api.

"""

from tests import case



class ProductResourceTest(case.api.ApiTestCase):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.ProductFactory


    @property
    def resource_name(self):
        return "product"


    def test_product(self):
        """Get a list of existing products and their versions"""
        assert False, "needs impl"


    def test_product_filter_name(self):
        """Get a products and its versions, filtered by product name"""
        assert False, "needs impl"
