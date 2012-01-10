# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
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
Tests for ProductVersion model.

"""
from django.test import TestCase

from ...execution.builders import create_run
from ...library.builders import create_case
from ..builders import create_user, create_product, create_productversion



class ProductVersionTest(TestCase):
    @property
    def ProductVersion(self):
        from cc.execution.models import ProductVersion
        return ProductVersion


    def test_unicode(self):
        p = create_product(name="Some Product")
        pv = self.ProductVersion(product=p, version="1.0")

        self.assertEqual(unicode(pv), u"Some Product 1.0")


    def test_parent(self):
        """A ProductVersion's ``parent`` property returns its Product."""
        pv = create_productversion()

        self.assertEqual(pv.parent, pv.product)


    def test_own_team(self):
        """If ``has_team`` is True, ProductVersion's team is its own."""
        pv = create_productversion(has_team=True)
        u = create_user()
        pv.own_team.add(u)

        self.assertEqual(list(pv.team.all()), [u])


    def test_inherit_team(self):
        """If ``has_team`` is False, ProductVersion's team is its parent's."""
        pv = create_productversion(has_team=False)
        u = create_user()
        pv.product.team.add(u)

        self.assertEqual(list(pv.team.all()), [u])


    def test_clone(self):
        """
        Cloning ProdVersion adds ".next" to version and "Cloned:" to codename.

        """
        c = create_productversion(version="1.0", codename="Foo")

        new = c.clone()

        self.assertNotEqual(new, c)
        self.assertIsInstance(new, self.ProductVersion)
        self.assertEqual(new.version, "1.0.next")
        self.assertEqual(new.codename, "Cloned: Foo")


    def test_clone_no_runs(self):
        """
        Cloning a ProductVersion does not clone runs.

        """
        pv = create_productversion()
        create_run(productversion=pv)

        new = pv.clone()

        self.assertEqual(len(new.runs.all()), 0)


    def test_clone_no_cases(self):
        """
        Cloning a ProductVersion does not clone test cases.

        """
        pv = create_productversion()
        create_case(productversion=pv)

        new = pv.clone()

        self.assertEqual(len(new.cases.all()), 0)
