from .default_settings import *

try:
    from .settings_local import *
except ImportError:
    pass

CACHES["default"]["VERSION"] = 3

COMPRESS_ROOT = STATIC_ROOT
COMPRESS_URL = STATIC_URL
