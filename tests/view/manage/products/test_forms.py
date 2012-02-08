# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-2012 Mozilla
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
Tests for product-management forms.

"""
from tests import case



class EditProductFormTest(case.DBTestCase):
    """Tests for EditProductForm."""
    @property
    def form(self):
        """The form class under test."""
        from cc.view.manage.products.forms import EditProductForm
        return EditProductForm


    def test_edit_product(self):
        """Can edit product name and description, with modified-by user."""
        p = self.F.ProductFactory(name="Take One", description="")
        u = self.F.UserFactory()

        f = self.form(
            {"name": "Two", "description": "not blank"}, instance=p, user=u)

        product = f.save()

        self.assertEqual(product.name, "Two")
        self.assertEqual(product.description, "not blank")
        self.assertEqual(product.modified_by, u)



class AddProductFormTest(case.DBTestCase):
    """Tests for AddProductForm."""
    @property
    def form(self):
        """The form class under test."""
        from cc.view.manage.products.forms import AddProductForm
        return AddProductForm


    def test_add_product(self):
        """Can add product, with version and created-by user."""
        u = self.F.UserFactory()

        f = self.form(
            {"name": "Two", "version": "1.0", "description": "not blank"},
            user=u)

        product = f.save()

        self.assertEqual(product.name, "Two")
        self.assertEqual(product.description, "not blank")
        self.assertEqual(product.created_by, u)

        version = product.versions.get()

        self.assertEqual(version.version, "1.0")
        self.assertEqual(version.created_by, u)


    def test_add_product_with_profile(self):
        """Can add product with initial environment profile."""
        profile = self.F.ProfileFactory.create()
        envs = self.F.EnvironmentFactory.create_full_set(
            {"OS": ["OS X", "Linux"]}, profile=profile)

        f = self.form({"name": "Two", "version": "1.0", "profile": profile.id})

        version = f.save().versions.get()

        self.assertEqual(set(version.environments.all()), set(envs))
