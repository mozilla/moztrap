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
Utility base TestCase for testing views.

"""
from django.utils.unittest import TestSuite

from django_webtest import WebTest

from .. import factories as F



class AuthenticatedViewTestCase(WebTest):
    """Base test case for authenticated views."""
    def setUp(self):
        """Set-up for authenticated view test cases; create a user."""
        self.user = F.UserFactory.create()


    # subclasses should provide a url property
    url = None


    def get(self, **kwargs):
        """Shortcut for getting url, authenticated."""
        kwargs.setdefault("user", self.user)
        return self.app.get(self.url, **kwargs)


    def post(self, data, **kwargs):
        """Shortcut for posting to url, authenticated."""
        kwargs.setdefault("user", self.user)
        return self.app.post(self.url, data, **kwargs)


    def add_perm(self, codename):
        """Add named permission to user."""
        from cc import model
        perm = model.Permission.objects.get(codename=codename)
        self.user.user_permissions.add(perm)


    def test_login_required(self):
        """Requires login."""
        response = self.app.get(self.url)

        self.assertEqual(response.status_int, 302)
