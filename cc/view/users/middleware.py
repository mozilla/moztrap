"""
Authentication-related middleware.

"""
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from cc.model.core.auth import AUTO_USERNAME_PREFIX

from . import views



class SetUsernameMiddleware(object):
    """Requires users to set their username before using the site."""
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Redirect users with auto-set username to set their username."""
        if (view_func is not views.set_username and
                request.user.username.startswith(AUTO_USERNAME_PREFIX)):
            return HttpResponseRedirect(reverse("auth_set_username") + "?next=" + request.path)
