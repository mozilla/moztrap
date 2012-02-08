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
from contextlib import contextmanager
from datetime import datetime

from django.conf import settings

from BeautifulSoup import BeautifulSoup
import django_webtest
from mock import patch

from .. import factories as F
from ..utils import Url, refresh



@contextmanager
def patch_session(session_data):
    """Context manager to patch session vars."""
    with patch(
            "django.contrib.sessions.backends.cached_db."
            "SessionStore._session_cache",
            session_data,
            create=True):
        yield



class WebTest(django_webtest.WebTest):
    """Fix WebTest so it works with django-session-csrf."""
    def _setup_auth_middleware(self):
        """
        Monkeypatch remote-user-auth middleware into MIDDLEWARE_CLASSES.

        Places remote-user-auth middleware before session-csrf middleware, so
        session-csrf sees the authenticated user.

        """
        auth_middleware = "django_webtest.middleware.WebtestUserMiddleware"
        session_csrf_middleware = "session_csrf.CsrfMiddleware"
        index = settings.MIDDLEWARE_CLASSES.index(session_csrf_middleware)
        settings.MIDDLEWARE_CLASSES.insert(index, auth_middleware)



class ViewTestCase(WebTest):
    """Add some utility assertions and methods."""
    # subclasses should provide a url property
    url = None


    def assertRedirects(self, response, path, status_code=302):
        """An assertRedirects that works with WebTest."""
        self.assertEqual(response.status_int, status_code)

        self.assertEqual(
            Url(response.headers["Location"]),
            Url("http://localhost:80" + path)
            )


    def assertElement(self, html, element, *args, **kwargs):
        """
        Assert that an element is in an HTML snippet some number of times.

        ``element`` is the HTML tag name; extra arguments and keyword arguments
        are passed on to BeautifulSoup as attribute selectors.

        ``count`` keyword arg specifies the number of elements matching the
        spec that are expected to be found; defaults to 1.

        """
        count = kwargs.pop("count", 1)
        actual = len(BeautifulSoup(html).findAll(element, *args, **kwargs))
        self.assertEqual(
            actual,
            count,
            "Element {0}({1}, {2}) is in the list {3} times, not {4}.".format(
                element, args, kwargs, actual, count)
            )


    def get(self, **kwargs):
        """Shortcut for getting url."""
        return self.app.get(self.url, **kwargs)



class AuthenticatedViewTestCase(ViewTestCase):
    """Base test case for authenticated views."""
    def setUp(self):
        """Set-up for authenticated view test cases; create a user."""
        self.user = F.UserFactory.create()


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
        response = self.app.get(self.url, status=302)

        self.assertIn("login", response.headers["Location"])



class FormViewTestCase(AuthenticatedViewTestCase):
    """Base class for testing any view with a form."""
    # subclasses should override
    form_id = None


    def get_form(self):
        """Get the manage list form."""
        return self.get().forms[self.form_id]



class ManageListViewTestCase(FormViewTestCase):
    """Base class for testing manage list views."""
    # subclasses should specify these:
    perm = None          # required management permission codename
    factory = None       # factory for creating objects in this list
    name_attr = "name"   # char attribute that should appear in list


    def assertInList(self, response, name, count=1):
        """Assert that item ``name`` is in the list ``count`` times."""
        self.assertElement(
            response.body, "h3", "title", title=name, count=count)


    def assertNotInList(self, response, name):
        """Assert that item ``name`` is not in the list."""
        self.assertInList(response, name, 0)


    def assertOrderInList(self, response, *names):
        """Assert that ``names`` appear in list in given order."""
        indices = []
        for name in names:
            try:
                indices.append((response.body.index(name), name))
            except ValueError:
                self.fail("{0} does not appear in response.".format(name))

        actual_order = sorted(indices, key=lambda t: t[0])

        self.assertEqual(
            [t[1] for t in actual_order],
            [t[1] for t in indices],
            )


    def assertActionRequiresPermission(self, action, permission=None):
        """Assert that the given list action requires the given permission."""
        if permission is None:
            permission = self.perm

        o = self.factory.create()

        form = self.get_form()

        name = "action-{0}".format(action)

        # action button not shown to the user
        self.assertTrue(name not in form.fields)

        # ...but if they cleverly submit it anyway they get a 403...
        res = self.post(
            {
                name: str(o.id),
                "csrfmiddlewaretoken":
                    form.fields.get("csrfmiddlewaretoken")[0].value
                },
            status=403,
            )

        # ...with a message about permissions.
        res.mustcontain("permission")


    def test_list(self):
        """Displays a list of objects."""
        self.factory.create(**{self.name_attr: "Foo Bar"})

        res = self.get()

        res.mustcontain("Foo Bar")


    def test_delete(self):
        """Can delete objects from list."""
        self.add_perm(self.perm)

        o = self.factory.create()

        self.get_form().submit(
            name="action-delete",
            index=0,
            headers={"X-Requested-With": "XMLHttpRequest"}
            )

        self.assertTrue(bool(refresh(o).deleted_on))


    def test_delete_requires_permission(self):
        """Deleting requires appropriate permission."""
        self.assertActionRequiresPermission("delete")


    def test_clone(self):
        """Can clone objects in list."""
        self.add_perm(self.perm)

        self.factory.create()

        res = self.get_form().submit(
            name="action-clone",
            index=0,
            headers={"X-Requested-With": "XMLHttpRequest"},
            )

        self.assertElement(
            res.json["html"], "h3", "title", count=2)


    def test_clone_requires_manage_cases_permission(self):
        """Cloning requires manage_cases permission."""
        self.assertActionRequiresPermission("clone")


    def test_filter_by_creator(self):
        """Can filter by creator."""
        self.factory.create(name="Foo 1", user=self.user)
        self.factory.create(name="Foo 2")

        res = self.get(params={"filter-creator": self.user.id})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_default_sort_by_last_created(self):
        """Default sort is by latest created first."""
        self.factory.create(
            name="Foo 1", created_on=datetime(2012, 1, 21))
        self.factory.create(
            name="Foo 2", created_on=datetime(2012, 1, 22))

        res = self.get()

        self.assertOrderInList(res, "Foo 2", "Foo 1")



class ManageListViewFinderTestCase(ManageListViewTestCase):
    """Test case for manage lists with finder."""
    def test_finder(self):
        """Finder is present in context with list of products."""
        p = F.ProductFactory.create(name="Foo Product")

        res = self.get()

        res.mustcontain("Foo Product")
        res.mustcontain(
            "data-sub-url="
            '"?finder=1&amp;col=productversions&amp;id={0}"'.format(p.id))


    def test_finder_ajax(self):
        """Finder intercepts its ajax requests to return child obj lists."""
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
