"""
Tests for home view.

"""
import json

from django.core.urlresolvers import reverse

from tests import case


class HomeViewTest(case.view.AuthenticatedViewTestCase):
    """Tests for home view."""
    @property
    def url(self):
        """Shortcut for home url."""
        return reverse("home")

    def test_execute_permission_redirects_to_runtests(self):
        """Users with execute permission are directed to run-tests page."""
        self.add_perm("execute")
        res = self.get(status=302)

        self.assertRedirects(res, reverse("runtests"))

    def test_no_permission_redirects_to_results(self):
        """Users without execute permission are directed to results."""
        res = self.get(status=302)

        self.assertRedirects(res, reverse("results_runs"))


class ContributeJSONViewTest(case.view.ViewTestCase):
    """Test specifically for the /contribute.json endpoint."""
    @property
    def url(self):
        return "/contribute.json"


    def test_view_contribute_json(self):
        res = self.get(status=200)
        self.assertEqual(res.headers["Content-Type"], "application/json")
        self.assertTrue(json.loads(res.content))
