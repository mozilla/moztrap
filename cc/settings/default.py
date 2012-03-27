# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-2012 Mozilla
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
from .base import *

try:
    from .local import *
except ImportError:
    pass

CACHES["default"]["VERSION"] = 1

if DEBUG:
    MIDDLEWARE_CLASSES.insert(
        0, "cc.debug.middleware.AjaxTracebackMiddleware")

    LOGGING["handlers"]["console"] = {
        "level": "DEBUG",
        "class": "logging.StreamHandler",
        }

    LOGGING["root"] = {"handlers": ["console"]}

try:
    HMAC_KEYS
except NameError:
    HMAC_KEYS = {"default": SECRET_KEY}
