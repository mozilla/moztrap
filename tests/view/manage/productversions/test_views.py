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
Tests for productversion management views.

"""
from django.core.urlresolvers import reverse

from tests import case



class ProductVersionsTest(case.view.manage.ListViewTestCase,
                          case.view.ListFinderTests,
                          case.view.manage.CCModelListTests,
                          ):
    """Test for productversions manage list view."""
    form_id = "manage-productversions-form"
    perm = "manage_products"


    @property
    def factory(self):
        """The model factory for this manage list."""
        return self.F.ProductVersionFactory


    @property
    def url(self):
        """Shortcut for manage-productversions url."""
        return reverse("manage_productversions")


    def test_filter_by_version(self):
        """Can filter by version."""
        self.factory.create(name="Foo 1.0")
        self.factory.create(name="Foo 2.0")

        res = self.get(params={"filter-version": "1"})

        self.assertInList(res, "Foo 1.0")
        self.assertNotInList(res, "Foo 2.0")


    def test_filter_by_codename(self):
        """Can filter by codename."""
        self.factory.create(name="Foo 1.0", codename="One")
        self.factory.create(name="Foo 2.0", codename="Two")

        res = self.get(params={"filter-codename": "One"})

        self.assertInList(res, "Foo 1.0")
        self.assertNotInList(res, "Foo 2.0")


    def test_filter_by_product(self):
        """Can filter by product."""
        one = self.factory.create(name="Foo 1.0")
        self.factory.create(name="Foo 2.0")

        res = self.get(params={"filter-product": str(one.product.id)})

        self.assertInList(res, "Foo 1.0")
        self.assertNotInList(res, "Foo 2.0")


    def test_filter_by_env_elements(self):
        """Can filter by environment elements."""
        envs = self.F.EnvironmentFactory.create_full_set(
            {"OS": ["Linux", "Windows"]})
        self.factory.create(name="Foo 1", environments=envs)
        self.factory.create(name="Foo 2", environments=envs[1:])

        res = self.get(
            params={"filter-envelement": envs[0].elements.all()[0].id})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_sort_by_default_order(self):
        """Can sort by default order."""
        self.factory.create(product__name="B", version="1")
        self.factory.create(product__name="A", version="1")
        self.factory.create(product__name="A", version="2")

        res = self.get(
            params={"sortfield": "product,order", "sortdirection": "asc"})

        self.assertOrderInList(res, "A 1", "A 2", "B 1")


    def test_sort_by_codename(self):
        """Can sort by codename."""
        self.factory.create(name="ProductVersion 1", codename="B")
        self.factory.create(name="ProductVersion 2", codename="A")

        res = self.get(
            params={"sortfield": "codename", "sortdirection": "asc"})

        self.assertOrderInList(res, "ProductVersion 2", "ProductVersion 1")


    def test_sort_by_product(self):
        """Can sort by product."""
        self.factory.create(product__name="B", version="1")
        self.factory.create(product__name="A", version="1")

        res = self.get(
            params={"sortfield": "product", "sortdirection": "asc"})

        self.assertOrderInList(res, "A 1", "B 1")



class ProductVersionDetailTest(case.view.AuthenticatedViewTestCase):
    """Test for productversion-detail ajax view."""
    def setUp(self):
        """Setup for case details tests; create a productversion."""
        super(ProductVersionDetailTest, self).setUp()
        self.productversion = self.F.ProductVersionFactory.create()


    @property
    def url(self):
        """Shortcut for product version detail url."""
        return reverse(
            "manage_productversion_details",
            kwargs=dict(productversion_id=self.productversion.id)
            )


    def test_details_envs(self):
        """Details lists envs."""
        self.productversion.environments.add(
            *self.F.EnvironmentFactory.create_full_set({"OS": ["Windows"]}))

        res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})

        res.mustcontain("Windows")


    def test_details_runs(self):
        """Details lists runs."""
        self.F.RunFactory.create(
            productversion=self.productversion, name="Foo Run")

        res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})

        res.mustcontain("Foo Run")


    def test_details_team(self):
        """Details lists team."""
        u = self.F.UserFactory.create(username="somebody")
        self.productversion.add_to_team(u)

        res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})

        res.mustcontain("somebody")



class AddProductVersionTest(case.view.FormViewTestCase):
    """Tests for add product version view."""
    form_id = "productversion-add-form"


    @property
    def url(self):
        """Shortcut for add-productversion url."""
        return reverse("manage_productversion_add")


    def setUp(self):
        """Add manage-products permission to user."""
        super(AddProductVersionTest, self).setUp()
        self.add_perm("manage_products")


    def test_success(self):
        """Can add a productversion with basic data."""
        p = self.F.ProductFactory.create(name="Foo")
        form = self.get_form()
        form["product"] = str(p.id)
        form["codename"] = "codename"
        form["version"] = "1.0"

        res = form.submit(status=302)

        self.assertRedirects(res, reverse("manage_productversions"))

        res.follow().mustcontain("Product version 'Foo 1.0' added.")

        pv = self.model.ProductVersion.objects.get()
        self.assertEqual(pv.name, "Foo 1.0")
        self.assertEqual(pv.codename, "codename")


    def test_error(self):
        """Bound form with errors is re-displayed."""
        res = self.get_form().submit()

        self.assertEqual(res.status_int, 200)
        res.mustcontain("This field is required.")


    def test_requires_manage_products_permission(self):
        """Requires manage-products permission."""
        res = self.app.get(
            self.url, user=self.F.UserFactory.create(), status=302)

        self.assertRedirects(res, reverse("auth_login") + "?next=" + self.url)



class EditProductVersionTest(case.view.FormViewTestCase):
    """Tests for edit-productversion view."""
    form_id = "productversion-edit-form"


    def setUp(self):
        """Setup for edit tests; create productversion, add perm."""
        super(EditProductVersionTest, self).setUp()
        self.productversion = self.F.ProductVersionFactory.create(
            product__name="Foo")
        self.add_perm("manage_products")


    @property
    def url(self):
        """Shortcut for edit-productversion url."""
        return reverse(
            "manage_productversion_edit",
            kwargs=dict(productversion_id=self.productversion.id))


    def test_requires_manage_products_permission(self):
        """Requires manage-products permission."""
        res = self.app.get(
            self.url, user=self.F.UserFactory.create(), status=302)

        self.assertRedirects(res, reverse("auth_login") + "?next=" + self.url)


    def test_save_basic(self):
        """Can save updates; redirects to manage productversions list."""
        form = self.get_form()
        form["version"] = "2.0"
        form["codename"] = "new code"
        res = form.submit(status=302)

        self.assertRedirects(res, reverse("manage_productversions"))

        res.follow().mustcontain("Saved 'Foo 2.0'.")

        pv = self.refresh(self.productversion)
        self.assertEqual(pv.name, "Foo 2.0")
        self.assertEqual(pv.codename, "new code")


    def test_errors(self):
        """Test bound form redisplay with errors."""
        form = self.get_form()
        form["version"] = ""
        res = form.submit(status=200)

        res.mustcontain("This field is required.")


    def test_concurrency_error(self):
        """Concurrency error is displayed."""
        form = self.get_form()

        self.productversion.save()

        form["codename"] = "New"
        res = form.submit(status=200)

        res.mustcontain("Another user saved changes to this object")
