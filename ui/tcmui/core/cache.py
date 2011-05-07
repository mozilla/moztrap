import httplib

from django.core.cache import cache

from .conf import conf



class CachingHttpWrapper(object):
    """
    Wraps an httplib2.Http-compatible object, providing a compatible
    ``request`` method and wrapping it with some basic smart caching
    behavior.

    The wrapper is instantiated with a ``bucket_name`` that is intended to be
    an identifier for a particular resource type (i.e. perhaps the name of a
    class representing that resource). It caches all 200 OK responses to GET
    requests. Anytime a non-safe request (anything but "GET" or "HEAD") passes
    through the wrapper, a "generation" integer (specific to the
    ``bucket_name``) is incremented in the cache. This generation is used as
    part of the cache key for all cached responses, so this effectively clears
    the cache for that resource type.

    Wrapper also accepts an iterator of ``dependent_bucket_names`` -- these
    bucket names will also have their generation key incremented on any unsafe
    requests.

    """
    def __init__(self, wrapped, bucket_name, dependent_bucket_names=None):
        self.wrapped = wrapped
        self.bucket_name = bucket_name
        self.dependent_bucket_names = dependent_bucket_names or []


    def generation_key(self, bucket_name=None):
        if bucket_name is None:
            bucket_name = self.bucket_name
        return "%s:generation" % bucket_name


    def next_generation(self):
        for bucket_name in [self.bucket_name] + list(self.dependent_bucket_names):
            self._next_generation(bucket_name)


    def _next_generation(self, bucket_name):
        try:
            return cache.incr(self.generation_key(bucket_name))
        except ValueError:
            cache.add(self.generation_key(bucket_name), 1)
            return 1


    def cache_key(self, uri):
        generation = cache.get(self.generation_key(), 0)
        return "%s-%s-%s" % (self.bucket_name, generation, uri)


    def request(self, **kwargs):
        method = kwargs.get("method", "GET").upper()
        if method == "GET":
            cache_key = self.cache_key(kwargs["uri"])
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
        elif method != "HEAD":
            self.next_generation()

        response, content = self.wrapped.request(**kwargs)

        # only cache 200 OK responses to GET queries
        if method == "GET" and response.status == httplib.OK:
            cache.set(cache_key, (response, content), conf.TCM_CACHE_SECONDS)

        return (response, content)
