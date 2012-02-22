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
Tests for results-list view.

"""
from django.core.urlresolvers import reverse

from tests import case



class ResultsViewTest(case.view.ListViewTestCase,
                      case.view.ListFinderTests,
                      ):
    """Tests for results-list view."""
    name_attr = "tester__username"


    def setUp(self):
        """Results list view requires a runcaseversion."""
        super(ResultsViewTest, self).setUp()
        self.rcv = self.F.RunCaseVersionFactory.create()


    @property
    def url(self):
        """Shortcut for result results url."""
        return reverse("results_results", kwargs={"rcv_id": self.rcv.id})


    def factory(self, **kwargs):
        """Create a result for this test case's runcaseversion."""
        kwargs.setdefault("runcaseversion", self.rcv)
        return self.F.ResultFactory.create(**kwargs)


    def test_filter_by_status(self):
        """Can filter by status."""
        self.factory(status="passed", tester__username="Tester 1")
        self.factory(status="failed", tester__username="Tester 2")

        res = self.get(params={"filter-status": "failed"})

        self.assertInList(res, "Tester 2")
        self.assertNotInList(res, "Tester 1")


    def test_filter_by_tester(self):
        """Can filter by tester."""
        r = self.factory(tester__username="Tester 1")
        self.factory(tester__username="Tester 2")

        res = self.get(params={"filter-tester": str(r.tester.id)})

        self.assertInList(res, "Tester 1")
        self.assertNotInList(res, "Tester 2")


    def test_filter_by_comment(self):
        """Can filter by name."""
        self.factory(comment="foo", tester__username="Tester 1")
        self.factory(comment="bar", tester__username="Tester 2")

        res = self.get(params={"filter-comment": "fo"})

        self.assertInList(res, "Tester 1")
        self.assertNotInList(res, "Tester 2")


    def test_filter_by_env_elements(self):
        """Can filter by environment elements."""
        envs = self.F.EnvironmentFactory.create_full_set(
            {"OS": ["Linux", "Windows"]})
        self.factory(
            tester__username="Tester 1", environment=envs[0])
        self.factory(
            tester__username="Tester 2", environment=envs[1])

        res = self.get(
            params={"filter-envelement": envs[0].elements.all()[0].id})

        self.assertInList(res, "Tester 1")
        self.assertNotInList(res, "Tester 2")


    def test_sort_by_status(self):
        """Can sort by status."""
        self.factory(tester__username="Tester 1", status="passed")
        self.factory(tester__username="Tester 2", status="failed")

        res = self.get(
            params={"sortfield": "status", "sortdirection": "asc"})

        self.assertOrderInList(res, "Tester 2", "Tester 1")


    def test_sort_by_tester(self):
        """Can sort by tester."""
        self.factory(tester__username="Tester 1")
        self.factory(tester__username="Tester 2")

        res = self.get(
            params={"sortfield": "tester__username", "sortdirection": "desc"}
            )

        self.assertOrderInList(res, "Tester 2", "Tester 1")
