"""
Tests for home view.

"""
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
