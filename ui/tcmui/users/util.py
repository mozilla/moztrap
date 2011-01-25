from django.core import urlresolvers

from ..core.api import Credentials

from .models import User



def login(request, user):
    """
    Persist the given user in the session.

    """
    request.session["userid"] = user.auth.userid
    request.session["password"] = user.auth.password



def logout(request):
    """
    Remove any logged-in user from the session, and flush all session data.

    """
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


def redirect_url(to, *args, **kwargs):
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
