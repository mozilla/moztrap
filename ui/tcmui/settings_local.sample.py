"""
Settings overrides for a particular deployment of this app. The defaults should
be suitable for local development; settings below are likely to need adjustment
for a staging or production deployment.

Copy settings_local.sample.py to settings_local.py and modify as needed.

"""

#DEBUG = False
#TEMPLATE_DEBUG = False

# Absolute path to directory where static media will be collected by the
# "collect_static management command, and can be served by front-end webserver.
#STATIC_ROOT = ""

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
