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
Tests for results finder.

"""
from django.core.urlresolvers import reverse

from tests import case



class CaseColumnTest(case.DBTestCase):
    """Tests for results finder CaseColumn."""
    @property
    def column(self):
        """The Column class under test."""
        from cc.view.results.finders import CaseColumn
        return CaseColumn


    def test_goto_url(self):
        """goto_url returns results list url for given RCV."""
        c = self.column(
            None,
            None,
            self.model.RunCaseVersion.objects.all(),
            "results_results",
            )
        rcv = self.F.RunCaseVersionFactory.create()

        url = c.goto_url(rcv)

        self.assertEqual(
            url, reverse("results_results", kwargs={"rcv_id": rcv.id}))


    def test_no_goto_url(self):
        """goto_url still returns None if no url name given."""
        c = self.column(
            None,
            None,
            self.model.RunCaseVersion.objects.all(),
            )
        rcv = self.F.RunCaseVersionFactory.create()

        self.assertIsNone(c.goto_url(rcv))
