import httplib

from django.core.cache import cache

from .conf import conf



class CachingHttpWrapper(object):
    def __init__(self, wrapped):
        self._wrapped = wrapped


    def request(self, **kwargs):
        method = kwargs.get("method", "GET").upper()
        if method == "GET":
            cache_key = kwargs["uri"]
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

        response, content = self._wrapped.request(**kwargs)

        # only cache 200 OK responses to GET queries
        if method == "GET" and response.status == httplib.OK:
            cache.set(cache_key, (response, content), conf.TCM_CACHE_SECONDS)

        return (response, content)
