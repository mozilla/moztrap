from mock import patch

from ..responses import response
from ..utils import ResourceTestCase, Url
from .builders import codevalues



@patch("ccui.static.data.cache")
@patch("ccui.core.api.userAgent")
class StaticDataTest(ResourceTestCase):
    def get_resource_class(self):
        from ccui.static.models import CodeValue
        return CodeValue


    def get_resource_list_class(self):
        from ccui.static.models import ArrayOfCodeValue
        return ArrayOfCodeValue


    @property
    def func(self):
        from ccui.static.data import get_codevalue
        return get_codevalue


    def _setup_get_uncached(self, http, cache):
        http.request.return_value = response(
            codevalues.array(
                {"id": 1, "description": "Draft"},
                {"id": 2, "description": "Active"}))

        cache.get.return_value = None


    def test_get_uncached_is_codevalue(self, http, cache):
        self._setup_get_uncached(http, cache)

        code = self.func("STATUS", 1)

        self.assertIsInstance(code, self.resource_class)


    def test_get_uncached_id(self, http, cache):
        self._setup_get_uncached(http, cache)

        code = self.func("STATUS", 1)

        self.assertEqual(code.id, 1)


    def test_get_uncached_calls_cache(self, http, cache):
        self._setup_get_uncached(http, cache)

        self.func("STATUS", 1)

        cache.get.assert_called_once_with("staticdata-STATUS-1")


    def test_get_uncached_makes_request(self, http, cache):
        self._setup_get_uncached(http, cache)

        self.func("STATUS", 1)

        self.assertEqual(
            Url(http.request.call_args[1]["uri"]),
            Url("http://fake.base/staticData/values/STATUS?_type=json"))


    def test_get_uncached_sets_cache(self, http, cache):
        self._setup_get_uncached(http, cache)

        self.func("STATUS", 1)

        self.assertEqual(
            sorted(cache.set_many.call_args[0][0].keys()),
            ["staticdata-STATUS-1", "staticdata-STATUS-2"])


    def test_get_uncached_sets_staticdata_timeout(self, http, cache):
        self._setup_get_uncached(http, cache)

        self.func("STATUS", 1)

        self.assertEqual(cache.set_many.call_args[0][1], 1800)


    def test_get_cached_returns_from_cache(self, http, cache):
        code = self.func("STATUS", 1)

        self.assertIs(code, cache.get.return_value)


    def test_get_cached_calls_cache(self, http, cache):
        self.func("STATUS", 1)

        cache.get.assert_called_once_with("staticdata-STATUS-1")


    def test_get_cached_makes_no_http_request(self, http, cache):
        self.func("STATUS", 1)

        http.request.assert_not_called()
