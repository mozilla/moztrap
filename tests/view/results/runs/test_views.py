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
Tests for run results view.

"""
from django.core.urlresolvers import reverse

from tests import case

from ...lists.runs import RunsListTests



class RunResultsViewTest(case.view.ListViewTestCase,
                         RunsListTests,
                         case.view.ListFinderTests,
                         ):
    """Tests for run results view."""
    @property
    def factory(self):
        """The Run factory."""
        return self.F.RunFactory


    @property
    def url(self):
        """Shortcut for run results url."""
        return reverse("results_runs")



class RunDetailTest(case.view.AuthenticatedViewTestCase):
    """Test for run-detail ajax view."""
    def setUp(self):
        """Setup for run details tests; create a run."""
        super(RunDetailTest, self).setUp()
        self.testrun = self.F.RunFactory.create()


    @property
    def url(self):
        """Shortcut for run detail url."""
        return reverse(
            "results_run_details",
            kwargs=dict(run_id=self.testrun.id)
            )


    def test_details_description(self):
        """Details lists description."""
        self.testrun.description = "foodesc"
        self.testrun.save()

        res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})

        res.mustcontain("foodesc")


    def test_details_envs(self):
        """Details lists envs."""
        self.testrun.environments.add(
            *self.F.EnvironmentFactory.create_full_set({"OS": ["Windows"]}))

        res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})

        res.mustcontain("Windows")


    def test_details_team(self):
        """Details lists team."""
        u = self.F.UserFactory.create(username="somebody")
        self.testrun.add_to_team(u)

        res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})

        res.mustcontain("somebody")


    def test_details_drilldown(self):
        """Details contains link to drilldown to runcaseversions."""
        res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})

        res.mustcontain(
            "{0}?filter-run={1}".format(
                reverse("results_runcaseversions"), self.testrun.id)
            )
