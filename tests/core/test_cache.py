import httplib

from mock import patch, Mock
from unittest2 import TestCase

from ..builder import ListBuilder
from ..responses import response, make_identity
from ..utils import ResourceTestCase, fill_cache, CachingFunctionalTestMixin



NO_CHECK = object() # sentinel value



@patch("ccui.core.cache.zlib.compress", lambda x: "zlib:%s" % x)
@patch("ccui.core.cache.zlib.decompress", lambda x: x[5:])
@patch("ccui.core.cache.cache", spec=["get", "set", "incr", "add"])
class CachingHttpWrapperTest(TestCase):
    def make_request(self, **kwargs):
        from ccui.core.cache import CachingHttpWrapper

        res = Mock(["status"])
        res.status = kwargs.pop("response_status", httplib.OK)
        content = kwargs.pop("response_content", "content")
        permissions = kwargs.pop("permissions", [])
        buckets = kwargs.pop("cache_buckets", ["BucketName"])
        dependent_buckets = kwargs.pop("cache_dependent_buckets", [])
        with patch("ccui.core.api.Http") as http:
            http.request.return_value = (res, content)
            return CachingHttpWrapper(
                http, permissions, buckets, dependent_buckets).request(**kwargs)


    def check_cached(self, cache, key,
                     data=NO_CHECK, perms=NO_CHECK, timeout=NO_CHECK):
        """
        Verify that something was cached under the given key, optionally also
        verifying the data that was cached, the perms it was cached with, and
        the cache timeout.

        Looks at all recorded calls to cache.set, not just the most recent.

        """
        found = False
        for args, kwargs in cache.set.call_args_list:
            c_key, (c_perms, c_data), c_timeout = args
            # undo the fake "compression"
            c_data = (c_data[0], c_data[1][5:])
            if (c_key == key and
                (data is NO_CHECK or c_data == data) and
                (perms is NO_CHECK or c_perms == perms) and
                (timeout is NO_CHECK or c_timeout == timeout)):
                found = True

        if not found:
            msg = "Cache key %r not set" % key
            if data is not NO_CHECK:
                msg += " to %r" % (data,)
            if perms is not NO_CHECK:
                msg += " with perms %r" % (perms,)
            if timeout is not NO_CHECK:
                msg += " with timeout %r" % timeout
            self.fail(
                "%s; cache.set call args: %s" % (msg, cache.set.call_args_list))


    def test_caches_get(self, cache):
        fill_cache(cache, {})

        ret = self.make_request(method="GET", uri="/uri/")

        self.check_cached(cache, "BucketName-0-/uri/", ret)


    def _check_increments_generation(self, method, cache):
        cache.incr.side_effect = ValueError

        self.make_request(method=method, uri="/uri/")

        cache.add.assert_called_once_with("BucketName:generation", 1, 1200)
        cache.incr.assert_called_once_with("BucketName:generation")

        # no cached response was set
        self.assertFalse(cache.set.called)


    def test_put_increments_generation(self, cache):
        self._check_increments_generation("PUT", cache)


    def test_post_increments_generation(self, cache):
        self._check_increments_generation("POST", cache)


    def test_delete_increments_generation(self, cache):
        self._check_increments_generation("DELETE", cache)


    def test_dependent_buckets(self, cache):
        cache.incr.side_effect = ValueError

        self.make_request(method="PUT", uri="/uri/",
                          cache_dependent_buckets=["DependentBucket"])

        cache.add.assert_called_with("DependentBucket:generation", 1, 1200)
        cache.incr.assert_called_with("DependentBucket:generation")

        # no cached response was set
        self.assertFalse(cache.set.called)


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
        fill_cache(
            cache,
            {"BucketName-0-/uri/": (
                    set([frozenset()]), ("res", "zlib:cached"))})

        ret = self.make_request(method="GET", uri="/uri/")

        cache.get.assert_called_with("BucketName-0-/uri/")
        self.assertEqual(ret, ("res", "cached"))


    def test_cache_set_uses_generational_key(self, cache):
        fill_cache(cache, {"BucketName:generation": 3})

        ret = self.make_request(method="GET", uri="/uri/")

        self.check_cached(cache, "BucketName-3-/uri/", ret)


    def test_cache_get_uses_generational_key(self, cache):
        fill_cache(cache, {
                "BucketName:generation": 4,
                "BucketName-4-/uri/": (
                    set([frozenset()]), ("res", "zlib:result"))
                })

        ret = self.make_request(method="GET", uri="/uri/")

        cache.get.assert_called_with("BucketName-4-/uri/")
        self.assertEqual(ret, ("res", "result"))


    def test_multiple_buckets_both_filled(self, cache):
        fill_cache(cache, {})

        ret = self.make_request(method="GET", uri="/uri/",
                                cache_buckets=["BucketName:1", "BucketName"])

        self.check_cached(cache, "BucketName:1-0-/uri/", ret)
        self.check_cached(cache, "BucketName-0-/uri/", ret)


    def test_multiple_buckets_both_checked(self, cache):
        fill_cache(
            cache,
            {"BucketName-0-/uri/": (
                    set([frozenset()]), ("res", "zlib:cached"))})

        ret = self.make_request(method="GET", uri="/uri/",
                                cache_buckets=["BucketName:1", "BucketName"])

        self.assertEqual(
            cache.get.call_args_list[-2:],
            [(("BucketName:1-0-/uri/",),), (("BucketName-0-/uri/",),)])
        self.assertEqual(ret, ("res", "cached"))


    def test_multiple_buckets_incremented(self, cache):
        cache.incr.side_effect = ValueError

        self.make_request(method="PUT", uri="/uri/",
                          cache_buckets=["BucketName:1", "BucketName"])

        self.assertEqual(
            cache.add.call_args_list,
            [(("BucketName:1:generation", 1, 1200),),
             (("BucketName:generation", 1, 1200),)])
        self.assertEqual(
            cache.incr.call_args_list,
            [(("BucketName:1:generation",),),
             (("BucketName:generation",),)])

        # no cached response was set
        self.assertFalse(cache.set.called)


    def test_cached_response_includes_permissions(self, cache):
        fill_cache(cache, {})

        ret = self.make_request(method="GET", uri="/uri/",
                                permissions=["PERM_ONE"])

        self.check_cached(
            cache, "BucketName-0-/uri/", ret, set([frozenset(["PERM_ONE"])]))


    def test_disjoint_permissions_cant_see_cached_result(self, cache):
        fill_cache(
            cache,
            {"BucketName-0-/uri/":
                 (set([frozenset(["ONE PERM"])]), ("response", "zlib:cached"))})

        res, content = self.make_request(
            method="GET", uri="/uri/", permissions=["TWO_PERM"])

        self.assertEqual(content, "content")


    def test_disjoint_permissions_recached_with_both_sets(self, cache):
        fill_cache(
            cache,
            {"BucketName-0-/uri/":
                 (set([frozenset(["ONE PERM"])]), ("response", "zlib:cached"))})

        ret = self.make_request(
            method="GET", uri="/uri/", permissions=["TWO_PERM"])

        self.check_cached(
            cache, "BucketName-0-/uri/", ret,
            perms=set([frozenset(["ONE PERM"]), frozenset(["TWO_PERM"])]))


    def test_subset_permissions_cant_see_cached_result(self, cache):
        fill_cache(
            cache,
            {"BucketName-0-/uri/":
                 (set([frozenset(["ONE_PERM", "TWO_PERM"])]),
                  ("response", "zlib:cached"))})

        res, content = self.make_request(
            method="GET", uri="/uri/", permissions=["TWO_PERM"])

        self.assertEqual(content, "content")


    def test_subset_permissions_recached_with_just_subset(self, cache):
        fill_cache(
            cache,
            {"BucketName-0-/uri/":
                 (set([frozenset(["ONE_PERM", "TWO_PERM"])]),
                  ("response", "zlib:cached"))})

        ret = self.make_request(
            method="GET", uri="/uri/", permissions=["TWO_PERM"])

        self.check_cached(
            cache, "BucketName-0-/uri/", ret,
            perms=set([frozenset(["TWO_PERM"])]))


    def test_either_permissions_can_see_cached_result(self, cache):
        fill_cache(
            cache,
            {"BucketName-0-/uri/":
                 (set([frozenset(["ONE_PERM"]), frozenset(["TWO_PERM"])]),
                  ("response", "zlib:cached"))})

        res, content = self.make_request(
            method="GET", uri="/uri/", permissions=["TWO_PERM"])

        self.assertEqual(content, "cached")
        self.assertFalse(cache.set.called)


    def test_superset_of_permissions_can_see_cached_result(self, cache):
        fill_cache(
            cache,
            {"BucketName-0-/uri/":
                 (set([frozenset(["TWO_PERM"])]), ("response", "zlib:cached"))})

        res, content = self.make_request(
            method="GET", uri="/uri/", permissions=["ONE_PERM", "TWO_PERM"])

        self.assertEqual(content, "cached")
        self.assertFalse(cache.set.called)


    def test_equal_permissions_can_see_cached_result(self, cache):
        fill_cache(
            cache,
            {"BucketName-0-/uri/":
                 (set([frozenset(["TWO_PERM", "ONE_PERM"])]),
                  ("response", "zlib:cached"))})

        res, content = self.make_request(
            method="GET", uri="/uri/", permissions=["ONE_PERM", "TWO_PERM"])

        self.assertEqual(content, "cached")
        self.assertFalse(cache.set.called)


    def test_generation_increment_success(self, cache):
        from ccui.core.cache import CachingHttpWrapper

        wrapper = CachingHttpWrapper("wrapped", ["perms"], ["BucketName"])

        cache.incr.return_value = 3

        self.assertEqual(wrapper._next_generation("BucketName"), 3)


    def test_generation_increment_race(self, cache):
        """
        If two caching wrappers try to increment the same nonexistent
        generation key at the same time, it should end up at 2, not 1.

        """
        from ccui.core.cache import CachingHttpWrapper

        wrapper = CachingHttpWrapper("wrapped", ["perms"], ["BucketName"])

        # Simulate a second wrapper having won the race between failed incr and
        # add by setting up the incr method to raise ValueError on first call
        # and return 2 on second call, and the add method to return False (not
        # added).
        cache.add.return_value = False
        def _incr(key, called=[]):
            # intentionally using mutable default as collector
            if called:
                return 2
            called.append(True)
            raise ValueError("Key %r not found" % key)
        cache.incr.side_effect = _incr

        self.assertEqual(wrapper._next_generation("BucketName"), 2)


