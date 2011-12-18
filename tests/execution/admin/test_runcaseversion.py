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
Tests for RunCaseVersion admin.

"""
from ...admin import AdminTestCase
from ...core.builders import create_user
from ..builders import create_runcaseversion, create_run, create_assignment



class RuncaseversionAdminTest(AdminTestCase):
    app_label = "execution"
    model_name = "runcaseversion"


    def test_changelist(self):
        """RunCaseVersion changelist page loads without error, contains name."""
        create_runcaseversion(run=create_run(name="Some Run"))

        self.get(self.changelist_url).mustcontain("Some Run")


    def test_change_page(self):
        """RunCaseVersion change page loads without error, contains name."""
        r = create_runcaseversion(run=create_run(name="Some Run"))

        self.get(self.change_url(r)).mustcontain("Some Run")


    def test_change_page_suite(self):
        """RunCaseVersion change page includes Assignment inline."""
        a = create_assignment(tester=create_user(username="sometester"))

        self.get(self.change_url(a.runcaseversion)).mustcontain("sometester")
