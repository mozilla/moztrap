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
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured



class Configuration(object):
    def __init__(self, **kwargs):
        self.defaults = kwargs


    def __getattr__(self, k):
        try:
            return getattr(settings, k)
        except AttributeError:
            if k in self.defaults:
                return self.defaults[k]
            raise ImproperlyConfigured("%s setting is required." % k)


conf = Configuration(
    CC_CACHE_SECONDS=600,
    CC_STATICDATA_CACHE_SECONDS=1200,
    CC_DEBUG_API_LOG_RECORDS=1000,
    CC_DEBUG_API_LOG=False,
    )
