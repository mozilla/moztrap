# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-12 Mozilla
#
# This file is part of Case Conductor.
#
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
"""
Tests for product management views.

"""
from django.core.urlresolvers import reverse

from .... import factories as F
from ... import base



class ProductsTest(base.ManageListViewFinderTestCase):
    """Test for products manage list view."""
    form_id = "manage-products-form"
    perm = "manage_products"
    factory = F.ProductFactory


    @property
    def url(self):
        """Shortcut for manage-products url."""
        return reverse("manage_products")


    def test_filter_by_name(self):
        """Can filter by name."""
        self.factory.create(name="Product 1")
        self.factory.create(name="Product 2")

        res = self.get(params={"filter-name": "1"})

        self.assertInList(res, "Product 1")
        self.assertNotInList(res, "Product 2")


    def test_sort_by_name(self):
        """Can sort by name."""
        self.factory.create(name="Product 1")
        self.factory.create(name="Product 2")

        res = self.get(params={"sortfield": "name", "sortdirection": "desc"})

        self.assertOrderInList(res, "Product 2", "Product 1")



class ProductDetailTest(base.AuthenticatedViewTestCase):
    """Test for product-detail ajax view."""
    def setUp(self):
        """Setup for case details tests; create a caseversion."""
        super(ProductDetailTest, self).setUp()
        self.product = F.ProductFactory.create()


    @property
    def url(self):
        """Shortcut for add-case-single url."""
        return reverse(
            "manage_product_details", kwargs=dict(product_id=self.product.id))


    def test_details(self):
        """Returns details HTML snippet for given product."""
        F.ProductVersionFactory.create(
            product=self.product, version="0.8-alpha-1")

        res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})

        res.mustcontain("0.8-alpha-1")
