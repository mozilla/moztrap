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
Tests for login/logout/account views.

"""
from django.core.urlresolvers import reverse

from ... import factories as F
from ...views import ViewTestCase



class CasesTest(ViewTestCase):
    """Test for cases manage list view."""
    @property
    def url(self):
        """Shortcut for manage-cases url."""
        return reverse("manage_cases")


    def get(self):
        """Shortcut for getting manage-cases url authenticated."""
        return self.app.get(self.url, user=self.user)


    def test_lists_cases(self):
        """Manage-cases view displays a list of cases."""
        F.CaseVersionFactory.create(name="Foo Bar")

        res = self.get()

        res.mustcontain("Foo Bar")
