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
import base64

from .conf import conf



class Credentials(object):
    """
    Encapsulates credentials necessary to access the API; userid and either
    password or cookie token. Capable of generating appropriate request headers
    using either basic auth (if password is available) or cookie, if
    available).

    """
    def __init__(self, userid, password=None, cookie=None):
        self.userid, self.password, self.cookie = userid, password, cookie


    def headers(self):
        if self.password is not None:
            return self.basic_auth_headers()
        elif self.cookie is not None:
            return self.cookie_headers()
        return {}


    def basic_auth_headers(self):
        return {
            "authorization": (
                "Basic %s"
                % base64.encodestring(
                    "%s:%s" % (self.userid, self.password)
                    )[:-1]
                )
            }


    def cookie_headers(self):
        return {"cookie": self.cookie}


    def __repr__(self):
        return "<Credentials: %s>" % self.userid


    def __eq__(self, other):
        return ((self.userid, self.password, self.cookie) ==
                (other.userid, other.password, other.cookie))



admin = Credentials(conf.CC_ADMIN_USER, conf.CC_ADMIN_PASS)
