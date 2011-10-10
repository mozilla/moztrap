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
import httplib

from mock import patch

from ..utils import ResourceTestCase, fill_cache
from ..responses import response
from .builders import users



@patch("ccui.core.api.userAgent", spec=["request"])
@patch("ccui.core.cache.cache", spec=["get", "set", "incr", "add"])
class GetUserTest(ResourceTestCase):
    def get_resource_class(self):
        from ccui.users.models import User
        return User


    def get_resource_list_class(self):
        from ccui.users.models import UserList
        return UserList


    def call(self, *args, **kwargs):
        from ccui.users.util import get_user
        return get_user(*args, **kwargs)


    def test_never_cached(self, cache, http):
        fill_cache(cache, {})
        http.request.return_value = response(
            users.one(email="test@example.com"))

        u1 = self.call("test@example.com", password="testpw")
        u2 = self.call("test@example.com", password="testpw")

        self.assertEqual(http.request.call_count, 2)
        self.assertEqual(u1.email, u2.email)
        self.assertEqual(u1.email, "test@example.com")
        self.assertEqual(cache.set.call_count, 0)
        self.assertEqual(cache.get.call_count, 0)


    def _check_causes_None(self, status_code, cache, http):
        fill_cache(cache, {})
        http.request.return_value = response(
            "", status_code)

        user = self.call("test@example.com", password="testpw")

        self.assertEqual(user, None)


    def test_forbidden_causes_None(self, cache, http):
        self._check_causes_None(httplib.FORBIDDEN, cache, http)


    def test_unauthorized_causes_None(self, cache, http):
        self._check_causes_None(httplib.UNAUTHORIZED, cache, http)


    def test_notfound_causes_None(self, cache, http):
        self._check_causes_None(httplib.NOT_FOUND, cache, http)

