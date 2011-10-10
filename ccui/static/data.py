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
from django.core.cache import cache

from .models import ArrayOfCodeValue

from ccui.core.conf import conf


def get_codevalue(key, id_):
    code = cache.get(_cache_key(key, id_))
    if code is None:
        array = ArrayOfCodeValue.get(key)
        to_set = {}
        for c in array:
            if c.id == id_:
                code = c
            to_set[_cache_key(key, c.id)] = c
        cache.set_many(to_set, conf.CC_STATICDATA_CACHE_SECONDS)
    return code



def _cache_key(key, id_):
    return "staticdata-%s-%s" % (key, id_)
