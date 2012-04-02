"""
Home management view.

"""
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from cc.view.utils.auth import login_maybe_required



@login_maybe_required
def home(request):
    """Manage home redirects to list of test runs, with finder open."""
    return redirect(reverse("manage_runs") + "?openfinder=1")
