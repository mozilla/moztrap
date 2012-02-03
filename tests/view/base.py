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
from django.conf import settings

import django_webtest

from .. import factories as F


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
    def assertInList(self, response, name, count=1):
        """Assert that item ``name`` is in the list ``count`` times."""
        # One occurrence in the list = two occurrences of the name in HTML
        actual = response.body.count(name)
        self.assertEqual(
            actual, count * 2,
            "'{0}' is in the list {1} times, not {2}.".format(
                name, actual, count))


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


    def assertActionRequiresPermission(self, action, permission):
        """Assert that the given list action requires the given permission."""
        cv = F.CaseVersionFactory.create()

        form = self.get_form()

        name = "action-{0}".format(action)

        # action button not shown to the user
        self.assertTrue(name not in form.fields)

        # ...but if they cleverly submit it anyway they get a 403...
        res = self.post(
            {
                name: str(cv.id),
                "csrfmiddlewaretoken":
                    form.fields.get("csrfmiddlewaretoken")[0].value
                },
            status=403,
            )

        # ...with a message about permissions.
        res.mustcontain("permission")
