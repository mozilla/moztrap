import httplib

from django.core.cache import cache

from .conf import conf



class CachingHttpWrapper(object):
    """
    Wraps an httplib2.Http-compatible object, providing a compatible
    ``request`` method and wrapping it with some basic smart caching
    behavior.

    The wrapper is instantiated with a list of ``bucket`` names (strings). All
    200 OK responses to GET requests are cached with a key specific to each
    bucket, plus a "generation" integer specific to each bucket stored
    separately in the cache. Anytime a non-safe request (anything but "GET" or
    "HEAD") passes through the wrapper, the "generation" integer for each
    bucket is incremented in the cache, effectively clearing the cache for
    those buckets.

    In the simplest case, a single bucket name would be passed in, representing
    a particular resource type - so anytime a resource of that type is updated,
    the entire cache for that resource type is cleared. In a more complex case,
    the list of bucket names might include a more specific bucket
    (e.g. resource type plus id) and then a more general one (just resource
    type). Both buckets will be checked for cached responses (first one found
    wins), and any newly-fetched response will be cached in both buckets (so
    future requests that may not know the id in advance can still benefit from
    the cache), but the id-specific bucket won't be cleared by unsafe requests
    to resources with a different id, improving cache hit rate.

    Wrapper accepts an optional iterable of ``dependent_buckets`` -- the
    wrapper won't cache anything in these buckets, but they will have their
    generation key incremented on any unsafe requests. This is useful for
    e.g. clearing the cache of "list" resources when an individual resource is
    updated or deleted.

    """
    def __init__(self, wrapped, buckets, dependent_buckets=None):
        self.wrapped = wrapped
        self.buckets = buckets
        self.dependent_buckets = dependent_buckets or []


    def generation_key(self, bucket):
        return "%s:generation" % bucket


    def next_generation(self):
        for bucket in list(self.buckets) + list(self.dependent_buckets):
            self._next_generation(bucket)


    def _next_generation(self, bucket):
        try:
            return cache.incr(self.generation_key(bucket))
        except ValueError:
            cache.add(self.generation_key(bucket), 1)
            return 1


    def cache_key(self, bucket, uri):
        generation = cache.get(self.generation_key(bucket), 0)
        return "%s-%s-%s" % (bucket, generation, uri)


    def cache_keys(self, uri):
        return [self.cache_key(bucket, uri) for bucket in self.buckets]


    def request(self, **kwargs):
        method = kwargs.get("method", "GET").upper()
        if method == "GET":
            cache_keys = self.cache_keys(kwargs["uri"])
            for cache_key in cache_keys:
                cached = cache.get(cache_key)
                if cached is not None:
                    return cached
        elif method != "HEAD":
            self.next_generation()

        response, content = self.wrapped.request(**kwargs)

        # only cache 200 OK responses to GET queries
        if method == "GET" and response.status == httplib.OK:
            for cache_key in cache_keys:
                cache.set(
                    cache_key, (response, content), conf.TCM_CACHE_SECONDS)

        return (response, content)
