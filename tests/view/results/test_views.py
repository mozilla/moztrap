"""
Tests for home results view.

"""
from django.core.urlresolvers import reverse

from tests import case



class ResultsHomeViewTest(case.view.AuthenticatedViewTestCase):
    """Tests for results home view."""
    @property
    def url(self):
        """Shortcut for results url."""
        return reverse("results")


    def test_redirects_to_runs_with_open_finder(self):
        """Redirects to the active runs list, with results finder open."""
        res = self.get(status=302)

        self.assertRedirects(
            res, reverse("results_runs") + "?openfinder=1&filter-status=active")