@patch("ccui.core.api.userAgent", spec=["request"])
class CachingFunctionalTest(CachingFunctionalTestMixin, ResourceTestCase):
    builder = ListBuilder(
        "testresource",
        "testresources",
        "Testresource",
        {
        "name": "Default name",
        })


    def get_resource_class(self):
        from ccui.core.api import RemoteObject, fields

        class TestResource(RemoteObject):
            name = fields.Field()

            def __unicode__(self):
                return u"__unicode__ of %s" % self.name

        return TestResource


    def get_resource_list_class(self):
        from ccui.core.api import ListObject, fields

        class TestResourceList(ListObject):
            entryclass = self.resource_class
            api_name = "testresources"
            default_url = "testresources"

            entries = fields.List(fields.Object(self.resource_class))

        return TestResourceList


    def test_list_cache(self, http):
        http.request.return_value = response(
            self.builder.array({"name": "One thing"}))

        lst = self.resource_list_class.get(auth=self.auth)
        lst.deliver()

        lst2 = self.resource_list_class.get(auth=self.auth)
        lst2.deliver()

        self.assertEqual(lst.api_data, lst2.api_data)
        self.assertEqual(http.request.call_count, 1)


    def test_single_cache(self, http):
        http.request.return_value = response(
            self.builder.one(name="One thing"))

        obj = self.resource_class.get("testresources/1", auth=self.auth)
        obj.deliver()

        obj2 = self.resource_class.get("testresources/1", auth=self.auth)
        obj2.deliver()

        self.assertEqual(obj.api_data, obj2.api_data)
        self.assertEqual(http.request.call_count, 1)


    def test_post_clears_list_cache(self, http):
        http.request.return_value = response(
            self.builder.array({"name": "One thing"}))

        lst = self.resource_list_class.get(auth=self.auth)
        lst.deliver()

        http.request.return_value = response(
            self.builder.one(name="New thing"))

        new = self.resource_class(name="New thing")
        lst.post(new, auth=self.auth)

        http.request.return_value = response(
            self.builder.array({"name": "One thing"}, {"name": "New thing"}))

        lst2 = self.resource_list_class.get(auth=self.auth)
        lst2.deliver()

        self.assertEqual(len(lst2), 2)
        self.assertEqual(http.request.call_count, 3,
                         http.request.call_args_list)


    def test_put_clears_single_cache(self, http):
        http.request.return_value = response(
            self.builder.one(name="One thing"))

        obj = self.resource_class.get("testresources/1", auth=self.auth)
        obj.deliver()

        http.request.return_value = response(
            self.builder.one(name="New name"))

        obj.name = "New name"
        obj.put()

        obj2 = self.resource_class.get("testresources/1", auth=self.auth)
        obj2.deliver()

        self.assertEqual(obj2.name, "New name")
        self.assertEqual(http.request.call_count, 3,
                         http.request.call_args_list)


    def test_put_clears_related_list_cache(self, http):
        http.request.return_value = response(
            self.builder.array({"name": "One thing"}))

        lst = self.resource_list_class.get(auth=self.auth)
        lst.deliver()

        http.request.return_value = response(
            self.builder.one(name="New thing"))

        obj = lst[0]
        obj.name = "New name"
        obj.put()

        http.request.return_value = response(
            self.builder.array({"name": "New name"}))

        lst2 = self.resource_list_class.get(auth=self.auth)
        lst2.deliver()

        self.assertEqual(lst2[0].name, "New name")
        self.assertEqual(http.request.call_count, 3,
                         http.request.call_args_list)


    def test_update_one_single_doesnt_clear_another(self, http):
        http.request.return_value = response(
            self.builder.one(
                name="One thing",
                resourceIdentity=make_identity(id=1, url="testresources/1")))

        obj = self.resource_class.get("testresources/1", auth=self.auth)
        obj.deliver()

        http.request.return_value = response(
            self.builder.one(
                name="Another thing",
                resourceIdentity=make_identity(id=2, url="testresources/2")))

        obj2 = self.resource_class.get("testresources/2", auth=self.auth)
        obj2.deliver()

        http.request.return_value = response(
            self.builder.one(
                name="New name",
                resourceIdentity=make_identity(id=2, url="testresources/2")))

        obj2.name = "New name"
        obj2.put()

        first_again = self.resource_class.get("testresources/1", auth=self.auth)
        first_again.deliver()

        self.assertEqual(http.request.call_count, 3)
        self.assertEqual(obj.api_data, first_again.api_data)
