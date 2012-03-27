"""
Settings overrides for a particular deployment of this app. The defaults should
be suitable for local development; other settings below are likely to need
adjustment for a staging or production deployment.

Copy local.sample.py to local.py and modify as needed.

"""

# Database settings.
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.mysql",
#         "NAME": "caseconductor",
#         "USER": environ.get("USER", ""),
#         "HOST": "", # empty string == localhost
#         "PASSWORD": "",
#         "STORAGE_ENGINE": "InnoDB",
#         "OPTIONS": {
#                 "init_command": "SET storage_engine=InnoDB",
#             },
#         }
#     }

#DEBUG = False
#TEMPLATE_DEBUG = False

# This must be changed to the correct live deployment URL.
#SITE_URL = "http://localhost:8000"

# This email address will get emailed on 500 server errors.
#ADMINS = [
#    ("Some One", "someone@mozilla.com"),
#]

# These must be uncommented and pointed to a functioning SMTP server or users
# will not be able to register.
#EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
#EMAIL_HOST = "localhost"
#EMAIL_HOST_USER = ""
#EMAIL_HOST_PASSWORD = ""
#EMAIL_PORT = 25
#EMAIL_USE_TLS = False
# Account activation and password reset emails will come from this address
#DEFAULT_FROM_EMAIL = "do-not-reply@example.com"

# Uncomment these if the app is served over HTTPS (required for any
# production deployment to avoid session hijacking):
#SESSION_COOKIE_SECURE = True
# http://en.wikipedia.org/wiki/Strict_Transport_Security
#SECURE_HSTS_SECONDS = 86400

# A unique (and secret) key for this deployment.
#SECRET_KEY = "replace this with some random characters"

# A dictionary of keys to use in password hashing.
#HMAC_KEYS = {
#    "2011-12-13": "replace this with some random characters"
#}

# Absolute path to directory where static assets will be collected by the
# "collectstatic" management command, and can be served by front-end webserver.
# Defaults to absolute filesystem path to "collected-assets/" directory.
#STATIC_ROOT = ""

# Base URL where files in STATIC_ROOT are deployed. Defaults to "/static/".
#STATIC_URL = ""

# Absolute path to directory where user-uploaded files (attachments) will be
# stored. Defaults to absolute filesystem path to "media/" directory.
#MEDIA_ROOT = ""

# Base URL where user-uploaded files will be served. In production mode, Case
# Conductor will not serve these files; the front-end webserver must be
# configured to serve the files at ``MEDIA_ROOT`` at this URL. Defaults to
# "/media/".
#MEDIA_URL = ""

# If user-uploaded files should not be stored on the local filesystem, set this
# to the dotted path to a custom Django file storage backend, such as the
# Amazon S3 backend included in django-storages
# (http://code.welldev.org/django-storages/). See the Django file storage
# backend documentation: https://docs.djangoproject.com/en/dev/topics/files/
#DEFAULT_FILE_STORAGE = ""

# Causes CSS/JS to be served in a single combined, minified file, with a name
# based on contents hash (thus can be safely far-futures-expired). With the
# below two settings uncommented, run "python manage.py collectstatic" followed
# by "python manage.py compress": the contents of ``STATIC_ROOT`` can then be
# deployed into production.
#COMPRESS_ENABLED = True
#COMPRESS_OFFLINE = True

# Uncomment this (and modify LOCATION appropriately) to use memcached rather
# than local-memory cache. See
# http://docs.djangoproject.com/en/dev/topics/cache/ for more configuration
# options. For faster caching, install pylibmc in place of python-memcached and
# replace MemcachedCache with PyLibMCCache.
#CACHES = {
#    "default": {
#        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
#        "LOCATION": "127.0.0.1:11211",
#        "KEY_PREFIX": "", # add a global key prefix here if necessary
#    }
#}
