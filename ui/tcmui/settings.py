from .default_settings import *

try:
    from .settings_local import *
except ImportError:
    pass

CACHES["default"]["VERSION"] = 5
CACHES["default"]["KEY_FUNCTION"] = "tcmui.core.cacheconfig.make_key"

COMPRESS_ROOT = STATIC_ROOT
COMPRESS_URL = STATIC_URL
