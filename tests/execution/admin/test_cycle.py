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
Tests for Cycle admin.

"""
from ...admin import AdminTestCase

from ..builders import create_cycle, create_run



class CycleAdminTest(AdminTestCase):
    app_label = "execution"
    model_name = "cycle"


    def test_changelist(self):
        """Cycle changelist page loads without error, contains name."""
        create_cycle(name="Some Cycle")

        self.get(self.changelist_url).mustcontain("Some Cycle")


    def test_change_page(self):
        """Cycle change page loads without error, contains name."""
        s = create_cycle(name="Some Cycle")

        self.get(self.change_url(s)).mustcontain("Some Cycle")


    def test_change_page_run(self):
        """Cycle change page includes Run inline."""
        s = create_run(name="Some Run")

        self.get(self.change_url(s.cycle)).mustcontain("Some Run")
