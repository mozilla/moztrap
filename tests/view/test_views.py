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
Tests for home view.

"""
from django.core.urlresolvers import reverse

from . import base



class HomeViewTest(base.AuthenticatedViewTestCase):
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


    def test_no_permission_redirects_to_manage_cases(self):
        """Users without execute permission are directed to manage-cases."""
        res = self.get(status=302)

        self.assertRedirects(res, reverse("manage_cases"))
