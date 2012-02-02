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



class ManifestTest(WebTest):
    """Tests for manifest view."""
    @property
    def url(self):
        """Shortcut for owa manifest url."""
        return reverse("owa_manifest")


    def get(self):
        """Shortcut for getting manifest url."""
        return self.app.get(self.url)


    def test_login(self):
        """Successful manifest is returned."""

        res = self.get()

        self.assertEqual(res.status_int, 200, res.headers)
        self.assertEqual(
            res.headers["Content-Type"], "application/x-web-app-manifest+json", 
            res.headers)
        res.mustcontain("A Test Case and Results management System")


class RegisterTest(WebTest):
    """Tests for register view."""
    @property
    def url(self):
        """Shortcut for owa register url."""
        return reverse("owa_register")


    def get(self):
        """Shortcut for getting register url."""
        return self.app.get(self.url)


    def test_registration_page(self):
        """registration page is returned."""

        res = self.get()

        self.assertEqual(res.status_int, 200, res.headers)
        res.mustcontain("Register as an Open Web App")

    def test_registration_succeed(self):
        """registration succeeds on button click."""

        res = self.get()
        self.assertEqual("got success", "oh no you di'int")

        self.assertEqual(res.status_int, 200, res.headers)
        res.mustcontain("Register as an Open Web App")


    def test_registration_fail(self):
        """registration fails on button click."""

        res = self.get()

        self.assertEqual("got success", "oh no you di'int")

        self.assertEqual(res.status_int, 200, res.headers)
        res.mustcontain("Register as an Open Web App")
