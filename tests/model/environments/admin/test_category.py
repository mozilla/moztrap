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
Tests for Category admin.

"""
from tests import case



class CategoryAdminTest(case.admin.AdminTestCase):
    app_label = "environments"
    model_name = "category"


    def test_changelist(self):
        """Category changelist page loads without error, contains name."""
        self.F.CategoryFactory.create(name="Operating System")

        self.get(self.changelist_url).mustcontain("Operating System")


    def test_change_page(self):
        """Category change page loads without error, contains name."""
        s = self.F.CategoryFactory.create(name="Operating System")

        self.get(self.change_url(s)).mustcontain("Operating System")


    def test_change_page_element(self):
        """Category change page includes Element inline."""
        e = self.F.ElementFactory.create(name="Linux")

        self.get(self.change_url(e.category)).mustcontain("Linux")
