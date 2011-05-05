import httplib

from django.core.cache import get_cache
from mock import patch, Mock
from unittest2 import TestCase

from ..responses import response
from ..utils import ResourceTestCase



@patch("tcmui.core.cache.cache", spec=["get", "set", "incr", "add"])
class CachingHttpWrapperTest(TestCase):
    def make_request(self, **kwargs):
        from tcmui.core.cache import CachingHttpWrapper

        res = Mock(["status"])
        res.status = kwargs.pop("response_status", httplib.OK)
        content = kwargs.pop("response_content", "content")
        bucket = kwargs.pop("cache_bucket", "BucketName")
        with patch("tcmui.core.api.Http") as http:
            http.request.return_value = (res, content)
            return CachingHttpWrapper(http, bucket).request(**kwargs)


    def fill_cache(self, cache, values_dict):
        cache.get.side_effect = lambda k, d=None: values_dict.get(k, d)


    def test_caches_get(self, cache):
        self.fill_cache(cache, {})

        ret = self.make_request(method="GET", uri="/uri/")

        cache.set.assert_called_with("BucketName-1-/uri/", ret, 600)


    def _check_increments_generation(self, method, cache):
        self.make_request(method=method, uri="/uri/")

        cache.add.assert_called_once_with("BucketName:generation", 1)
        cache.incr.assert_called_once_with("BucketName:generation")

        # no cached response was set
        self.assertFalse(cache.set.called)


    def test_put_increments_generation(self, cache):
        self._check_increments_generation("PUT", cache)


    def test_post_increments_generation(self, cache):
        self._check_increments_generation("POST", cache)


    def test_delete_increments_generation(self, cache):
        self._check_increments_generation("DELETE", cache)


    def test_head_doesnt_cache_or_increment_generation(self, cache):
        self.make_request(method="HEAD", uri="/uri/")

        self.assertFalse(cache.add.called)
        self.assertFalse(cache.incr.called)
        self.assertFalse(cache.set.called)


    def test_doesnt_cache_non_OK(self, cache):
        cache.get.return_value = None

        self.make_request(method="GET", uri="/uri/", response_status=401)

        self.assertTrue(cache.get.called)
        self.assertFalse(cache.set.called)


    def test_returns_cached_for_get(self, cache):
        self.fill_cache(cache, {"BucketName-1-/uri/": "cached"})

        ret = self.make_request(method="GET", uri="/uri/")

        cache.get.assert_called_with("BucketName-1-/uri/")
        self.assertEqual(ret, "cached")


    def test_cache_set_uses_generational_key(self, cache):
        self.fill_cache(cache, {"BucketName:generation": 3})

        ret = self.make_request(method="GET", uri="/uri/")

        cache.set.assert_called_with("BucketName-3-/uri/", ret, 600)


    def test_cache_get_uses_generational_key(self, cache):
        self.fill_cache(cache, {
                "BucketName:generation": 4,
                "BucketName-4-/uri/": "result"
                })

        ret = self.make_request(method="GET", uri="/uri/")

        cache.get.assert_called_with("BucketName-4-/uri/")
        self.assertEqual(ret, "result")



@patch("tcmui.core.api.userAgent", spec=["request"])
class CachingFunctionalTest(ResourceTestCase):
    def setUp(self):
        self.cache = get_cache("django.core.cache.backends.locmem.LocMemCache")
        self.cache.clear()
        self.patcher = patch("tcmui.core.cache.cache", self.cache)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)


    RESOURCE_DEFAULTS = {
        "name": "Default name",
        }


    def get_resource_class(self):
        from tcmui.core.api import RemoteObject, fields

        class TestResource(RemoteObject):
            name = fields.Field()

            cache = True

            def __unicode__(self):
                return u"__unicode__ of %s" % self.name

        return TestResource


    def get_resource_list_class(self):
        from tcmui.core.api import ListObject, fields

        class TestResourceList(ListObject):
            entryclass = self.resource_class
            api_name = "testresources"
            default_url = "testresources"
            cache = True

            entries = fields.List(fields.Object(self.resource_class))

        return TestResourceList


    def test_list_cache(self, http):
        http.request.return_value = response(
            self.make_array({"name": "One thing"}))

        lst = self.resource_list_class.get(auth=self.auth)
        lst.deliver()

        lst2 = self.resource_list_class.get(auth=self.auth)
        lst2.deliver()

        self.assertEqual(lst.api_data, lst2.api_data)
        self.assertEqual(http.request.call_count, 1)


    def test_single_cache(self, http):
        http.request.return_value = response(
            self.make_one(name="One thing"))

        obj = self.resource_class.get("testresources/1", auth=self.auth)
        obj.deliver()

        obj2 = self.resource_class.get("testresources/1", auth=self.auth)
        obj2.deliver()

        self.assertEqual(obj.api_data, obj2.api_data)
        self.assertEqual(http.request.call_count, 1)


    def test_post_clears_list_cache(self, http):
        http.request.return_value = response(
            self.make_array({"name": "One thing"}))

        lst = self.resource_list_class.get(auth=self.auth)
        lst.deliver()

        http.request.return_value = response(
            self.make_one(name="New thing"))

        new = self.resource_class(name="New thing")
        lst.post(new, auth=self.auth)

        http.request.return_value = response(
            self.make_array({"name": "One thing"}, {"name": "New thing"}))

        lst2 = self.resource_list_class.get(auth=self.auth)
        lst2.deliver()

        self.assertEqual(len(lst2), 2)
        self.assertEqual(http.request.call_count, 3,
                         http.request.call_args_list)


    def test_put_clears_single_cache(self, http):
        http.request.return_value = response(
            self.make_one(name="One thing"))

        obj = self.resource_class.get("testresources/1", auth=self.auth)
        obj.deliver()

        http.request.return_value = response(
            self.make_one(name="New name"))

        obj.name = "New name"
        obj.put()

        obj2 = self.resource_class.get("testresources/1", auth=self.auth)
        obj2.deliver()

        self.assertEqual(obj2.name, "New name")
        self.assertEqual(http.request.call_count, 3,
                         http.request.call_args_list)
