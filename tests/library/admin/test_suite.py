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
Tests for Suite admin.

"""
from ...admin import AdminTestCase
from ... import factories as F



class SuiteAdminTest(AdminTestCase):
    app_label = "library"
    model_name = "suite"


    def test_changelist(self):
        """Suite changelist page loads without error, contains name."""
        F.SuiteFactory.create(name="Performance")

        self.get(self.changelist_url).mustcontain("Performance")


    def test_change_page(self):
        """Suite change page loads without error, contains name."""
        s = F.SuiteFactory.create(name="Performance")

        self.get(self.change_url(s)).mustcontain("Performance")
