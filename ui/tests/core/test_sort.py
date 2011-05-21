from mock import Mock
from unittest2 import TestCase



class TestFromRequest(TestCase):
    @property
    def func(self):
        from tcmui.core.sort import from_request
        return from_request


    def _check(self, GET, result):
        request = Mock()
        request.GET = GET
        self.assertEqual(self.func(request), result)


    def test_defaults(self):
        self._check({}, (None, "asc"))


    def test_set(self):
        self._check(
            {"sortfield": "name", "sortdirection": "desc"}, ("name", "desc"))



class TestUrl(TestCase):
    @property
    def func(self):
        from tcmui.core.sort import url
        return url


    def test_basic(self):
        self.assertEqual(
            self.func("http://fake.base/some/", "name", "asc"),
            "http://fake.base/some/?sortfield=name&sortdirection=asc")


    def test_override(self):
        self.assertEqual(
            self.func(
                "http://fake.base/some/?sortfield=status&sortdirection=desc",
                "name", "asc"),
            "http://fake.base/some/?sortfield=name&sortdirection=asc")


    def test_other(self):
        self.assertEqual(
            self.func("http://fake.base/some/?blah=foo", "name", "asc"),
            "http://fake.base/some/?blah=foo&sortdirection=asc&sortfield=name")


    def test_override_with_other(self):
        self.assertEqual(
            self.func(
                "http://fake.base/?b=f&sortfield=status&sortdirection=desc",
                "name", "asc"),
            "http://fake.base/?sortfield=name&sortdirection=asc&b=f")



class TestToggle(TestCase):
    @property
    def func(self):
        from tcmui.core.sort import toggle
        return toggle


    def test_asc(self):
        self.assertEqual(self.func("asc"), "desc")


    def test_desc(self):
        self.assertEqual(self.func("desc"), "asc")
