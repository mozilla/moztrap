import httplib

from mock import patch

from ..utils import ResourceTestCase, fill_cache
from ..responses import response
from .builders import users



@patch("tcmui.core.api.userAgent", spec=["request"])
@patch("tcmui.core.cache.cache", spec=["get", "set", "incr", "add"])
class GetUserTest(ResourceTestCase):
    def get_resource_class(self):
        from tcmui.users.models import User
        return User


    def get_resource_list_class(self):
        from tcmui.users.models import UserList
        return UserList


    def call(self, *args, **kwargs):
        from tcmui.users.util import get_user
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

