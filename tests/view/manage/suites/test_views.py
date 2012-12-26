# coding: utf-8
"""
Tests for suite management views.

"""
from django.core.urlresolvers import reverse

from tests import case



class SuitesTest(case.view.manage.ListViewTestCase,
                 case.view.ListFinderTests,
                 case.view.manage.MTModelListTests,
                 case.view.manage.StatusListTests,
                 case.view.NoCacheTest,
                 ):
    """Test for suites manage list view."""
    form_id = "manage-suites-form"
    perm = "manage_suites"


    @property
    def factory(self):
        """The model factory for this manage list."""
        return self.F.SuiteFactory


    @property
    def url(self):
        """Shortcut for manage-suites url."""
        return reverse("manage_suites")


    def test_filter_by_status(self):
        """Can filter by status."""
        self.factory.create(name="Foo 1", status=self.model.Suite.STATUS.active)
        self.factory.create(name="Foo 2", status=self.model.Suite.STATUS.draft)

        res = self.get(params={"filter-status": "active"})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_filter_by_product(self):
        """Can filter by product."""
        one = self.factory.create(name="Foo 1")
        self.factory.create(name="Foo 2")

        res = self.get(
            params={"filter-product": str(one.product.id)})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_filter_by_productversion(self):
        """Can filter by product of productversion."""
        pv1 = self.F.ProductVersionFactory()
        pv2 = self.F.ProductVersionFactory()
        one = self.factory.create(name="Foo 1", product=pv1.product)
        self.factory.create(name="Foo 2", product=pv2.product)

        res = self.get(
            params={"filter-productversion": str(pv1.id)})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_filter_by_run(self):
        """Can filter by run."""
        one = self.factory.create(name="Foo 1")
        rs = self.F.RunSuiteFactory.create(suite=one)
        self.factory.create(name="Foo 2")

        res = self.get(
            params={"filter-run": str(rs.run.id)})

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


    def test_filter_by_case_id(self):
        """Can filter by included case id."""
        one = self.factory.create(name="Foo 1")
        sc = self.F.SuiteCaseFactory.create(suite=one)
        self.factory.create(name="Foo 2")

        res = self.get(params={"filter-case": str(sc.case.id)})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_sort_by_status(self):
        """Can sort by status."""
        self.factory.create(name="Suite 1", status=self.model.Suite.STATUS.active)
        self.factory.create(name="Suite 2", status=self.model.Suite.STATUS.draft)

        res = self.get(
            params={"sortfield": "status", "sortdirection": "desc"})

        self.assertOrderInList(res, "Suite 2", "Suite 1")


    def test_sort_by_name(self):
        """Can sort by name."""
        self.factory.create(name="Suite 1")
        self.factory.create(name="Suite 2")

        res = self.get(
            params={"sortfield": "name", "sortdirection": "desc"})

        self.assertOrderInList(res, "Suite 2", "Suite 1")


    def test_sort_by_product(self):
        """Can sort by product."""
        pb = self.F.ProductFactory.create(name="B")
        pa = self.F.ProductFactory.create(name="A")
        self.factory.create(name="Foo 1", product=pb)
        self.factory.create(name="Foo 2", product=pa)

        res = self.get(
            params={"sortfield": "product", "sortdirection": "asc"})

        self.assertOrderInList(res, "Foo 2", "Foo 1")


    def test_link_to_manage_cases(self):
        """Contains link to manage cases in suite."""
        s = self.factory.create(name="Foo")

        res = self.get()

        self.assertElement(
            res.html,
            "a",
            href="{0}?filter-suite={1}".format(
                reverse("manage_cases"), str(s.id)
                )
            )


    def assertAddCaseLink(self, res, suite, count=1):
        """Assert that given response contains link to add case in suite."""
        self.assertElement(
            res.html,
            "a",
            href="{0}?product={1}&suite={2}".format(
                reverse("manage_case_add"), str(suite.product.id), str(suite.id)
                ),
            count=count
            )


    def assertNoAddCaseLink(self, res, suite):
        """Assert that response does not contain link to add case in suite."""
        self.assertAddCaseLink(res, suite, 0)


    def test_add_case_link(self):
        """Contains link to add case in this suite (with proper perms)."""
        self.add_perm("create_cases")
        self.add_perm("manage_suite_cases")
        s = self.factory.create(name="Foo")

        self.assertAddCaseLink(self.get(), s)


    def test_add_case_link_requires_manage_suite_case_perm(self):
        """No link to add case in suite if no manage_suite_case perm."""
        self.add_perm("create_cases")
        s = self.factory.create(name="Foo")

        self.assertNoAddCaseLink(self.get(), s)


    def test_add_case_link_requires_create_cases_perm(self):
        """No link to add case in suite if no create_cases perm."""
        self.add_perm("manage_suite_cases")
        s = self.factory.create(name="Foo")

        self.assertNoAddCaseLink(self.get(), s)



