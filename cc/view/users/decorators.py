"""
Auth-related decorators.

"""
from functools import wraps

from django.conf import settings
from django.shortcuts import redirect
from django.utils.decorators import available_attrs

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login




def permission_required(perm):
    """
    View decorator to check user permissions and redirect as needed.

    If user is logged in but has insufficient permissions, redirects to the
    home page.

    If user is not logged in, redirects to login.

    """
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if request.user.has_perm(perm):
                return view_func(request, *args, **kwargs)
            if request.user.is_authenticated():
                return redirect("/")
            return redirect_to_login(
                request.get_full_path(),
                settings.LOGIN_URL,
                REDIRECT_FIELD_NAME,
                )
        return _wrapped_view
    return decorator
