"""
Tests for suite results view.

"""
from django.core.urlresolvers import reverse

from tests import case

# from ...lists.runs import RunsListTests



class SuiteResultsViewTest(case.view.ListViewTestCase,
                           case.view.ListFinderTests,
                          ):
    """Tests for suite results view."""
    @property
    def url(self):
        """Shortcut for run results url."""
        return reverse("results_suites")

    def setUp(self):
        """Setup for suite tests"""
        self.testsuite1 = self.F.SuiteFactory.create(name="Suite Foo")
        self.testsuite2 = self.F.SuiteFactory.create(name="Suite Bar")


    def test_sort_by_name(self):
        res = self.get(
            params={"sortfield": "name", "sortdirection": "desc"})

        self.assertOrderInList(res, "Suite Foo", "Suite Bar")


    def test_sort_by_product(self):
        self.testsuite1.product.name = "Product A"
        self.testsuite1.product.save()
        self.testsuite2.product.name = "Product B"
        self.testsuite2.product.save()

        res = self.get(
            params={"sortfield": "product", "sortdirection": "desc"})

        self.assertOrderInList(res, "Suite Bar", "Suite Foo")


    def test_filter_by_result_passed(self):
        """The passed button in the Suite list item should have a link that
        filters for both suite and result."""
        self.assertTrue(False)


    def test_filter_by_result_failed(self):
        """The failed button in the Suite list item should have a link that
        filters for both suite and result."""
        self.assertTrue(False)


    def test_filter_by_result_invalid(self):
        """The invalid button in the Suite list item should have a link that
        filters for both suite and result."""
        self.assertTrue(False)


class SuiteDetailTest(case.view.AuthenticatedViewTestCase):
    """Test for suite-detail ajax view."""
    def setUp(self):
        """Setup for suite details tests; create a run."""
        super(SuiteDetailTest, self).setUp()
        self.testsuite = self.F.SuiteFactory.create()


    @property
    def url(self):
        """Shortcut for run detail url."""
        return reverse(
            "results_suite_details",
            kwargs=dict(suite_id=self.testsuite.id)
            )


    def test_details_description(self):
        """Details lists description."""
        self.testsuite.description = "foodesc"
        self.testsuite.save()

        res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})

        res.mustcontain("foodesc")


    # def test_details_envs(self):
    #     """Details lists envs."""
    #     self.testsuite.environments.add(
    #         *self.F.EnvironmentFactory.create_full_set({"OS": ["Windows"]}))
    #
    #     res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})
    #
    #     res.mustcontain("Windows")
    #
    #
    # def test_details_team(self):
    #     """Details lists team."""
    #     u = self.F.UserFactory.create(username="somebody")
    #     self.testsuite.add_to_team(u)
    #
    #     res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})
    #
    #     res.mustcontain("somebody")


    def test_details_drilldown(self):
        """Details contains link to drilldown to suites."""
        res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})

        res.mustcontain(
            "{0}?filter-suite={1}".format(
                reverse("results_runcaseversions"), self.testsuite.id)
            )
