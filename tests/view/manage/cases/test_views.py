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
from datetime import datetime

from django.core.urlresolvers import reverse

from django.contrib.auth.models import Permission

from .... import factories as F
from ....utils import refresh
from ...base import AuthenticatedViewTestCase



class CasesTest(AuthenticatedViewTestCase):
    """Test for cases manage list view."""
    @property
    def url(self):
        """Shortcut for manage-cases url."""
        return reverse("manage_cases")


    def get_form(self):
        """Get the manage-cases form."""
        return self.get().forms["manage-cases-form"]


    def assertInList(self, response, name, count=1):
        """Assert that caseversion ``name`` is in the list ``count`` times."""
        # One occurrence in the list = two occurrences of the name in HTML
        actual = response.body.count(name)
        self.assertEqual(
            actual, count * 2,
            "'{0}' is in the list {1} times, not {2}.".format(
                name, actual, count))


    def assertNotInList(self, response, name):
        """Assert that caseversion ``name`` is not in the list."""
        self.assertInList(response, name, 0)


    def assertOrderInList(self, response, *names):
        """Assert that ``names`` appear in list in given order."""
        indices = []
        for name in names:
            try:
                indices.append((response.body.index(name), name))
            except ValueError:
                self.fail("{0} does not appear in response.".format(name))

        actual_order = sorted(indices, key=lambda t: t[0])

        self.assertEqual(
            [t[1] for t in actual_order],
            [t[1] for t in indices],
            )


    def assertActionRequiresPermission(self, action, permission):
        """Assert that the given list action requires the given permission."""
        cv = F.CaseVersionFactory.create()

        form = self.get_form()

        name = "action-{0}".format(action)

        # action button not shown to the user
        self.assertTrue(name not in form.fields)

        # ...but if they cleverly submit it anyway they get a 403...
        res = self.post(
            {
                name: str(cv.id),
                "csrfmiddlewaretoken":
                    form.fields.get("csrfmiddlewaretoken")[0].value
                },
            status=403,
            )

        # ...with a message about permissions.
        res.mustcontain("permission")


    def test_login_required(self):
        """Requires login."""
        response = self.app.get(self.url)

        self.assertEqual(response.status_int, 302)


    def test_lists_cases(self):
        """Displays a list of cases."""
        F.CaseVersionFactory.create(name="Foo Bar")

        res = self.get()

        res.mustcontain("Foo Bar")


    def test_lists_latest_versions(self):
        """Lists only latest version of each case."""
        cv = F.CaseVersionFactory.create(
            name="Old Version", productversion__version="1.0")
        F.CaseVersionFactory.create(
            name="Latest Version",
            case=cv.case,
            productversion__product=cv.productversion.product,
            productversion__version="2.0")

        res = self.get()

        self.assertNotInList(res, "Old Version")
        self.assertInList(res, "Latest Version")


    def test_delete(self):
        """Can delete objects from list."""
        self.add_perm("manage_cases")

        cv = F.CaseVersionFactory.create()

        self.get_form().submit(name="action-delete", index=0)

        self.assertTrue(bool(refresh(cv).deleted_on))


    def test_delete_requires_manage_cases_permission(self):
        """Deleting requires manage_cases permission."""
        self.assertActionRequiresPermission("delete", "manage_cases")


    def test_clone(self):
        """Can clone objects in list."""
        self.add_perm("manage_cases")

        F.CaseVersionFactory.create()

        self.get_form().submit(name="action-clone", index=0)

        from cc.model import Case
        self.assertEqual(Case.objects.count(), 2)


    def test_clone_requires_manage_cases_permission(self):
        """Cloning requires manage_cases permission."""
        self.assertActionRequiresPermission("clone", "manage_cases")


    def test_activate(self):
        """Can activate objects in list."""
        self.add_perm("manage_cases")

        cv = F.CaseVersionFactory.create(status="draft")

        self.get_form().submit(name="action-activate", index=0)

        self.assertEqual(refresh(cv).status, "active")


    def test_activate_requires_manage_cases_permission(self):
        """Activating requires manage_cases permission."""
        self.assertActionRequiresPermission("activate", "manage_cases")


    def test_deactivate(self):
        """Can deactivate objects in list."""
        self.add_perm("manage_cases")

        cv = F.CaseVersionFactory.create(status="active")

        self.get_form().submit(name="action-deactivate", index=0)

        self.assertEqual(refresh(cv).status, "disabled")


    def test_deactivate_requires_manage_cases_permission(self):
        """Deactivating requires manage_cases permission."""
        self.assertActionRequiresPermission("deactivate", "manage_cases")


    def test_filter_by_status(self):
        """Can filter by status."""
        F.CaseVersionFactory.create(status="draft", name="Case 1")
        F.CaseVersionFactory.create(status="active", name="Case 2")

        res = self.get(params={"filter-status": "draft"})

        self.assertInList(res, "Case 1")
        self.assertNotInList(res, "Case 2")


    def test_filter_by_id(self):
        """Can filter by id."""
        cv1 = F.CaseVersionFactory.create(name="Case 1")
        F.CaseVersionFactory.create(name="Case 2")

        res = self.get(params={"filter-id": cv1.case.id})

        self.assertInList(res, "Case 1")
        self.assertNotInList(res, "Case 2")


    def test_filter_by_name(self):
        """Can filter by id."""
        F.CaseVersionFactory.create(name="Case 1")
        F.CaseVersionFactory.create(name="Case 2")

        res = self.get(params={"filter-name": "1"})

        self.assertInList(res, "Case 1")
        self.assertNotInList(res, "Case 2")


    def test_filter_by_tag(self):
        """Can filter by tag."""
        t = F.TagFactory.create()
        cv = F.CaseVersionFactory.create(name="Case 1")
        cv.tags.add(t)
        F.CaseVersionFactory.create(name="Case 2")

        res = self.get(params={"filter-tag": t.id})

        self.assertInList(res, "Case 1")
        self.assertNotInList(res, "Case 2")


    def test_filter_by_product(self):
        """Can filter by product."""
        cv = F.CaseVersionFactory.create(name="Case 1")
        F.CaseVersionFactory.create(name="Case 2")

        res = self.get(params={"filter-product": cv.case.product.id})

        self.assertInList(res, "Case 1")
        self.assertNotInList(res, "Case 2")


    def test_filter_by_productversion(self):
        """Can filter by product version; no implicit filter by latest."""
        cv = F.CaseVersionFactory.create(name="Case 1")
        F.CaseVersionFactory.create(
            name="Case 2",
            case=cv.case,
            productversion__product=cv.productversion.product,
            productversion__version="2.0")

        res = self.get(params={"filter-productversion": cv.productversion.id})

        self.assertInList(res, "Case 1")
        self.assertNotInList(res, "Case 2")


    def test_filter_by_step_instruction(self):
        """Can filter by step instruction."""
        F.CaseStepFactory.create(
            caseversion__name="Case 1", instruction="do this")
        F.CaseStepFactory.create(
            caseversion__name="Case 2", instruction="do that")

        res = self.get(params={"filter-instruction": "this"})

        self.assertInList(res, "Case 1")
        self.assertNotInList(res, "Case 2")


    def test_filter_by_step_expected_result(self):
        """Can filter by step expected result."""
        F.CaseStepFactory.create(
            caseversion__name="Case 1", expected="see this")
        F.CaseStepFactory.create(
            caseversion__name="Case 2", expected="see that")

        res = self.get(params={"filter-expected": "this"})

        self.assertInList(res, "Case 1")
        self.assertNotInList(res, "Case 2")


    def test_filter_by_creator(self):
        """Can filter by creator."""
        F.CaseVersionFactory.create(name="Case 1", user=self.user)
        F.CaseVersionFactory.create(name="Case 2")

        res = self.get(params={"filter-creator": self.user.id})

        self.assertInList(res, "Case 1")
        self.assertNotInList(res, "Case 2")


    def test_filter_by_env_elements(self):
        """Can filter by environment elements."""
        envs = F.EnvironmentFactory.create_full_set(
            {"OS": ["Linux", "Windows"]})
        F.CaseVersionFactory.create(name="Case 1", environments=envs)
        F.CaseVersionFactory.create(name="Case 2", environments=envs[1:])

        res = self.get(
            params={"filter-envelement": envs[0].elements.all()[0].id})

        self.assertInList(res, "Case 1")
        self.assertNotInList(res, "Case 2")


    def test_filter_by_suite(self):
        """Can filter by suite."""
        cv = F.CaseVersionFactory.create(name="Case 1")
        F.CaseVersionFactory.create(name="Case 2")
        sc = F.SuiteCaseFactory.create(case=cv.case)

        res = self.get(params={"filter-suite": sc.suite.id})

        self.assertInList(res, "Case 1")
        self.assertNotInList(res, "Case 2")


    def test_default_sort_by_last_created(self):
        """Default sort is by latest created first."""
        F.CaseVersionFactory.create(
            name="Case 1", created_on=datetime(2012, 1, 21))
        F.CaseVersionFactory.create(
            name="Case 2", created_on=datetime(2012, 1, 22))

        res = self.get()

        self.assertOrderInList(res, "Case 2", "Case 1")


    def test_sort_by_status(self):
        """Can sort by status."""
        F.CaseVersionFactory.create(name="Case 1", status="draft")
        F.CaseVersionFactory.create(name="Case 2", status="active")

        res = self.get(params={"sortfield": "status", "sortdirection": "asc"})

        self.assertOrderInList(res, "Case 2", "Case 1")


    def test_sort_by_name(self):
        """Can sort by name."""
        F.CaseVersionFactory.create(name="Case 1")
        F.CaseVersionFactory.create(name="Case 2")

        res = self.get(params={"sortfield": "name", "sortdirection": "desc"})

        self.assertOrderInList(res, "Case 2", "Case 1")



