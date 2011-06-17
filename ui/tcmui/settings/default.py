from .base import *

try:
    from .local import *
except ImportError:
    pass

CACHES["default"]["VERSION"] = 7
CACHES["default"]["KEY_FUNCTION"] = "tcmui.core.cacheconfig.make_key"

COMPRESS_ROOT = STATIC_ROOT
COMPRESS_URL = STATIC_URL

if DEBUG:
    MIDDLEWARE_CLASSES.insert(0, "tcmui.core.middleware.RequestLogMiddleware")
    INSTALLED_APPS += ["tcmui.debug"]
