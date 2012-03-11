# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-2012 Mozilla
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
