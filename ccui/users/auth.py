# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
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
from ..core.auth import Credentials
from .models import User



class UserCredentials(Credentials):
    """
    Expands the core Credentials object with lazy ``user`` and
    ``permission_codes`` properties.

    """
    def __init__(self, *args, **kwargs):
        super(UserCredentials, self).__init__(*args, **kwargs)
        self._user = None
        self._permission_codes = None


    @property
    def user(self):
        if self._user is None:
            try:
                user = User.current(auth=self, cache=False)
                user.deliver()
            except (User.Forbidden, User.Unauthorized, User.NotFound):
                user = None
            self._user = user
        return self._user


    @property
    def permission_codes(self):
        if self._permission_codes is None:
            self._permission_codes = self.user.permissionCodes
        return self._permission_codes
