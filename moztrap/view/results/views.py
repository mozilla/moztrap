"""
Home results view.

"""
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from cc.view.utils.auth import login_maybe_required



@login_maybe_required
def home(request):
    """Results home redirects to list of active test runs, with finder open."""
    return redirect(
        reverse("results_runs") + "?openfinder=1&filter-status=active")
