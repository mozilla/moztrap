from functools import wraps

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.template import TemplateSyntaxError

import simplejson as json

from ..core.api import RemoteObject

from .util import redirect_to_login



def login_redirect(function=None, redirect_field_name=None, login_url=None):
    """
    Decorator for views that catches Unauthorized and Forbidden API errors
    raised in a view and redirects to the login URL, with an explanatory
    message in the Forbidden case.

    """
    redirect_field_name = redirect_field_name or "next"

    def decorator(view_func):
        wrapped = unwrap_template_syntax_error(
            RemoteObject.Unauthorized,
            RemoteObject.Forbidden)(force_render(view_func))

        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            try:
                response = wrapped(request, *args, **kwargs)
            except RemoteObject.Unauthorized:
                error_status = 401
                messages.info(
                    request,
                    "Please log in to view this page.")
            except RemoteObject.Forbidden:
                error_status = 403
                messages.warning(
                    request,
                    "Your account does not have sufficient permissions "
                    "to view this page. Please log in with a different account "
                    "or request the needed permissions from the system "
                    "administrator.")
            else:
                return response

            if request.is_ajax():
                error_info = {"login_url": reverse("login")}
                return HttpResponse(json.dumps(error_info), status=error_status)

            return redirect_to_login(
                from_url=request.path,
                redirect_field_name=redirect_field_name,
                login_url=login_url)
        return _wrapped_view

    if function is not None:
        return decorator(function)
    return decorator



def login_required(view_func):
    """
    A decorator to redirect to login if no user is logged in.

    This is only needed to fake login-required on views that aren't doing
    anything dynamic yet (wireframes). Otherwise, an API call will raise
    Unauthorized and the login_redirect decorator is all that's needed.

    """
    @login_redirect
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.auth is None:
            raise RemoteObject.Unauthorized("Must be logged-in.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view



def unwrap_template_syntax_error(*exceptions):
    """
    A decorator to catch TemplateSyntaxError and unwrap it, reraising the
    wrapped exception.

    Only unwraps if the wrapped exception is one of ``exceptions``.

    """

    def decorator(func):
        @wraps(func)
        def _wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except TemplateSyntaxError, e:
                if hasattr(e, "exc_info"):
                    wrapped = e.exc_info[1]
                    if (wrapped in exceptions or
                        isinstance(wrapped, exceptions)):
                        raise wrapped
                raise
        return _wrapped
    return decorator



def force_render(view_func):
    """
    A view decorator to force immediate rendering of a TemplateResponse.

    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        if hasattr(response, "render") and callable(response.render):
            response.render()
        return response
    return _wrapped_view
