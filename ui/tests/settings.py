from tcmui.settings.base import *

TCM_API_BASE = "http://fake.base/rest"

TCM_COMPANY_ID = 1

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

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
