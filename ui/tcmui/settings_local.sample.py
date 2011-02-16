"""
Settings overrides for a particular deployment of this app. The defaults should
be suitable for local development; settings below are likely to need adjustment
for a staging or production deployment.

Copy settings_local.sample.py to settings_local.py and modify as needed.

"""

#TCM_API_BASE = "http://localhost:8080/tcm/services/v2/rest/"
#TCM_ADMIN_USER = "admin@utest.com"
#TCM_ADMIN_PASS = "admin"

#DEBUG = False
#TEMPLATE_DEBUG = False

# Absolute path to directory where static assets will be collected by the
# "collectstatic" management command, and can be served by front-end webserver.
# Defaults to absolute filesystem path to "ui/collected-assets" directory.
#STATIC_ROOT = ""

# Base URL where files in STATIC_ROOT are deployed.
#STATIC_URL = ""

# Uncomment these if the app is served over HTTPS (required for any
# production deployment to avoid session hijacking):
#SESSION_COOKIE_SECURE = True
# http://en.wikipedia.org/wiki/Strict_Transport_Security
#HTTPS_STS_SECONDS = 86400

# A unique (and secret) key for this deployment.
#SECRET_KEY = ""

# Uncomment this (and modify LOCATION appropriately) to use memcached rather
# than local-memory cache. See
# http://docs.djangoproject.com/en/dev/topics/cache/ for more configuration
# options. For faster caching, install pylibmc in place of python-memcached and
# replace MemcachedCache with PyLibMCCache.
#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#        'LOCATION': '127.0.0.1:11211',
#    }
#}
