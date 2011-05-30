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
