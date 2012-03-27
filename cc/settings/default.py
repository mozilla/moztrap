from .base import *

try:
    from .local import *
except ImportError:
    pass

CACHES["default"]["VERSION"] = 1

if DEBUG:
    MIDDLEWARE_CLASSES.insert(
        0, "cc.debug.middleware.AjaxTracebackMiddleware")

    LOGGING["handlers"]["console"] = {
        "level": "DEBUG",
        "class": "logging.StreamHandler",
        }

    LOGGING["root"] = {"handlers": ["console"]}

try:
    HMAC_KEYS
except NameError:
    HMAC_KEYS = {"default": SECRET_KEY}
