"""
Settings for tests.

"""
from moztrap.settings.default import *

DEFAULT_FILE_STORAGE = "tests.storage.MemoryStorage"
ALLOW_ANONYMOUS_ACCESS = False
SITE_URL = "http://localhost:80"
USE_BROWSERID = True
