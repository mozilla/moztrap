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
Proxy User and Role models.

"""
from django.contrib.auth.backends import ModelBackend as DjangoModelBackend
# Permission is imported solely so other places can import it from here
from django.contrib.auth.models import User as BaseUser, Group, Permission

from registration.models import RegistrationProfile



class User(BaseUser):
    """Proxy for contrib.auth User that adds action methods and roles alias."""
    class Meta:
        proxy = True


    def delete(self, user=None):
        """
        Delete this user.

        We ignore the passed-in user since User is not a CCModel and doesn't
        track created_by / modified_by.

        We have to delete registration profiles manually, to avoid
        https://code.djangoproject.com/ticket/16128.

        """
        # @@@ Django ticket 16128, hopefully fixed in 1.4?
        # RegistrationProfile's FK is to Django's user model, not ours
        RegistrationProfile.objects.filter(user=self).delete()
        super(User, self).delete()


    def activate(self, user=None):
        """Activate this user."""
        self.is_active = True
        self.save(force_update=True)


    def deactivate(self, user=None):
        """Deactivate this user."""
        self.is_active = False
        self.save(force_update=True)


    @property
    def roles(self):
        """Maps our name (roles) to Django name (groups)."""
        return self.groups



Role = Group



class ModelBackend(DjangoModelBackend):
    """Authentication backend that returns instances of our proxy User model."""
    def authenticate(self, username=None, password=None):
        """Return User for given credentials, or None."""
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None


    def get_user(self, user_id):
        """Return User for given ID, or None."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
