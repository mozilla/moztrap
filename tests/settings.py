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
from ccui.settings.base import *

CC_API_BASE = "http://fake.base/rest"

CC_COMPANY_ID = 1

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

CC_CACHE_SECONDS = 600
CC_STATICDATA_CACHE_SECONDS = 1800

DEBUG_PROPAGATE_EXCEPTIONS = True

MEDIA_URL = "/media/"
COMPRESS_URL = "/static/"

# configure a null root handler to silence "no handler" warnings
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "null": {
            "level": "CRITICAL",
            "class": "logging.StreamHandler",
            }
        },
    "loggers": {
        "": {
            "handlers": ["null"],
            }
        }
    }
