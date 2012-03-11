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
Tests for ProductVersion admin.

"""
from tests import case



class ProductVersionAdminTest(case.admin.AdminTestCase):
    app_label = "core"
    model_name = "productversion"


    def test_changelist(self):
        """ProductVersion changelist page loads without error, contains name."""
        self.F.ProductVersionFactory.create(
            product__name="Foo", version="1.0")

        self.get(self.changelist_url).mustcontain("Foo 1.0")


    def test_change_page(self):
        """ProductVersion change page loads without error, contains name."""
        pv = self.F.ProductVersionFactory.create(
            product__name="Foo", version="1.0")

        self.get(self.change_url(pv)).mustcontain("Foo 1.0")
