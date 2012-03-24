"""
Tests for home management view.

"""
from django.core.urlresolvers import reverse

from tests import case



class ManageHomeViewTest(case.view.AuthenticatedViewTestCase):
    """Tests for manage home view."""
    @property
    def url(self):
        """Shortcut for manage url."""
        return reverse("manage")


    def test_redirects_to_manage_runs_with_open_finder(self):
        """Redirects to the manage runs list, with manage finder open."""
        res = self.get(status=302)

        self.assertRedirects(res, reverse("manage_runs") + "?openfinder=1")
