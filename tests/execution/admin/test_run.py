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
Tests for Run admin.

"""
from ...admin import AdminTestCase
from ... import factories as F



class RunAdminTest(AdminTestCase):
    app_label = "execution"
    model_name = "run"


    def test_changelist(self):
        """Run changelist page loads without error, contains name."""
        F.RunFactory.create(name="Some Run")

        self.get(self.changelist_url).mustcontain("Some Run")


    def test_change_page(self):
        """Run change page loads without error, contains name."""
        r = F.RunFactory.create(name="Some Run")

        self.get(self.change_url(r)).mustcontain("Some Run")


    def test_change_page_suite(self):
        """Run change page includes RunSuite inline."""
        rs = F.RunSuiteFactory.create(
            run__name="Some Run", suite__name="A Suite")

        self.get(self.change_url(rs.run)).mustcontain("A Suite")


    def test_change_page_caseversion(self):
        """Run change page includes RunCaseVersion inline."""
        rcv = F.RunCaseVersionFactory.create(
            run__name="Some Run", caseversion__name="A Test Case Version")

        self.get(self.change_url(rcv.run)).mustcontain("A Test Case Version")
