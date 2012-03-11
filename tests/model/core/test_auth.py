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
Tests for auth proxy models.

"""
from tests import case



class UserTest(case.DBTestCase):
    """Tests for User proxy model."""
    def test_can_delete_user_with_registration_profile(self):
        """Can delete a user with a registration profile; refs Django #16128."""
        u = self.F.UserFactory.create()
        self.model.RegistrationProfile.objects.create(
            user=u, activation_key="foo")

        u.delete()

        with self.assertRaises(self.model.User.DoesNotExist):
            self.refresh(u)


    def test_can_pass_user_to_delete(self):
        """Can pass user to User.delete() even though its not a CCModel."""
        u = self.F.UserFactory.create()

        u.delete(user=u)

        with self.assertRaises(self.model.User.DoesNotExist):
            self.refresh(u)


    def test_activate(self):
        """Can activate a user."""
        u = self.F.UserFactory.create(is_active=False)

        u.activate(user=u)

        self.assertTrue(self.refresh(u).is_active)


    def test_deactivate(self):
        """Can deactivate a user."""
        u = self.F.UserFactory.create(is_active=True)

        u.deactivate(user=u)

        self.assertFalse(self.refresh(u).is_active)


    def test_roles(self):
        """Can assign roles."""
        u = self.F.UserFactory.create()
        r = self.F.RoleFactory.create()
        u.roles.add(r)

        self.assertEqual(set(u.roles.all()), set([r]))



class ModelBackendTest(case.DBTestCase):
    """Tests for our custom ModelBackend."""
    @property
    def backend(self):
        """An instance of the backend class under test."""
        from cc.model.core.auth import ModelBackend
        return ModelBackend()


    def test_authenticate(self):
        """Can authenticate a user with username and password."""
        u = self.F.UserFactory.create(username="foo", password="sekrit")

        res = self.backend.authenticate(username="foo", password="sekrit")

        self.assertEqual(res, u)


    def test_authenticate_bad_username(self):
        """Cannot authenticate a user with bad username."""
        res = self.backend.authenticate(username="food", password="sekrit")

        self.assertIsNone(res)


    def test_authenticate_bad_password(self):
        """Cannot authenticate a user with bad password."""
        self.F.UserFactory.create(username="foo", password="sekrit")

        res = self.backend.authenticate(username="foo", password="wrong")

        self.assertIsNone(res)


    def test_get_user(self):
        """Can get a user with correct user_id."""
        u = self.F.UserFactory.create()

        res = self.backend.get_user(u.id)

        self.assertEqual(res, u)


    def test_get_user_bad_id(self):
        """Cannot get a user with bad user_id."""
        res = self.backend.get_user(-1)

        self.assertIsNone(res)
