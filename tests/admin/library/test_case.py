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
Tests for Case admin.

"""
from ..base import AdminTestCase

from ...library.builders import create_case, create_caseversion


class CaseAdminTest(AdminTestCase):
    app_label = "library"
    model_name = "case"


    def test_changelist(self):
        """Case changelist page loads without error, contains id."""
        c = create_case()

        self.get(self.changelist_url).mustcontain(c.id)


    def test_change_page(self):
        """Case change page loads without error, contains id."""
        c = create_case()

        self.get(self.change_url(c)).mustcontain(c.id)


    def test_change_page_version(self):
        """Case change page includes CaseVersion inline."""
        cv = create_caseversion(name="Can load a website")

        self.get(self.change_url(cv.case)).mustcontain(
            "Can load a website")
