from ccui.settings.base import *

CC_API_BASE = "http://fake.base/rest"

CC_COMPANY_ID = 1

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

CC_CACHE_SECONDS = 600
CC_STATICDATA_CACHE_SECONDS = 1800

DEBUG_PROPAGATE_EXCEPTIONS = True

MEDIA_URL = "/media/"
COMPRESS_URL = "/static/"

# configure a null root handler to silence "no handler" warnings
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "null": {
            "level": "CRITICAL",
            "class": "logging.StreamHandler",
            }
        },
    "loggers": {
        "": {
            "handlers": ["null"],
            }
        }
    }
