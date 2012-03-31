"""
Tests for login/logout/registration forms.

"""
from tests import case



class RegistrationFormTest(case.DBTestCase):
    """Tests for RegistrationForm."""
    @property
    def RegistrationForm(self):
        """The form class under test."""
        from cc.view.users.forms import RegistrationForm
        return RegistrationForm


    def test_unique_email(self):
        """Validation error for non-unique email."""
        self.F.UserFactory.create(email="test@example.com")

        form = self.RegistrationForm({
                "username": "foo",
                "email": "test@example.com",
                "password1": "testpw1234",
                "password2": "testpw1234",
                })

        self.assertFalse(form.is_valid())

        self.assertEqual(
            form.errors["email"], [u"A user with that email already exists."])



class SetUsernameFormTest(case.DBTestCase):
    """Tests for SetUsernameForm."""
    @property
    def SetUsernameForm(self):
        """The form class under test."""
        from cc.view.users.forms import SetUsernameForm
        return SetUsernameForm


    def test_invalid_chars(self):
        """Validation error for invalid username characters."""
        self.F.UserFactory.create()

        form = self.SetUsernameForm({"username": ":foo:"})

        self.assertFalse(form.is_valid())

        self.assertEqual(
            form.errors["username"],
            [u"This value must contain only letters, numbers and underscores."],
            )
