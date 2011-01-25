from functools import wraps

from django.conf import settings
from django.http import HttpResponseRedirect

from ..core.util import add_to_querystring

from .util import redirect_url

def user_passes_test(test_func, redirect_field_name=None, login_url=None):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.

    """
    redirect_field_name = redirect_field_name or "next"

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            redirect_to = add_to_querystring(
                redirect_url(login_url or settings.LOGIN_URL),
                **{redirect_field_name: request.path}
                )
            return HttpResponseRedirect(redirect_to)
        return _wrapped_view
    return decorator


def login_required(function=None, redirect_field_name=None, login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u is not None,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
