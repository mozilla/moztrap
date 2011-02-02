from django.conf import settings
from django.core import urlresolvers
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect

from ..core.api import Credentials
from ..core.util import add_to_querystring

from .models import User



def login(request, user):
    """
    Persist the given user in the session.

    """
    # @@@ should not be storing plaintext auth info in session, but currently
    #     API doesn't allow for any other authentication method
    request.session["userid"] = user.auth.userid
    request.session["password"] = user.auth.password
    user.login()



def logout(request):
    """
    Remove any logged-in user from the session, and flush all session data.

    """
    request.user.logout()
    request.session.flush()



def get_user(userid, password):
    """
    Tries to fetch the user matching the given credentials. Returns a User
    object if successful, otherwise None.

    """
    auth = Credentials(userid, password)
    try:
        user = User.current(auth=auth)
        user.deliver()
    except (User.Forbidden, User.Unauthorized):
        user = None
    return user


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

    if " " in to or "//" in to:
        raise SuspiciousOperation(
            "Redirect should not have spaces or be absolute.")

    # Finally, fall back and assume it's a URL
    return to


def redirect_to_login(from_url, redirect_field_name=None, login_url=None):
    redirect_to = add_to_querystring(
        resolve_url(login_url or settings.LOGIN_URL),
        **{redirect_field_name: from_url}
        )
    return HttpResponseRedirect(redirect_to)
