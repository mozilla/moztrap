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

from django_webtest import WebTest

from .. import factories as F



class LoginTest(WebTest):
    """Tests for login view."""
    @property
    def url(self):
        """Shortcut for login url."""
        return reverse("login")


    def get(self):
        """Shortcut for getting login url."""
        return self.app.get(self.url)


    def test_login(self):
        """Successful login redirects."""
        F.UserFactory.create(username="test", password="sekrit")

        form = self.get().forms["loginform"]
        form["username"] = "test"
        form["password"] = "sekrit"
        res = form.submit()

        self.assertEqual(res.status_int, 302, res.body)
        self.assertEqual(
            res.headers["Location"], "http://localhost:80/manage/cases/")


    def test_login_failed(self):
        """Failed login returns error message."""
        F.UserFactory.create(username="test", password="sekrit")

        form = self.get().forms["loginform"]
        form["username"] = "test"
        form["password"] = "blah"
        res = form.submit()

        self.assertEqual(res.status_int, 200, res.headers)
        res.mustcontain("Please enter a correct username and password")



class LogoutTest(WebTest):
    """Tests for logout view."""
    @property
    def url(self):
        """Shortcut for logout url."""
        return reverse("logout")


    def get(self):
        """Shortcut for getting logout url."""
        return self.app.get(self.url)


    def test_logout(self):
        """Successful logout redirects to login."""
        F.UserFactory.create(username="test", password="sekrit")

        form = self.app.get(reverse("login")).forms["loginform"]
        form["username"] = "test"
        form["password"] = "sekrit"
        form.submit()

        res = self.get()

        self.assertEqual(res.status_int, 302, res.body)
        self.assertEqual(
            res.headers["Location"], "http://localhost:80/users/login/")