class SuiteDetailTest(case.view.AuthenticatedViewTestCase,
                      case.view.NoCacheTest,
                      ):
    """Test for suite-detail ajax view."""
    def setUp(self):
        """Setup for case details tests; create a suite."""
        super(SuiteDetailTest, self).setUp()
        self.testsuite = self.F.SuiteFactory.create()


    @property
    def url(self):
        """Shortcut for suite detail url."""
        return reverse(
            "manage_suite_details",
            kwargs=dict(suite_id=self.testsuite.id)
            )


    def test_details_description(self):
        """Details includes description, markdownified safely."""
        self.testsuite.description = "_foodesc_ <script>"
        self.testsuite.save()

        res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})

        res.mustcontain("<em>foodesc</em> &lt;script&gt;")



class AddSuiteTest(case.view.FormViewTestCase,
                   case.view.NoCacheTest,
                   ):
    """Tests for add suite view."""
    form_id = "suite-add-form"


    @property
    def url(self):
        """Shortcut for add-suite url."""
        return reverse("manage_suite_add")


    def setUp(self):
        """Add manage-suites permission to user."""
        super(AddSuiteTest, self).setUp()
        self.add_perm("manage_suites")


    def test_success(self):
        """Can add a suite with basic data."""
        p = self.F.ProductFactory.create()
        form = self.get_form()
        form["product"] = str(p.id)
        form["name"] = "Foo Suite ùê"
        form["description"] = "Foo desc"
        form["status"] = "active"

        res = form.submit(status=302)

        self.assertRedirects(res, reverse("manage_suites"))

        res.follow().mustcontain("Suite 'Foo Suite ùê' added.")

        s = p.suites.get()
        self.assertEqual(unicode(s.name), u"Foo Suite ùê")
        self.assertEqual(s.description, "Foo desc")
        self.assertEqual(s.status, "active")


    def test_error(self):
        """Bound form with errors is re-displayed."""
        res = self.get_form().submit()

        self.assertEqual(res.status_int, 200)
        res.mustcontain("This field is required.")


    def test_requires_manage_suites_permission(self):
        """Requires manage-suites permission."""
        res = self.app.get(
            self.url, user=self.F.UserFactory.create(), status=302)

        self.assertRedirects(res, "/")



class EditSuiteTest(case.view.FormViewTestCase,
                    case.view.NoCacheTest,
                    ):
    """Tests for edit-suite view."""
    form_id = "suite-edit-form"


    def setUp(self):
        """Setup for edit tests; create suite, add perm."""
        super(EditSuiteTest, self).setUp()
        self.suite = self.F.SuiteFactory.create()
        self.add_perm("manage_suites")


    @property
    def url(self):
        """Shortcut for edit-suite url."""
        return reverse(
            "manage_suite_edit", kwargs=dict(suite_id=self.suite.id))


    def test_requires_manage_suites_permission(self):
        """Requires manage-suites permission."""
        res = self.app.get(
            self.url, user=self.F.UserFactory.create(), status=302)

        self.assertRedirects(res, "/")


    def test_save_basic(self):
        """Can save updates; redirects to manage suites list."""
        form = self.get_form()
        form["name"] = "New Foo ùê"
        res = form.submit(status=302)

        self.assertRedirects(res, reverse("manage_suites"))

        res.follow().mustcontain("Saved 'New Foo ùê'.")

        r = self.refresh(self.suite)
        self.assertEqual(unicode(r.name), u"New Foo ùê")



    def test_errors(self):
        """Test bound form redisplay with errors."""
        form = self.get_form()
        form["name"] = ""
        res = form.submit(status=200)

        res.mustcontain("This field is required.")


    def test_concurrency_error(self):
        """Concurrency error is displayed."""
        form = self.get_form()

        self.suite.save()

        form["name"] = "New"
        res = form.submit(status=200)

        res.mustcontain("Another user saved changes to this object")
