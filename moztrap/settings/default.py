from .base import *

try:
    from .local import *
except ImportError:
    pass

CACHES["default"]["VERSION"] = 1

if DEBUG:
    MIDDLEWARE_CLASSES.insert(
        0, "moztrap.debug.middleware.AjaxTracebackMiddleware")

try:
    HMAC_KEYS
except NameError:
    HMAC_KEYS = {"default": SECRET_KEY}

LOGGING["handlers"]["null"] = {
    'level':'DEBUG',
    'class':'django.utils.log.NullHandler',
    }
LOGGING["loggers"]["moztrap"] = {
    "handlers": ["null"], # replace this in local.py if you want logging
    "level": "ERROR",
    "propagate": True,
    }

