"""
Tests for run management views.

"""
from datetime import date

from django.core.urlresolvers import reverse

from tests import case

from ...lists.runs import RunsListTests



class RunsTest(case.view.manage.ListViewTestCase,
               RunsListTests,
               case.view.ListFinderTests,
               case.view.manage.CCModelListTests,
               case.view.manage.StatusListTests,
               case.view.NoCacheTest,
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



class RunDetailTest(case.view.AuthenticatedViewTestCase,
                    case.view.NoCacheTest,
                    ):
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



class AddRunTest(case.view.FormViewTestCase,
                 case.view.NoCacheTest,
                 ):
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


    def test_non_field_error(self):
        """Non-field errors are displayed"""
        form = self.get_form()

        form["start"] = "2012-3-1"
        form["end"] = "2012-2-1"

        res = form.submit()

        self.assertEqual(res.status_int, 200)
        res.mustcontain("Start date must be prior to end date.")


    def test_requires_manage_runs_permission(self):
        """Requires manage-runs permission."""
        res = self.app.get(
            self.url, user=self.F.UserFactory.create(), status=302)

        self.assertRedirects(res, "/")



class EditRunTest(case.view.FormViewTestCase,
                  case.view.NoCacheTest,
                  ):
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

        self.assertRedirects(res, "/")


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


    def test_concurrency_error(self):
        """Concurrency error is displayed."""
        form = self.get_form()

        self.testrun.save()

        form["name"] = "New"
        res = form.submit(status=200)

        res.mustcontain("Another user saved changes to this object")
