from .base import *

try:
    from .local import *
except ImportError:
    pass

CACHES["default"]["VERSION"] = 1

if DEBUG:
    MIDDLEWARE_CLASSES.insert(
        0, "cc.debug.middleware.AjaxTracebackMiddleware")

try:
    HMAC_KEYS
except NameError:
    HMAC_KEYS = {"default": SECRET_KEY}
