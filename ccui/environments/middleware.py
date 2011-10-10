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
from .models import EnvironmentList, Environment


def get_envs_from_request(request):
    envs = request.session.get("environments", [])

    ret = EnvironmentList(entries=
        [Environment.get("environments/%s" % eid, auth=request.auth)
         for etid, eid in envs])
    ret.auth = request.auth
    return ret



class LazyEnvironments(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_envs'):
            request._cached_envs = get_envs_from_request(request)
        return request._cached_envs



class EnvironmentsMiddleware(object):
    def process_request(self, request):
        request.__class__.environments = LazyEnvironments()
