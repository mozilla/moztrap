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
Tests for Assignment admin.

"""
from ...admin import AdminTestCase
from ..builders import (
    create_assignment, create_runcaseversion, create_run, create_result)



class AssignmentAdminTest(AdminTestCase):
    app_label = "execution"
    model_name = "assignment"


    def test_changelist(self):
        """Assignment changelist page loads without error, contains name."""
        create_assignment(
            runcaseversion=create_runcaseversion(
                run=create_run(name="Some Run")))

        self.get(self.changelist_url).mustcontain("Some Run")


    def test_change_page(self):
        """Assignment change page loads without error, contains name."""
        a = create_assignment(
            runcaseversion=create_runcaseversion(
                run=create_run(name="Some Run")))

        self.get(self.change_url(a)).mustcontain("Some Run")


    def test_change_page_result(self):
        """Assignment change page includes Result inline."""
        r = create_result(comment="Some comment")

        self.get(self.change_url(r.assignment)).mustcontain("Some comment")
