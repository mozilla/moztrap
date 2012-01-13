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

from ... import factories as F



class ProductVersionTest(TestCase):
    def test_unicode(self):
        pv = F.ProductVersionFactory(
            product__name="Some Product", version="1.0")

        self.assertEqual(unicode(pv), u"Some Product 1.0")


    def test_parent(self):
        """A ProductVersion's ``parent`` property returns its Product."""
        pv = F.ProductVersionFactory()

        self.assertIs(pv.parent, pv.product)


    def test_own_team(self):
        """If ``has_team`` is True, ProductVersion's team is its own."""
        pv = F.ProductVersionFactory.create(has_team=True)
        u = F.UserFactory.create()
        pv.own_team.add(u)

        self.assertEqual(list(pv.team.all()), [u])


    def test_inherit_team(self):
        """If ``has_team`` is False, ProductVersion's team is its parent's."""
        pv = F.ProductVersionFactory.create(has_team=False)
        u = F.UserFactory.create()
        pv.product.team.add(u)

        self.assertEqual(list(pv.team.all()), [u])


    def test_clone(self):
        """Cloning PV adds ".next" to version, "Cloned:" to codename."""
        c = F.ProductVersionFactory.create(
            version="1.0", codename="Foo")

        new = c.clone()

        self.assertNotEqual(new, c)
        self.assertIsInstance(new, type(c))
        self.assertEqual(new.version, "1.0.next")
        self.assertEqual(new.codename, "Cloned: Foo")


    def test_clone_no_runs(self):
        """Cloning a ProductVersion does not clone runs."""
        run = F.RunFactory.create()

        new = run.productversion.clone()

        self.assertEqual(len(new.runs.all()), 0)


    def test_clone_no_cases(self):
        """Cloning a ProductVersion does not clone test case versions."""
        cv = F.CaseVersionFactory()

        new = cv.productversion.clone()

        self.assertEqual(len(new.caseversions.all()), 0)


    def test_clone_environments(self):
        """Cloning a ProductVersion clones its environments."""
        pv = F.ProductVersionFactory(environments={"OS": ["OS X", "Linux"]})

        new = pv.clone()

        self.assertEqual(len(new.environments.all()), 2)


    def test_clone_team(self):
        """Cloning a ProductVersion clones its team."""
        pv = F.ProductVersionFactory(team=["One", "Two"])

        new = pv.clone()

        self.assertEqual(len(new.team.all()), 2)
