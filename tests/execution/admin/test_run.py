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
Tests for Run admin.

"""
from ...admin import AdminTestCase
from ...library.builders import create_suite, create_caseversion
from ..builders import create_run, create_runsuite, create_runcaseversion



class RunAdminTest(AdminTestCase):
    app_label = "execution"
    model_name = "run"


    def test_changelist(self):
        """Run changelist page loads without error, contains name."""
        create_run(name="Some Run")

        self.get(self.changelist_url).mustcontain("Some Run")


    def test_change_page(self):
        """Run change page loads without error, contains name."""
        r = create_run(name="Some Run")

        self.get(self.change_url(r)).mustcontain("Some Run")


    def test_change_page_suite(self):
        """Run change page includes RunSuite inline."""
        r = create_run(name="Some Run")
        s = create_suite(name="A Suite")
        create_runsuite(run=r, suite=s)

        self.get(self.change_url(r)).mustcontain("A Suite")


    def test_change_page_caseversion(self):
        """Run change page includes RunCaseVersion inline."""
        r = create_run(name="Some Run")
        cv = create_caseversion(name="A Test Case Version")
        create_runcaseversion(run=r, caseversion=cv)

        self.get(self.change_url(r)).mustcontain("A Test Case Version")
