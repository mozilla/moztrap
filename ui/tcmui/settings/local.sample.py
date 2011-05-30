"""
Settings overrides for a particular deployment of this app. Aside from the two
required settings at the top, the defaults should be suitable for local
development; other settings below are likely to need adjustment for a staging
or production deployment.

Copy local.sample.py to local.py and modify as needed.

"""

# Set these to IDs of actual company/roles; use "./manage.py create_company" to
# create them if needed.
TCM_COMPANY_ID = 0
TCM_NEW_USER_ROLE_ID = 0

#TCM_API_BASE = "http://localhost:8080/tcm/services/v2/rest/"
#TCM_ADMIN_USER = "admin@utest.com"
#TCM_ADMIN_PASS = "admin"

#DEBUG = False
#TEMPLATE_DEBUG = False

# This email address will get emailed on 500 server errors.
#ADMINS = [
#    ("Some One", "someone@mozilla.com"),
#]


# Causes CSS/JS to be served in a single combined, minified file, with a name
# based on contents hash (thus can be safely far-futures-expired).  This
# setting requires the Django server process to have write access to
# STATIC_ROOT (or, more specifically, a CACHE/ subdirectory of it), as minified
# combined files are generated on-demand if the underlying files have
# changed. If static files are hosted off-site, a custom Django file storage
# handler can be used as well.
#COMPRESS = True

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

# If a mail server is not available at localhost:25, set these to appropriate
# values:
#EMAIL_HOST = ""
#EMAIL_PORT = ""
# If the mail server configured above requires authentication and/or TLS:
#EMAIL_USE_TLS = True
#EMAIL_HOST_USER = ""
#EMAIL_HOST_PASSWORD = ""
