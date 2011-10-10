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
from .base import *

try:
    from .local import *
except ImportError:
    pass

CACHES["default"]["VERSION"] = 7
CACHES["default"]["KEY_FUNCTION"] = "ccui.core.cacheconfig.make_key"

COMPRESS_ROOT = STATIC_ROOT
COMPRESS_URL = STATIC_URL

if DEBUG:
    MIDDLEWARE_CLASSES.insert(
        0, "ccui.debug.middleware.AjaxTracebackMiddleware")
    MIDDLEWARE_CLASSES.insert(
        0, "ccui.debug.middleware.RequestLogMiddleware")
    INSTALLED_APPS += ["ccui.debug"]
