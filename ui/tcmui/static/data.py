from django.core.cache import cache

from .models import ArrayOfCodeValue

from tcmui.core.conf import conf


def get_codevalue(key, id_):
    code = cache.get(_cache_key(key, id_))
    if code is None:
        array = ArrayOfCodeValue.get(key)
        to_set = {}
        for c in array:
            if c.id == id_:
                code = c
            to_set[_cache_key(key, c.id)] = c
        cache.set_many(to_set, conf.TCM_STATICDATA_CACHE_SECONDS)
    return code



def _cache_key(key, id_):
    return "staticdata-%s-%s" % (key, id_)
