import httplib

from flufl.enum import Enum
from unittest2 import TestCase

from mock import patch

from tcmui.static.data import get_codevalue
from tcmui.static.models import CodeValue

from ..responses import response, make_codevalues



class SomeStatus(Enum):
    DRAFT = 1
    ACTIVE = 2



class StatusValueTest(TestCase):
    def _make(self, val):
        from tcmui.static.fields import StatusValue
        return StatusValue(val)


    def test_true(self):
        self.assertIs(self._make(SomeStatus.DRAFT).DRAFT, True)


    def test_false(self):
        self.assertIs(self._make(SomeStatus.DRAFT).ACTIVE, False)


    def test_error(self):
        with self.assertRaises(AttributeError):
            self._make(SomeStatus.DRAFT).BLAH



@patch("tcmui.static.data.cache")
@patch("remoteobjects.http.userAgent")
class StaticDataTest(TestCase):
    def _setup_get_uncached(self, http, cache):
        http.request.return_value = response(
            httplib.OK, make_codevalues(
                {"id": 1, "description": "Draft"},
                {"id": 2, "description": "Active"}))

        cache.get.return_value = None


    def test_get_uncached_is_codevalue(self, http, cache):
        self._setup_get_uncached(http, cache)

        code = get_codevalue("STATUS", 1)

        self.assertIsInstance(code, CodeValue)


    def test_get_uncached_id(self, http, cache):
        self._setup_get_uncached(http, cache)

        code = get_codevalue("STATUS", 1)

        self.assertEqual(code.id, 1)


    def test_get_uncached_calls_cache(self, http, cache):
        self._setup_get_uncached(http, cache)

        get_codevalue("STATUS", 1)

        cache.get.assert_called_once_with("staticdata-STATUS-1")


    def test_get_uncached_makes_request(self, http, cache):
        self._setup_get_uncached(http, cache)

        get_codevalue("STATUS", 1)

        self.assertEqual(
            http.request.call_args[1]["uri"],
            "http://fake.base/staticData/values/STATUS?_type=json")


    def test_get_uncached_sets_cache(self, http, cache):
        self._setup_get_uncached(http, cache)

        get_codevalue("STATUS", 1)

        self.assertEqual(
            sorted(cache.set_many.call_args[0][0].keys()),
            ["staticdata-STATUS-1", "staticdata-STATUS-2"])


    def test_get_uncached_sets_no_cache_timeout(self, http, cache):
        self._setup_get_uncached(http, cache)

        get_codevalue("STATUS", 1)

        self.assertEqual(cache.set_many.call_args[0][1], 0)


    def test_get_cached_returns_from_cache(self, http, cache):
        code = get_codevalue("STATUS", 1)

        self.assertIs(code, cache.get.return_value)


    def test_get_cached_calls_cache(self, http, cache):
        get_codevalue("STATUS", 1)

        cache.get.assert_called_once_with("staticdata-STATUS-1")


    def test_get_cached_makes_no_http_request(self, http, cache):
        get_codevalue("STATUS", 1)

        http.request.assert_not_called()
