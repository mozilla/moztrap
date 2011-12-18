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
from mock import patch

from ..base import AdminTestCase

from ...library.builders import create_caseversion, create_casestep, create_case
from ...utils import refresh



class CaseVersionAdminTest(AdminTestCase):
    app_label = "library"
    model_name = "caseversion"


    def test_changelist(self):
        """CaseVersion changelist page loads without error, contains name."""
        create_caseversion(name="Can load a website")

        self.get(self.changelist_url).mustcontain("Can load a website")


    def test_change_page(self):
        """CaseVersion change page loads without error, contains name."""
        p = create_caseversion(name="Can load a website")

        self.get(self.change_url(p)).mustcontain("Can load a website")


    def test_change_page_step(self):
        """CaseVersion change page includes CaseStep inline."""
        s = create_casestep(instruction="Type a URL in the address bar")

        self.get(self.change_url(s.caseversion)).mustcontain(
            "Type a URL in the address bar")


    def test_add_step_with_caseversion(self):
        case = create_case()

        # patching extra avoids need for JS to add step
        with patch("cc.library.admin.CaseStepInline.extra", 1):
            form = self.get(self.add_url).forms[0]
            form["case"] = str(case.id)
            form["number"] = "1"
            form["name"] = "Some case"
            form["steps-0-number"] = "1"
            form["steps-0-instruction"] = "An instruction"
            form["steps-0-expected"] = "A result"
            res = form.submit()
        self.assertEqual(res.status_int, 302)

        self.assertEqual(
            case.versions.get().steps.get().instruction, "An instruction")


    def test_add_step_tracks_user(self):
        """Adding a CaseStep via inline tracks created-by user."""
        cv = create_caseversion()

        # patching extra avoids need for JS to submit new step
        with patch("cc.library.admin.CaseStepInline.extra", 1):
            form = self.get(self.change_url(cv)).forms[0]
            form["steps-0-number"] = "1"
            form["steps-0-instruction"] = "An instruction"
            form["steps-0-expected"] = "A result"
            res = form.submit()
        self.assertEqual(res.status_int, 302)

        s = cv.steps.get()

        self.assertEqual(s.created_by, self.user)


    def test_change_step_tracks_user(self):
        """Modifying a CaseStep via inline tracks modified-by user."""
        s = create_casestep(instruction="Type a URL in the address bar")

        form = self.get(self.change_url(s.caseversion)).forms[0]
        form["steps-0-instruction"] = "A new instruction"
        res = form.submit()
        self.assertEqual(res.status_int, 302)

        self.assertEqual(refresh(s).modified_by, self.user)


    def test_delete_step_tracks_user(self):
        """Deleting a CaseStep via inline tracks modified-by user."""
        s = create_casestep()

        form = self.get(self.change_url(s.caseversion)).forms[0]
        form["steps-0-DELETE"] = True
        res = form.submit()
        self.assertEqual(res.status_int, 302)

        self.assertEqual(refresh(s).deleted_by, self.user)