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
Tests for runtests views.

"""
from django.core.urlresolvers import reverse

from ... import factories as F

from .. import base



class SelectTest(base.AuthenticatedViewTestCase):
    """Tests for select-run view."""
    @property
    def url(self):
        """Shortcut for runtests url."""
        return reverse("runtests")


    def test_requires_execute_permission(self):
        """Requires execute permission."""
        res = self.app.get(self.url, user=F.UserFactory.create(), status=302)

        self.assertIn("login", res.headers["Location"])


    def test_finder(self):
        """Finder is present in context with list of products."""
        self.add_perm("execute")

        p = F.ProductFactory.create(name="Foo Product")

        res = self.get()

        res.mustcontain("Foo Product")
        res.mustcontain(
            "data-sub-url="
            '"?finder=1&amp;col=productversions&amp;id={0}"'.format(p.id))


    def test_finder_ajax(self):
        """Finder intercepts its ajax requests to return child obj lists."""
        self.add_perm("execute")

        pv = F.ProductVersionFactory.create(version="1.0.1")

        res = self.get(
            params={
                "finder": "1",
                "col": "productversions",
                "id": str(pv.product.id)
                },
            headers={"X-Requested-With": "XMLHttpRequest"},
            )

        self.assertIn("1.0.1", res.json["html"])
        self.assertIn(
            'data-sub-url="?finder=1&amp;col=runs&amp;id={0}"'.format(pv.id),
            res.json["html"]
            )
