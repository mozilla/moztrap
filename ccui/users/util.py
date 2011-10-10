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
from django.core import urlresolvers
from django.http import HttpResponseRedirect

from ..core.util import update_querystring
from .auth import UserCredentials



def login(request, user):
    """
    Persist the given user in the session.

    """
    request.session["userid"] = user.auth.userid
    request.session["cookie"] = user.login()



def logout(request):
    """
    Remove any logged-in user from the session, and flush all session data.

    """
    if request.user:
        request.user.logout()
    request.session.flush()



def get_user(userid, password=None, cookie=None):
    """
    Tries to fetch the user matching the given credentials. Returns a User
    object if successful, otherwise None.

    """
    auth = UserCredentials(userid, password=password, cookie=cookie)
    return auth.user


def resolve_url(to, *args, **kwargs):
    """
    Accept a URL, a view function, or a reversible name (dotted path to view
    function or named URL), and return the resolved URL.

    """
    try:
        return urlresolvers.reverse(to, args=args, kwargs=kwargs)
    except urlresolvers.NoReverseMatch:
        # If this is a callable, re-raise.
        if callable(to):
            raise
        # If this doesn't "feel" like a URL, re-raise.
        if '/' not in to and '.' not in to:
            raise

    # Finally, fall back and assume it's a URL
    return to


def redirect_to_login(from_url, redirect_field_name=None, login_url=None):
    redirect_to = update_querystring(
        resolve_url(login_url or settings.LOGIN_URL),
        **{redirect_field_name: from_url}
        )
    return HttpResponseRedirect(redirect_to)
