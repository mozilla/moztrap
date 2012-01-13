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
Tests for RunCaseVersion admin.

"""
from ...admin import AdminTestCase
from ... import factories as F



class RunCaseVersionAdminTest(AdminTestCase):
    app_label = "execution"
    model_name = "runcaseversion"


    def test_changelist(self):
        """RunCaseVersion changelist page loads without error, contains name."""
        F.RunCaseVersionFactory.create(run__name="Some Run")

        self.get(self.changelist_url).mustcontain("Some Run")


    def test_change_page(self):
        """RunCaseVersion change page loads without error, contains name."""
        rcv = F.RunCaseVersionFactory.create(run__name="Some Run")

        self.get(self.change_url(rcv)).mustcontain("Some Run")


    def test_change_page_suite(self):
        """RunCaseVersion change page includes Result inline."""
        r = F.ResultFactory.create(tester__username="sometester")

        self.get(self.change_url(r.runcaseversion)).mustcontain("sometester")
