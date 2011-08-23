import httplib
import logging
import zlib

from django.core.cache import cache

from .conf import conf
from .log import log_api_call



log = logging.getLogger("tcmui.core.cache")



class CachingHttpWrapper(object):
    """
    Wraps an httplib2.Http-compatible object, providing a compatible
    ``request`` method and wrapping it with some basic caching and cache
    invalidation.

    The cache invalidation approach taken here assumes that all clients of the
    target API share the same cache.

    The wrapper is instantiated with a list of ``bucket`` names (strings). All
    200 OK responses to GET requests are cached with a key specific to each
    bucket, plus a "generation" integer specific to each bucket stored
    separately in the cache. When a non-safe request (anything but "GET" or
    "HEAD") passes through the wrapper, the "generation" integer for each
    bucket is incremented in the cache, effectively clearing the cache for
    those buckets.

    In the simplest case, a single bucket name would be passed in, representing
    a particular resource type - so when a resource of that type is updated,
    created, or deleted, the entire cache for that resource type is cleared.

    In a more complex case, the list of bucket names might first include a more
    specific bucket (e.g. resource type plus object id) and then a more general
    one (just resource type). Both buckets will be checked for cached responses
    (first one found wins), and any newly-fetched response will be cached in
    both buckets (so future requests that may not know the id in advance can
    still benefit from the cache), but the id-specific bucket won't be cleared
    by unsafe requests to resources with a different id, improving cache hit
    rate for requests where the id is known in advance.

    Wrapper accepts an optional iterable of ``dependent_buckets`` -- the
    wrapper won't cache anything in these buckets, but they will have their
    generation key incremented on any unsafe requests. This is useful for
    e.g. clearing the cache of "list" resources when an individual resource is
    updated or deleted.

    The wrapper also supports an abstract concept of permissions, to prevent
    users from seeing cached data that would otherwise be unavailable to
    them. The wrapper is instantiated with a set of permission ids for the
    current user. Each cached response is cached along with a set of sets of
    permission ids of the users that have successfully fetched that
    response. When another user hits that cached response, if their permissions
    are not a superset of one of the sets of permissions that the response was
    cached with, it is considered a cache miss, and the response they get will
    be re-cached with their permission set added, lowering the bar for future
    cache hits.

    """
    def __init__(self, wrapped, permissions, buckets, dependent_buckets=None):
        self.wrapped = wrapped
        self.permissions = frozenset(permissions)
        self.buckets = list(buckets)
        self.dependent_buckets = list(dependent_buckets or [])
        log.debug(
            "Instantiated CachingHttpWrapper for buckets %r and dependents %r"
            % (self.buckets, self.dependent_buckets))


    def generation_key(self, bucket):
        return "%s:generation" % bucket


    def next_generation(self):
        for bucket in self.buckets + self.dependent_buckets:
            self._next_generation(bucket)


    def _next_generation(self, bucket):
        gen_key = self.generation_key(bucket)
        log.debug("Trying to increment generation key %r" % gen_key)
        try:
            val = cache.incr(gen_key)
            log.debug("Incremented generation key %r to %r" % (gen_key, val))
        except ValueError:
            val = 1
            # Cache for twice as long as a regular cache key - ensures that a
            # cached item from a previous generation can never outlive its
            # bucket generation key.
            added = cache.add(gen_key, val, conf.CC_CACHE_SECONDS * 2)
            if not added:
                # Someone else won the race, so we try again to increment.
                log.warn(
                    "Couldn't increment or add gen key %r, trying again"
                    % gen_key)
                val = cache.incr(gen_key)
        return val


    def cache_key(self, bucket, uri):
        generation = cache.get(self.generation_key(bucket), 0)
        return "%s-%s-%s" % (bucket, generation, uri)


    def cache_keys(self, uri):
        return [self.cache_key(bucket, uri) for bucket in self.buckets]


    def request(self, **kwargs):
        method = kwargs.setdefault("method", "GET").upper()
        cache_keys = []

        if method == "GET":
            # track all the permission sets that we may want to re-cache with
            # later.
            all_permsets = set([self.permissions])
            cache_keys = self.cache_keys(kwargs["uri"])
            log.debug(
                "Checking for cached %r in keys %r"
                % (kwargs["uri"], cache_keys))
            for cache_key in cache_keys:
                cached = cache.get(cache_key)
                if cached is not None:
                    log.debug("Found cached response")
                    permsets, (response, compressed_content) = cached
                    content = zlib.decompress(compressed_content)
                    for permset in permsets:
                        # if our permissions are a superset of any of the
                        # permissions this was cached with, we can see the
                        # cached response.
                        if permset.issubset(self.permissions):
                            log.debug("Found acceptable permset, returning.")
                            log_api_call(kwargs, response, content, cache_key)
                            return (response, content)

                        # no need to include a permset that's a superset of our
                        # permissions; anybody who'd pass the one test would be
                        # guaranteed to pass the other
                        if not self.permissions.issubset(permset):
                            all_permsets.add(permset)
        elif method != "HEAD":
            self.next_generation()

        response, content = self.wrapped.request(**kwargs)

        # only cache 200 OK responses to GET queries
        if method == "GET" and response.status == httplib.OK:
            compressed_content = zlib.compress(content)
            log.debug("Caching response under keys %r" % (cache_keys,))
            for cache_key in cache_keys:
                cache.set(
                    cache_key,
                    (all_permsets, (response, compressed_content)),
                    conf.CC_CACHE_SECONDS)

        return (response, content)
