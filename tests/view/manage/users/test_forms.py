"""
Tests for user-management forms.

"""
from tests import case



class EditUserFormTest(case.DBTestCase):
    """Tests for EditUserForm."""
    @property
    def form(self):
        """The form class under test."""
        from moztrap.view.manage.users.forms import EditUserForm
        return EditUserForm


    def test_edit_user(self):
        """Can edit user name and description."""
        g1 = self.F.RoleFactory()
        g2 = self.F.RoleFactory()
        self.F.RoleFactory()
        p = self.F.UserFactory(username="Take One", email="", is_active=False)

        f = self.form(
            {
                "username": "two",
                "email": "two@example.com",
                "is_active": "1",
                "groups": [str(g1.id), str(g2.id)]
                },
            instance=p
            )

        user = f.save()

        self.assertEqual(user.username, "two")
        self.assertEqual(user.email, "two@example.com")
        self.assertEqual(user.is_active, True)
        self.assertEqual(set(user.groups.all()), set([g1, g2]))



class AddUserFormTest(case.DBTestCase):
    """Tests for AddUserForm."""
    @property
    def form(self):
        """The form class under test."""
        from moztrap.view.manage.users.forms import AddUserForm
        return AddUserForm


    def test_add_user(self):
        """Can add user."""
        g1 = self.F.RoleFactory()
        g2 = self.F.RoleFactory()
        self.F.RoleFactory()
        f = self.form(
            {
                "username": "Two",
                "email": "two@example.com",
                "is_active": "",
                "groups": [str(g1.id), str(g2.id)]
                }
            )

        user = f.save()

        self.assertEqual(user.username, "Two")
        self.assertEqual(user.email, "two@example.com")
        self.assertEqual(user.is_active, False)
        self.assertEqual(set(user.groups.all()), set([g1, g2]))
