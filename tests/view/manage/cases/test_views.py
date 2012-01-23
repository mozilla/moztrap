# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-12 Mozilla
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
Tests for case management views.

"""
from django.core.urlresolvers import reverse

from django.contrib.auth.models import Permission

from cc.model.library.models import CaseVersion

from .... import factories as F
from ...base import ViewTestCase



class CasesTest(ViewTestCase):
    """Test for cases manage list view."""
    @property
    def url(self):
        """Shortcut for manage-cases url."""
        return reverse("manage_cases")


    def get(self):
        """Shortcut for getting manage-cases url authenticated."""
        return self.app.get(self.url, user=self.user)


    def test_lists_cases(self):
        """Manage-cases view displays a list of cases."""
        F.CaseVersionFactory.create(name="Foo Bar")

        res = self.get()

        res.mustcontain("Foo Bar")



class CaseDetailTest(ViewTestCase):
    """Test for case-detail ajax view."""
    def test_details(self):
        """Returns details HTML snippet for given caseversion."""
        step = F.CaseStepFactory.create(instruction="Frobnigate.")
        res = self.app.get(
            reverse(
                "manage_case_details",
                kwargs=dict(caseversion_id=step.caseversion.id)
                ),
            user=self.user,
            headers=dict(HTTP_X_REQUESTED_WITH="XMLHttpRequest"),
            )

        res.mustcontain("Frobnigate.")



class AddCaseTest(ViewTestCase):
    """Tests for add-case-single view."""
    @property
    def url(self):
        """Shortcut for add-case-single url."""
        return reverse("manage_case_add")


    def setUp(self):
        """Add create-cases permission to user."""
        super(AddCaseTest, self).setUp()
        perm = Permission.objects.get(codename="create_cases")
        self.user.user_permissions.add(perm)


    def get(self):
        """Shortcut for getting add-case-single url authenticated."""
        return self.app.get(self.url, user=self.user)


    def get_form(self):
        """Get single case add form."""
        return self.get().forms["single-case-add"]


    def test_success(self):
        """Can add a test case with basic data, including a step."""
        pv = F.ProductVersionFactory.create()

        form = self.get_form()
        form["product"] = pv.product.id
        form["productversion"] = pv.id
        form["name"] = "Can log in."
        form["description"] = "Tests that a user can log in."
        form["steps-0-instruction"] = "Type creds and click login."
        form["steps-0-expected"] = "You should see a welcome message."
        res = form.submit()

        self.assertEqual(res.status_int, 302)
        self.assertEqual(res["Location"], "http://testserver/manage/cases/")

        cv = CaseVersion.objects.get()
        self.assertEqual(cv.case.product, pv.product)
        self.assertEqual(cv.productversion, pv)
        self.assertEqual(cv.name, "Can log in.")
        self.assertEqual(cv.description, "Tests that a user can log in.")
        step = cv.steps.get()
        self.assertEqual(step.instruction, "Type creds and click login.")
        self.assertEqual(step.expected, "You should see a welcome message.")


    def test_error(self):
        """Bound form with errors is re-displayed."""
        res = self.get_form().submit()

        self.assertEqual(res.status_int, 200)
        res.mustcontain("This field is required.")
