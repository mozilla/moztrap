from mock import patch, Mock
from unittest2 import TestCase



class CachedHttpTest(TestCase):
    def make_request(self, **kwargs):
        from tcmui.core.api import CachedHttp
        import httplib

        response = Mock()
        response.status = kwargs.pop("response_status", httplib.OK)
        content = kwargs.pop("response_content", "content")
        with patch(
            "tcmui.core.api.httplib2.Http.request",
            Mock(return_value=(response, content))):
            return CachedHttp().request(**kwargs)


    def test_caches_get(self):
        with patch("tcmui.core.api.cache") as cache:
            cache.get = Mock(return_value=None)

            ret = self.make_request(method="GET", uri="/uri/")

            cache.set.assert_called_with("/uri/", ret, 600)




    def _test_doesnt_cache(self, method):
        with patch("tcmui.core.api.cache") as cache:
            self.make_request(method=method, uri="/uri/")

            self.assertFalse(cache.get.called)
            self.assertFalse(cache.set.called)


    def test_put_doesnt_cache(self):
        self._test_doesnt_cache("PUT")


    def test_post_doesnt_cache(self):
        self._test_doesnt_cache("POST")


    def test_delete_doesnt_cache(self):
        self._test_doesnt_cache("DELETE")


    def test_doesnt_cache_non_OK(self):
        with patch("tcmui.core.api.cache") as cache:
            cache.get = Mock(return_value=None)

            self.make_request(method="GET", uri="/uri/", response_status=401)

            self.assertTrue(cache.get.called)
            self.assertFalse(cache.set.called)


    def test_returns_cached_for_get(self):
        with patch("tcmui.core.api.cache") as cache:
            cache.get = Mock(return_value="cached")

            ret = self.make_request(method="GET", uri="/uri/")

            cache.get.assert_called_with("/uri/")
            self.assertEqual(ret, "cached")



class CredentialsTest(TestCase):
    def get_creds(self, *args, **kwargs):
        from tcmui.core.api import Credentials
        return Credentials(*args, **kwargs)


    def test_with_password(self):
        c = self.get_creds("user@example.com", password="blah")

        self.assertEqual(
            c.headers(),
            {
                "authorization": "Basic dXNlckBleGFtcGxlLmNvbTpibGFo"
                }
            )


    def test_with_cookie(self):
        c = self.get_creds("user@example.com", cookie="USERTOKEN: value")

        self.assertEqual(
            c.headers(),
            {
                "cookie": "USERTOKEN: value"
                }
            )


    def test_with_both(self):
        c = self.get_creds(
            "user@example.com", password="blah", cookie="USERTOKEN: value")

        self.assertEqual(
            c.headers(),
            {
                "authorization": "Basic dXNlckBleGFtcGxlLmNvbTpibGFo"
                }
            )


    def test_with_neither(self):
        c = self.get_creds("user@example.com")

        self.assertEqual(c.headers(), {})


    def test_repr(self):
        c = self.get_creds("user@example.com")

        self.assertEqual(repr(c), "<Credentials: user@example.com>")
