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
from .util import get_user



def get_user_from_request(request):
    userid = request.session.get("userid")
    cookie = request.session.get("cookie")

    user = None
    if userid and cookie:
        user = get_user(userid, cookie=cookie)
        if not user:
            request.session.flush()
    return user



class LazyUser(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_user'):
            request._cached_user = get_user_from_request(request)
        return request._cached_user



class LazyAuth(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_auth'):
            request._cached_auth = None
            if request.user:
                request._cached_auth = request.user.auth
        return request._cached_auth



class AuthenticationMiddleware(object):
    def process_request(self, request):
        request.__class__.user = LazyUser()
        request.__class__.auth = LazyAuth()
