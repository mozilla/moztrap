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
Tests for run management views.

"""
from datetime import date

from django.core.urlresolvers import reverse

from tests import case



class RunsTest(case.view.manage.ListViewTestCase,
               case.view.manage.ListFinderTests,
               case.view.manage.CCModelListTests,
               case.view.manage.StatusListTests
               ):
    """Test for runs manage list view."""
    form_id = "manage-runs-form"
    perm = "manage_runs"


    @property
    def factory(self):
        """The model factory for this manage list."""
        return self.F.RunFactory


    @property
    def url(self):
        """Shortcut for manage-runs url."""
        return reverse("manage_runs")


    def test_filter_by_status(self):
        """Can filter by status."""
        self.factory.create(name="Foo 1", status=self.model.Run.STATUS.active)
        self.factory.create(name="Foo 2", status=self.model.Run.STATUS.draft)

        res = self.get(params={"filter-status": "active"})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_filter_by_product(self):
        """Can filter by product."""
        one = self.factory.create(name="Foo 1")
        self.factory.create(name="Foo 2")

        res = self.get(
            params={"filter-product": str(one.productversion.product.id)})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_filter_by_productversion(self):
        """Can filter by product version."""
        one = self.factory.create(name="Foo 1")
        self.factory.create(name="Foo 2")

        res = self.get(
            params={"filter-productversion": str(one.productversion.id)})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_filter_by_name(self):
        """Can filter by name."""
        self.factory.create(name="Foo 1")
        self.factory.create(name="Foo 2")

        res = self.get(params={"filter-name": "1"})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_filter_by_description(self):
        """Can filter by name."""
        self.factory.create(name="Foo 1", description="foo bar")
        self.factory.create(name="Foo 2", description="bar baz")

        res = self.get(params={"filter-description": "foo"})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_filter_by_suite(self):
        """Can filter by included suite."""
        one = self.factory.create(name="Foo 1")
        rs = self.F.RunSuiteFactory(run=one)
        self.factory.create(name="Foo 2")

        res = self.get(params={"filter-suite": str(rs.suite.id)})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_filter_by_case_id(self):
        """Can filter by included case id."""
        one = self.factory.create(name="Foo 1")
        rs = self.F.RunSuiteFactory.create(run=one)
        sc = self.F.SuiteCaseFactory.create(suite=rs.suite)
        self.factory.create(name="Foo 2")

        res = self.get(params={"filter-case": str(sc.case.id)})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_filter_by_env_elements(self):
        """Can filter by environment elements."""
        envs = self.F.EnvironmentFactory.create_full_set(
            {"OS": ["Linux", "Windows"]})
        self.factory.create(name="Foo 1", environments=envs)
        self.factory.create(name="Foo 2", environments=envs[1:])

        res = self.get(
            params={"filter-envelement": envs[0].elements.all()[0].id})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_sort_by_status(self):
        """Can sort by status."""
        self.factory.create(name="Run 1", status=self.model.Run.STATUS.active)
        self.factory.create(name="Run 2", status=self.model.Run.STATUS.draft)

        res = self.get(
            params={"sortfield": "status", "sortdirection": "desc"})

        self.assertOrderInList(res, "Run 2", "Run 1")


    def test_sort_by_name(self):
        """Can sort by name."""
        self.factory.create(name="Run 1")
        self.factory.create(name="Run 2")

        res = self.get(
            params={"sortfield": "name", "sortdirection": "desc"})

        self.assertOrderInList(res, "Run 2", "Run 1")


    def test_sort_by_productversion(self):
        """Can sort by productversion."""
        pb = self.F.ProductFactory.create(name="B")
        pa = self.F.ProductFactory.create(name="A")
        self.factory.create(
            name="x", productversion__product=pb, productversion__version="2")
        self.factory.create(
            name="y", productversion__product=pb, productversion__version="1")
        self.factory.create(
            name="z", productversion__product=pa, productversion__version="1")

        res = self.get(
            params={"sortfield": "productversion", "sortdirection": "asc"})

        self.assertOrderInList(res, "z", "y", "x")


    def test_sort_by_start(self):
        """Can sort by start."""
        self.factory.create(name="Run 1", start=date(2012, 1, 5))
        self.factory.create(name="Run 2", start=date(2012, 1, 10))

        res = self.get(
            params={"sortfield": "start", "sortdirection": "desc"})

        self.assertOrderInList(res, "Run 2", "Run 1")


    def test_sort_by_end(self):
        """Can sort by end."""
        self.factory.create(name="Run 1", end=date(2012, 1, 15))
        self.factory.create(name="Run 2", end=date(2012, 1, 10))

        res = self.get(
            params={"sortfield": "end", "sortdirection": "asc"})

        self.assertOrderInList(res, "Run 2", "Run 1")



class RunDetailTest(case.view.AuthenticatedViewTestCase):
    """Test for run-detail ajax view."""
    def setUp(self):
        """Setup for case details tests; create a run."""
        super(RunDetailTest, self).setUp()
        self.testrun = self.F.RunFactory.create()


    @property
    def url(self):
        """Shortcut for run detail url."""
        return reverse(
            "manage_run_details",
            kwargs=dict(run_id=self.testrun.id)
            )


    def test_details_description(self):
        """Details lists description."""
        self.testrun.description = "foodesc"
        self.testrun.save()

        res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})

        res.mustcontain("foodesc")


    def test_details_envs(self):
        """Details lists envs."""
        self.testrun.environments.add(
            *self.F.EnvironmentFactory.create_full_set({"OS": ["Windows"]}))

        res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})

        res.mustcontain("Windows")


    def test_details_suites(self):
        """Details lists suites."""
        self.F.RunSuiteFactory.create(run=self.testrun, suite__name="Foo Suite")

        res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})

        res.mustcontain("Foo Suite")


    def test_details_team(self):
        """Details lists team."""
        u = self.F.UserFactory.create(username="somebody")
        self.testrun.add_to_team(u)

        res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})

        res.mustcontain("somebody")



class AddRunTest(case.view.FormViewTestCase):
    """Tests for add run view."""
    form_id = "run-add-form"


    @property
    def url(self):
        """Shortcut for add-run url."""
        return reverse("manage_run_add")


    def setUp(self):
        """Add manage-runs permission to user."""
        super(AddRunTest, self).setUp()
        self.add_perm("manage_runs")


    def test_success(self):
        """Can add a run with basic data."""
        pv = self.F.ProductVersionFactory.create()
        form = self.get_form()
        form["productversion"] = str(pv.id)
        form["name"] = "Foo Run"
        form["description"] = "Foo desc"
        form["start"] = "2012-1-2"
        form["end"] = "2012-1-20"

        res = form.submit(status=302)

        self.assertRedirects(res, reverse("manage_runs"))

        res.follow().mustcontain("Run 'Foo Run' added.")

        r = pv.runs.get()
        self.assertEqual(r.name, "Foo Run")
        self.assertEqual(r.description, "Foo desc")
        self.assertEqual(r.start, date(2012, 1, 2))
        self.assertEqual(r.end, date(2012, 1, 20))


    def test_error(self):
        """Bound form with errors is re-displayed."""
        res = self.get_form().submit()

        self.assertEqual(res.status_int, 200)
        res.mustcontain("This field is required.")


    def test_requires_manage_runs_permission(self):
        """Requires manage-runs permission."""
        res = self.app.get(
            self.url, user=self.F.UserFactory.create(), status=302)

        self.assertRedirects(res, reverse("auth_login") + "?next=" + self.url)



class EditRunTest(case.view.FormViewTestCase):
    """Tests for edit-run view."""
    form_id = "run-edit-form"


    def setUp(self):
        """Setup for edit tests; create run, add perm."""
        super(EditRunTest, self).setUp()
        self.testrun = self.F.RunFactory.create()
        self.add_perm("manage_runs")


    @property
    def url(self):
        """Shortcut for edit-run url."""
        return reverse(
            "manage_run_edit", kwargs=dict(run_id=self.testrun.id))


    def test_requires_manage_runs_permission(self):
        """Requires manage-runs permission."""
        res = self.app.get(
            self.url, user=self.F.UserFactory.create(), status=302)

        self.assertRedirects(res, reverse("auth_login") + "?next=" + self.url)


    def test_save_basic(self):
        """Can save updates; redirects to manage runs list."""
        form = self.get_form()
        form["name"] = "New Foo"
        res = form.submit(status=302)

        self.assertRedirects(res, reverse("manage_runs"))

        res.follow().mustcontain("Saved 'New Foo'.")

        r = self.refresh(self.testrun)
        self.assertEqual(r.name, "New Foo")



    def test_errors(self):
        """Test bound form redisplay with errors."""
        form = self.get_form()
        form["name"] = ""
        res = form.submit(status=200)

        res.mustcontain("This field is required.")


    def test_active_run_product_version_readonly(self):
        """If editing active run, product version field is read only."""
        self.testrun.status = self.testrun.STATUS.active
        self.testrun.save()
        pv = self.testrun.productversion

        res = self.get()

        div = res.html.find("div", "product-version-field")
        self.assertEqual(div.find("span", "value").text, unicode(pv))
        self.assertEqual(
            div.find(
                "input",
                attrs={"name": "productversion", "type": "hidden"}
                )["value"],
            unicode(pv.id)
            )
