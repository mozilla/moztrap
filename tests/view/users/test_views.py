"""
Tests for login/logout/account views.

"""
from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse

# @@@ import from Django in 1.4
from djangosecure.test_utils import override_settings
import mock

from tests import case
from tests.utils import patch_session



@mock.patch.object(settings, "USE_BROWSERID", False)
class LoginTest(case.view.ViewTestCase):
    """Tests for login view."""
    @property
    def url(self):
        """Shortcut for login url."""
        return reverse("auth_login")


    def test_login(self):
        """Successful login redirects."""
        self.F.UserFactory.create(username="test", password="sekrit")

        form = self.get().forms["loginform"]
        form["username"] = "test"
        form["password"] = "sekrit"
        res = form.submit(status=302)

        self.assertRedirects(res, reverse("home"))


    def test_email_login(self):
        """Can log in with email address."""
        self.F.UserFactory.create(
            username="test", email="test@example.com", password="sekrit")

        form = self.get().forms["loginform"]
        form["username"] = "test@example.com"
        form["password"] = "sekrit"
        res = form.submit(status=302)

        self.assertRedirects(res, reverse("home"))


    def test_login_failed(self):
        """Failed login returns error message."""
        self.F.UserFactory.create(username="test", password="sekrit")

        form = self.get().forms["loginform"]
        form["username"] = "test"
        form["password"] = "blah"
        res = form.submit(status=200)

        res.mustcontain("Please enter a correct username and password")


    def test_display_captcha(self):
        """Sixth login attempt within a minute returns form with captcha."""
        res = self.get()
        for i in range(6):
            res = res.forms["loginform"].submit()

        form = res.forms["loginform"]

        self.assertIn("captcha", form.fields)


    def test_bad_captcha(self):
        """Bad value for captcha fails login, even with correct user/pw."""
        self.F.UserFactory.create(username="test", password="sekrit")

        session_data = {}

        with patch_session(session_data):
            res = self.get()
            for i in range(6):
                res = res.forms["loginform"].submit()

            form = res.forms["loginform"]
            answer = session_data["auth_captcha_answer"]
            form["captcha"] = answer + 1 # oops, wrong answer!
            form["username"] = "test"
            form["password"] = "sekrit"
            res = form.submit(status=200)

        res.mustcontain("not the answer we were looking for")


    def test_good_captcha(self):
        """Good value for captcha allows login."""
        self.F.UserFactory.create(username="test", password="sekrit")

        session_data = {}

        with patch_session(session_data):
            res = self.get()
            for i in range(6):
                res = res.forms["loginform"].submit()

            form = res.forms["loginform"]
            answer = session_data["auth_captcha_answer"]
            form["captcha"] = answer
            form["username"] = "test"
            form["password"] = "sekrit"
            res = form.submit(status=302)

        self.assertRedirects(res, reverse("home"))



@mock.patch.object(settings, "USE_BROWSERID", True)
class BrowserIDTest(case.view.ViewTestCase):
    """Tests for BrowserID verify view."""
    @property
    def url(self):
        """Shortcut for login url with a next URL."""
        return reverse("auth_login")


    def new_browserid(self, email="test@example.com"):
        """Create a new user via browserID login; return the redirect."""
        with mock.patch("django_browserid.auth.verify") as verify:
            verify.return_value = {"email": email}

            form = self.get().forms["browserid-form"]
            form["assertion"].force_value("foo")
            res = form.submit(status=302)

        return res


    def test_fail_redirect(self):
        """Failed BrowserID verification redirects without losing 'next'."""
        url = reverse("auth_login") + "?next=/foo"
        form = self.app.get(url).forms["browserid-form"]
        res = form.submit(status=302)

        self.assertRedirects(res, url)


    def test_fail_message(self):
        """Failed BrowserID verification has a message for the user."""
        form = self.get().forms["browserid-form"]
        res = form.submit(status=302).follow()

        self.assertContains(res, "Unable to sign in with that email address")


    def test_new_user(self):
        """Successful new BrowserID login creates User with auto username."""
        self.new_browserid()

        user = self.model.User.objects.get()
        self.assertTrue(user.username.startswith(":auto:"))


    def test_new_user_role(self):
        """New user has default new user role."""
        from preferences import preferences
        cp = preferences.CorePreferences
        role = self.F.RoleFactory.create()
        cp.default_new_user_role = role
        cp.save()

        self.new_browserid()

        user = self.model.User.objects.get()
        self.assertTrue(user.roles.get(), role)


    def test_set_username_initial(self):
        """A new browserID user gets a set-username form, initially blank."""
        form = self.new_browserid().follow().follow().forms["setusernameform"]

        self.assertEqual(form.fields["username"][0].value, "")


    def test_set_username(self):
        """A new browserID user is prompted to set their username, and can."""
        form = self.new_browserid().follow().follow().forms["setusernameform"]
        form["username"] = "tester"
        res = form.submit(status=302)

        self.assertRedirects(res, "/")
        user = self.model.User.objects.get()
        self.assertEqual(user.username, "tester")


    def test_set_username_error(self):
        """A new browserID user gets an error if they choose an in-use name."""
        self.F.UserFactory.create(username="tester")

        form = self.new_browserid().follow().follow().forms["setusernameform"]
        form["username"] = "tester"
        res = form.submit(status=200)

        res.mustcontain("User with this Username already exists.")


    def test_auto_username_logout(self):
        """A user with an auto-username can logout."""
        logoutform = self.new_browserid().follow().follow().forms["logoutform"]
        res = logoutform.submit().follow()

        self.assertRedirects(res, reverse("auth_login") + "?next=/")



