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
Utility base TestCase classes for testing views.

"""
from django.conf import settings

from BeautifulSoup import BeautifulSoup
import django_webtest
import django_webtest.backends

from cc import model

from ...utils import Url
from ..base import DBMixin



class WebtestUserBackend(django_webtest.backends.WebtestUserBackend):
    """A version of WebtestUserBackend that returns our proxy User model."""
    def authenticate(self, django_webtest_user):
        """
        The username passed as ``remote_user`` is considered trusted.  This
        method simply returns the ``User`` object with the given username,
        creating a new ``User`` object if ``create_unknown_user`` is ``True``.

        Returns None if ``create_unknown_user`` is ``False`` and a ``User``
        object with the given username is not found in the database.
        """
        if not django_webtest_user:
            return
        user = None
        username = self.clean_username(django_webtest_user)

        # Note that this could be accomplished in one try-except clause, but
        # instead we use get_or_create when creating unknown users since it has
        # built-in safeguards for multiple threads.
        if self.create_unknown_user:
            user, created = model.User.objects.get_or_create(username=username)
            if created:
                user = self.configure_user(user)
        else:
            try:
                user = model.User.objects.get(username=username)
            except model.User.DoesNotExist:
                pass
        return user


    def get_user(self, user_id):
        """Return instances of our User model."""
        try:
            return model.User.objects.get(pk=user_id)
        except model.User.DoesNotExist:
            return None




class WebTest(DBMixin, django_webtest.WebTest):
    """Fix WebTest so it works with django-session-csrf, mixin db utilities."""
    def _setup_auth_backend(self):
        """Use our subclass of the remote user backend."""
        backend_name = 'tests.case.view.base.WebtestUserBackend'
        settings.AUTHENTICATION_BACKENDS.insert(0, backend_name)


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

        ``html`` is either an HTML string or a BeautifulSoup object.

        ``element`` is the HTML tag name; extra arguments and keyword arguments
        are passed on to BeautifulSoup as attribute selectors.

        ``count`` keyword arg specifies the number of elements matching the
        spec that are expected to be found; defaults to 1.

        """
        count = kwargs.pop("count", 1)
        if isinstance(html, basestring):
            html = BeautifulSoup(html)
        actual = len(html.findAll(element, *args, **kwargs))
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
        self.user = self.F.UserFactory.create()


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
        perm = self.model.Permission.objects.get(codename=codename)
        self.user.user_permissions.add(perm)


    def test_login_required(self):
        """Requires login."""
        response = self.app.get(self.url, status=302)

        self.assertIn("login", response.headers["Location"])



class FormViewTestCase(AuthenticatedViewTestCase):
    """Base class for testing any view with a form."""
    # subclasses should override
    form_id = None


    def get_form(self, *args, **kwargs):
        """Get the manage list form; passes args/kwargs on to self.get()."""
        return self.get(*args, **kwargs).forms[self.form_id]
