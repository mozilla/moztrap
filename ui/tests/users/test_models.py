from mock import patch

from ..core.test_cache import CachingFunctionalTestMixin
from ..responses import response
from ..utils import BaseResourceTest
from .base import UserTestCase



@patch("tcmui.core.api.userAgent")
class UserTest(CachingFunctionalTestMixin, BaseResourceTest, UserTestCase):
    def test_current_caches_for_same_user(self, http):
        jane_auth = self.creds("jane@example.com")
        jim_auth = self.creds("jim@example.com")

        http.request.return_value = response(
            self.make_one(email="jane@example.com"))

        jane1 = self.resource_class.current(auth=jane_auth)
        jane1.deliver()

        http.request.return_value = response(
            self.make_one(email="jim@example.com"))

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
            self.make_one(email="jane@example.com"))

        jane1 = self.resource_class.current(auth=jane_auth)
        jane1.deliver()

        jane2 = self.resource_class.current(auth=jane_auth, cache=False)
        jane2.deliver()

        self.assertEqual(http.request.call_count, 2)
        self.assertEqual(jane1.email, jane2.email)
        self.assertEqual(jane1.email, "jane@example.com")
