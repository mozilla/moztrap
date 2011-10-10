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
from mock import patch

from ..responses import response
from ..utils import (
    ResourceTestCase, BaseResourceTest, CachingFunctionalTestMixin)
from .builders import users



@patch("ccui.core.api.userAgent")
class UserTest(CachingFunctionalTestMixin, BaseResourceTest, ResourceTestCase):
    def get_resource_class(self):
        from ccui.users.models import User
        return User


    def get_resource_list_class(self):
        from ccui.users.models import UserList
        return UserList


    def test_current_caches_for_same_user(self, http):
        jane_auth = self.creds("jane@example.com")
        jim_auth = self.creds("jim@example.com")

        http.request.return_value = response(
            users.one(email="jane@example.com"))

        jane1 = self.resource_class.current(auth=jane_auth)
        jane1.deliver()

        http.request.return_value = response(
            users.one(email="jim@example.com"))

        jim = self.resource_class.current(auth=jim_auth)
        jim.deliver()

        jane2 = self.resource_class.current(auth=jane_auth)
        jane2.deliver()

        self.assertEqual(http.request.call_count, 2)
        self.assertEqual(jane1.email, jane2.email)
        self.assertEqual(jane1.email, "jane@example.com")
        self.assertEqual(jim.email, "jim@example.com")


    def test_prevent_current_caching(self, http):
        jane_auth = self.creds("jane@example.com")

        http.request.return_value = response(
            users.one(email="jane@example.com"))

        jane1 = self.resource_class.current(auth=jane_auth)
        jane1.deliver()

        jane2 = self.resource_class.current(auth=jane_auth, cache=False)
        jane2.deliver()

        self.assertEqual(http.request.call_count, 2)
        self.assertEqual(jane1.email, jane2.email)
        self.assertEqual(jane1.email, "jane@example.com")
