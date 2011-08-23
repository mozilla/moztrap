from django.conf import settings
from django.core.exceptions import ImproperlyConfigured



class Configuration(object):
    def __init__(self, **kwargs):
        self.defaults = kwargs


    def __getattr__(self, k):
        try:
            return getattr(settings, k)
        except AttributeError:
            if k in self.defaults:
                return self.defaults[k]
            raise ImproperlyConfigured("%s setting is required." % k)


conf = Configuration(
    TCM_CACHE_SECONDS=600,
    TCM_STATICDATA_CACHE_SECONDS=1200,
    TCM_DEBUG_API_LOG_RECORDS=1000,
    TCM_DEBUG_API_LOG=False,
    )
