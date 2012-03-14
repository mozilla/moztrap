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
Tests for open web app views.

"""
import json

from django.core.urlresolvers import reverse

from django_webtest import WebTest



class ManifestTest(WebTest):
    """Tests for manifest view."""
    @property
    def url(self):
        """Shortcut for owa manifest url."""
        return reverse("owa_manifest")


    def get(self, **kwargs):
        """Shortcut for getting manifest url."""
        return self.app.get(self.url, **kwargs)


    def test_manifest(self):
        """Successful manifest is returned."""

        res = self.get(status=200)

        self.assertEqual(
            res.headers["Content-Type"], "application/x-web-app-manifest+json",
            res.headers)

        # content-type isn't normal JSON, so I must parse the JSON
        # directly, rather than using res.json["name"]

        self.assertEqual(
            json.loads(res.body)["description"],
            "A Test Case and Results management System.",
            )
