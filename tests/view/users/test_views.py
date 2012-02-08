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
from django.core import mail
from django.core.urlresolvers import reverse

from .. import base

from ... import factories as F



class LoginTest(base.ViewTestCase):
    """Tests for login view."""
    @property
    def url(self):
        """Shortcut for login url."""
        return reverse("auth_login")


    def test_login(self):
        """Successful login redirects."""
        F.UserFactory.create(username="test", password="sekrit")

        form = self.get().forms["loginform"]
        form["username"] = "test"
        form["password"] = "sekrit"
        res = form.submit(status=302)

        self.assertRedirects(res, reverse("home"))


    def test_login_failed(self):
        """Failed login returns error message."""
        F.UserFactory.create(username="test", password="sekrit")

        form = self.get().forms["loginform"]
        form["username"] = "test"
        form["password"] = "blah"
        res = form.submit(status=200)

        res.mustcontain("Please enter a correct username and password")



class LogoutTest(base.ViewTestCase):
    """Tests for logout view."""
    @property
    def url(self):
        """Shortcut for logout url."""
        return reverse("auth_logout")


    def test_logout(self):
        """Successful logout redirects to login."""
        F.UserFactory.create(username="test", password="sekrit")

        form = self.app.get(reverse("auth_login")).forms["loginform"]
        form["username"] = "test"
        form["password"] = "sekrit"
        form.submit()

        res = self.get(status=302)

        self.assertRedirects(res, reverse("auth_login"))



class PasswordChangeTest(base.AuthenticatedViewTestCase):
    """Tests for change-password view."""
    def setUp(self):
        """Set password for user."""
        super(PasswordChangeTest, self).setUp()
        self.user.set_password("sekrit")
        self.user.save()


    @property
    def url(self):
        """Shortcut for password-change url."""
        return reverse("auth_password_change")


    def test_change_password(self):
        """Get a confirmation message after changing password."""
        form = self.get().forms["changepasswordform"]
        form["old_password"] = "sekrit"
        form["new_password1"] = "foo"
        form["new_password2"] = "foo"

        res = form.submit(status=302).follow().follow()

        res.mustcontain("Password changed")



class PasswordResetTest(base.ViewTestCase):
    """Tests for reset-password view."""
    def setUp(self):
        """Create a user."""
        super(PasswordResetTest, self).setUp()
        self.user = F.UserFactory.create(email="user@example.com")


    @property
    def url(self):
        """Shortcut for password-reset url."""
        return reverse("auth_password_reset")


    def test_reset_password(self):
        """Get a confirmation message and reset email."""
        form = self.get().forms["resetpasswordform"]
        form["email"] = "user@example.com"

        res = form.submit(status=302).follow().follow()

        res.mustcontain("Password reset email sent")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["user@example.com"])



class PasswordResetConfirmTest(base.ViewTestCase):
    """Tests for reset-password-confirm view."""
    def setUp(self):
        """Create a user."""
        super(PasswordResetConfirmTest, self).setUp()
        self.user = F.UserFactory.create(email="user@example.com")


    @property
    def url(self):
        """Shortcut for password-reset-confirm url."""
        form = self.app.get(
            reverse("auth_password_reset")).forms["resetpasswordform"]
        form["email"] = "user@example.com"
        form.submit(status=302)

        for line in mail.outbox[0].body.splitlines():
            if "://" in line:
                return line.strip()

        self.fail("No password reset confirm URL found in reset email.")


    def test_reset_password_confirm(self):
        """Get a confirmation message after resetting password."""
        form = self.get().forms["setpasswordform"]
        form["new_password1"] = "foo"
        form["new_password2"] = "foo"

        res = form.submit(status=302).follow().follow()

        res.mustcontain("Password changed")



class RegisterTest(base.ViewTestCase):
    """Tests for register view."""
    @property
    def url(self):
        """Shortcut for register url."""
        return reverse("registration_register")


    def test_register(self):
        """Get a confirmation message after registering."""
        form = self.get().forms["accountform"]
        form["username"] = "new"
        form["email"] = "new@example.com"
        form["password1"] = "sekrit"
        form["password2"] = "sekrit"

        res = form.submit(status=302).follow().follow()

        res.mustcontain("Check your email for an account activation link")



class ActivateTest(base.ViewTestCase):
    @property
    def url(self):
        """Shortcut for activate url."""
        form = self.app.get(
            reverse("registration_register")).forms["accountform"]
        form["username"] = "new"
        form["email"] = "new@example.com"
        form["password1"] = "sekrit"
        form["password2"] = "sekrit"
        form.submit(status=302)

        for line in mail.outbox[0].body.splitlines():
            if "://" in line:
                return line.strip()

        self.fail("Activation link not found in activation email.")


    def test_activate(self):
        """Get a confirmation message after activating."""
        res = self.get(status=302).follow().follow()

        res.mustcontain("Account activated")


    def test_failed_activate(self):
        """Failed activation returns a failure message."""
        res = self.app.get(
            reverse("registration_activate", kwargs={"activation_key": "foo"})
            )

        res.mustcontain("that activation key is not valid")
