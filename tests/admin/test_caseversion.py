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
Tests for CaseVersion admin.

"""
from .base import AdminTestCase

from ..library.builders import create_caseversion, create_casestep



class CaseVersionAdminTest(AdminTestCase):
    app_label = "library"
    model_name = "caseversion"


    def test_changelist(self):
        """CaseVersion changelist page loads without error, contains name."""
        create_caseversion(name="Can load a website")

        self.get(self.changelist_url).mustcontain("Can load a website")


    def test_change(self):
        """CaseVersion change page loads without error, contains name."""
        p = create_caseversion(name="Can load a website")

        self.get(self.change_url(p)).mustcontain("Can load a website")


    def test_change_step(self):
        """CaseVersion change page includes CaseStep inline."""
        s = create_casestep(instruction="Type a URL in the address bar")

        self.get(self.change_url(s.caseversion)).mustcontain(
            "Type a URL in the address bar")
