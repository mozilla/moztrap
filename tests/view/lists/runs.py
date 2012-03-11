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
Common tests for run-list views.

"""
from datetime import date



class RunsListTests(object):
    """Common tests for any runs-list view."""
    def test_filter_by_status(self):
        """Can filter by status."""
        self.factory.create(name="Foo 1", status=self.model.Run.STATUS.active)
        self.factory.create(name="Foo 2", status=self.model.Run.STATUS.draft)

        res = self.get(params={"filter-status": "active"})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_filter_by_product(self):
        """Can filter by product."""
        one = self.factory.create(name="Foo 1")
        self.factory.create(name="Foo 2")

        res = self.get(
            params={"filter-product": str(one.productversion.product.id)})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_filter_by_productversion(self):
        """Can filter by product version."""
        one = self.factory.create(name="Foo 1")
        self.factory.create(name="Foo 2")

        res = self.get(
            params={"filter-productversion": str(one.productversion.id)})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_filter_by_name(self):
        """Can filter by name."""
        self.factory.create(name="Foo 1")
        self.factory.create(name="Foo 2")

        res = self.get(params={"filter-name": "1"})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_filter_by_description(self):
        """Can filter by name."""
        self.factory.create(name="Foo 1", description="foo bar")
        self.factory.create(name="Foo 2", description="bar baz")

        res = self.get(params={"filter-description": "foo"})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_filter_by_suite(self):
        """Can filter by included suite."""
        one = self.factory.create(name="Foo 1")
        rs = self.F.RunSuiteFactory(run=one)
        self.factory.create(name="Foo 2")

        res = self.get(params={"filter-suite": str(rs.suite.id)})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_filter_by_case_id(self):
        """Can filter by included case id."""
        one = self.factory.create(name="Foo 1")
        rs = self.F.RunSuiteFactory.create(run=one)
        sc = self.F.SuiteCaseFactory.create(suite=rs.suite)
        self.factory.create(name="Foo 2")

        res = self.get(params={"filter-case": str(sc.case.id)})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


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


    def test_sort_by_status(self):
        """Can sort by status."""
        self.factory.create(name="Run 1", status=self.model.Run.STATUS.active)
        self.factory.create(name="Run 2", status=self.model.Run.STATUS.draft)

        res = self.get(
            params={"sortfield": "status", "sortdirection": "desc"})

        self.assertOrderInList(res, "Run 2", "Run 1")


    def test_sort_by_name(self):
        """Can sort by name."""
        self.factory.create(name="Run 1")
        self.factory.create(name="Run 2")

        res = self.get(
            params={"sortfield": "name", "sortdirection": "desc"})

        self.assertOrderInList(res, "Run 2", "Run 1")


    def test_sort_by_productversion(self):
        """Can sort by productversion."""
        pb = self.F.ProductFactory.create(name="B")
        pa = self.F.ProductFactory.create(name="A")
        self.factory.create(
            name="x", productversion__product=pb, productversion__version="2")
        self.factory.create(
            name="y", productversion__product=pb, productversion__version="1")
        self.factory.create(
            name="z", productversion__product=pa, productversion__version="1")

        res = self.get(
            params={"sortfield": "productversion", "sortdirection": "asc"})

        self.assertOrderInList(res, "z", "y", "x")


    def test_sort_by_start(self):
        """Can sort by start."""
        self.factory.create(name="Run 1", start=date(2012, 1, 5))
        self.factory.create(name="Run 2", start=date(2012, 1, 10))

        res = self.get(
            params={"sortfield": "start", "sortdirection": "desc"})

        self.assertOrderInList(res, "Run 2", "Run 1")


    def test_sort_by_end(self):
        """Can sort by end."""
        self.factory.create(name="Run 1", end=date(2012, 1, 15))
        self.factory.create(name="Run 2", end=date(2012, 1, 10))

        res = self.get(
            params={"sortfield": "end", "sortdirection": "asc"})

        self.assertOrderInList(res, "Run 2", "Run 1")
