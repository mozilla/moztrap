from .base import *

try:
    from .local import *
except ImportError:
    pass

CACHES["default"]["VERSION"] = 7
CACHES["default"]["KEY_FUNCTION"] = "ccui.core.cacheconfig.make_key"

COMPRESS_ROOT = STATIC_ROOT
COMPRESS_URL = STATIC_URL

if DEBUG:
    MIDDLEWARE_CLASSES.insert(
        0, "ccui.debug.middleware.AjaxTracebackMiddleware")
    MIDDLEWARE_CLASSES.insert(
        0, "ccui.debug.middleware.RequestLogMiddleware")
    INSTALLED_APPS += ["ccui.debug"]