class CaseDetailTest(AuthenticatedViewTestCase):
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



class AddCaseTest(AuthenticatedViewTestCase):
    """Tests for add-case-single view."""
    @property
    def url(self):
        """Shortcut for add-case-single url."""
        return reverse("manage_case_add")


    def setUp(self):
        """Add create-cases permission to user."""
        super(AddCaseTest, self).setUp()
        self.add_perm("create_cases")


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
        form["status"] = "active"
        res = form.submit()

        self.assertEqual(res.status_int, 302)
        self.assertEqual(res["Location"], "http://testserver/manage/cases/")

        from cc.model import CaseVersion
        cv = CaseVersion.objects.get()
        self.assertEqual(cv.case.product, pv.product)
        self.assertEqual(cv.productversion, pv)
        self.assertEqual(cv.name, "Can log in.")
        self.assertEqual(cv.description, "Tests that a user can log in.")
        self.assertEqual(cv.status, "active")
        step = cv.steps.get()
        self.assertEqual(step.instruction, "Type creds and click login.")
        self.assertEqual(step.expected, "You should see a welcome message.")


    def test_error(self):
        """Bound form with errors is re-displayed."""
        res = self.get_form().submit()

        self.assertEqual(res.status_int, 200)
        res.mustcontain("This field is required.")
