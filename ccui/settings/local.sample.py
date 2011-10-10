# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
# 
# This file is part of Case Conductor.
# 
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
"""
Settings overrides for a particular deployment of this app. Aside from the two
required settings at the top, the defaults should be suitable for local
development; other settings below are likely to need adjustment for a staging
or production deployment.

Copy local.sample.py to local.py and modify as needed.

"""

# Set these to IDs of actual company/roles; use "./manage.py create_company" to
# create them if needed.
CC_COMPANY_ID = 0
CC_NEW_USER_ROLE_ID = 0

#CC_API_BASE = "http://localhost:8080/tcm/services/v2/rest/"
#CC_ADMIN_USER = "admin@utest.com"
#CC_ADMIN_PASS = "admin"

#DEBUG = False
#TEMPLATE_DEBUG = False

# This email address will get emailed on 500 server errors.
#ADMINS = [
#    ("Some One", "someone@mozilla.com"),
#]


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
# based on contents hash (thus can be safely far-futures-expired).  This
# setting requires the Django server process to have write access to
# STATIC_ROOT (or, more specifically, a CACHE/ subdirectory of it), as minified
# combined files are generated on-demand if the underlying files have
# changed. If static files are hosted off-site, a custom Django file storage
# handler can be used as well.
#COMPRESS = True

# Uncomment these if the app is served over HTTPS (required for any
# production deployment to avoid session hijacking):
#SESSION_COOKIE_SECURE = True
# http://en.wikipedia.org/wiki/Strict_Transport_Security
#SECURE_HSTS_SECONDS = 86400

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

# Uncomment and modify this to use a SQLite database file for storing user
# sessions, rather than storing them in cache. This is required if you are
# using the local-memory cache backend and a multi-process webserver. For all
# but the smallest deployments, using the memcached cache backend is
# recommended instead.
#DATABASES['default']['NAME'] = '/path/to/where/you/want/your/sqlite.db'
#SESSION_BACKEND = 'django.contrib.sessions.backends.db'

# If a mail server is not available at localhost:25, set these to appropriate
# values:
#EMAIL_HOST = ""
#EMAIL_PORT = ""
# If the mail server configured above requires authentication and/or TLS:
#EMAIL_USE_TLS = True
#EMAIL_HOST_USER = ""
#EMAIL_HOST_PASSWORD = ""