@mock.patch.object(settings, "USE_BROWSERID", False)
class LogoutTest(case.view.ViewTestCase):
    """Tests for logout view."""
    @property
    def url(self):
        """Shortcut for logout url."""
        return reverse("auth_logout")


    def test_get_405(self):
        """GETting the logout view results in HTTP 405 Method Not Allowed."""
        self.get(status=405)


    def test_logout_redirect(self):
        """Successful logout POST redirects to the page you were on."""
        user = self.F.UserFactory.create()

        form = self.app.get("/manage/runs/", user=user).forms["logoutform"]
        res = form.submit()

        self.assertRedirects(res, "/manage/runs/")



class PasswordStrengthTests(object):
    """Mixin tests for any view that sets or changes a password."""
    # subclasses should set
    form_id = None
    extra_form_data = {}
    password_fields = ["new_password1", "new_password2"]


    def get_form(self):
        """Shortcut to get the form."""
        return self.get().forms[self.form_id]


    def submit_form(self, password, status):
        """Submit form with given password and return response."""
        form = self.get_form()
        for k, v in self.extra_form_data.items():
            form[k] = v
        for fn in self.password_fields:
            form[fn] = password
        return form.submit(status=status)


    @override_settings(MINIMUM_PASSWORD_CHARS=10)
    def test_minimum_password_length(self):
        """Passwords must meet the minimum length."""
        res = self.submit_form("abcdef123", status=200)

        res.mustcontain("Your password must be a minimum of 10 characters")


    @override_settings(PASSWORD_REQUIRE_ALPHA_NUMERIC=True)
    def test_password_require_numeric(self):
        """If enabled, passwords require numbers + letters, not just letters."""
        res = self.submit_form("abcdefgh", status=200)

        res.mustcontain("Your password must contain both letters and numbers")


    @override_settings(PASSWORD_REQUIRE_ALPHA_NUMERIC=True)
    def test_password_require_alpha(self):
        """If enabled, passwords require numbers + letters, not just numbers."""
        res = self.submit_form("12345678", status=200)

        res.mustcontain("Your password must contain both letters and numbers")


    @override_settings(FORBIDDEN_PASSWORDS=["abcdef123"])
    def test_forbidden_passwords(self):
        """Some passwords are explicitly forbidden."""
        res = self.submit_form("abcdef123", status=200)

        res.mustcontain("That password is too easily guessed")



class PasswordChangeTest(PasswordStrengthTests,
                         case.view.AuthenticatedViewTestCase
                         ):
    """Tests for change-password view."""
    form_id = "changepasswordform"
    extra_form_data = {"old_password": "sekrit"}


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
        res = self.submit_form("sekrit123", status=302).follow().follow()

        res.mustcontain("Password changed")



class PasswordResetTest(case.view.ViewTestCase):
    """Tests for reset-password view."""
    def setUp(self):
        """Create a user."""
        super(PasswordResetTest, self).setUp()


    @property
    def url(self):
        """Shortcut for password-reset url."""
        return reverse("auth_password_reset")


    def test_reset_password(self):
        """Get a confirmation message and reset email."""
        self.F.UserFactory.create(email="user@example.com")

        form = self.get().forms["resetpasswordform"]
        form["email"] = "user@example.com"

        res = form.submit(status=302).follow().follow()

        res.mustcontain("Password reset email sent")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["user@example.com"])


    def test_bad_email(self):
        """Nonexistent user emails give no clue to an attacker."""
        form = self.get().forms["resetpasswordform"]
        form["email"] = "doesnotexist@example.com"

        res = form.submit(status=302).follow().follow()

        res.mustcontain("Password reset email sent")
        self.assertEqual(len(mail.outbox), 0)



class PasswordResetConfirmTest(PasswordStrengthTests, case.view.ViewTestCase):
    """Tests for reset-password-confirm view."""
    form_id = "setpasswordform"


    def setUp(self):
        """Create a user."""
        super(PasswordResetConfirmTest, self).setUp()
        self.user = self.F.UserFactory.create(email="user@example.com")


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
        res = self.submit_form("sekrit123", status=302).follow().follow()

        res.mustcontain("Password changed")



class RegisterTest(PasswordStrengthTests, case.view.ViewTestCase):
    """Tests for register view."""
    form_id = "accountform"
    extra_form_data = {"username": "new", "email": "new@example.com"}
    password_fields = ["password1", "password2"]


    @property
    def url(self):
        """Shortcut for register url."""
        return reverse("registration_register")


    def test_register(self):
        """Get a confirmation message after registering."""
        res = self.submit_form("sekrit123", status=302).follow().follow()

        res.mustcontain("Check your email for an account activation link")


    def test_new_user_role(self):
        """New user has default new user role."""
        from preferences import preferences
        cp = preferences.CorePreferences
        role = self.F.RoleFactory.create()
        cp.default_new_user_role = role
        cp.save()

        self.submit_form("sekrit123", status=302)

        user = self.model.User.objects.get()
        self.assertTrue(user.roles.get(), role)



class ActivateTest(case.view.ViewTestCase):
    @property
    def url(self):
        """Shortcut for activate url."""
        form = self.app.get(
            reverse("registration_register")).forms["accountform"]
        form["username"] = "new"
        form["email"] = "new@example.com"
        form["password1"] = "sekrit123"
        form["password2"] = "sekrit123"
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
