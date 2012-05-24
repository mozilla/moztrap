"""
MozTrap home view.

"""
from django.shortcuts import redirect

from .utils.auth import login_maybe_required



@login_maybe_required
def home(request):
    """Home view; redirects to run-tests or results depending on permissions."""
    if request.user.has_perm("execution.execute"):
        return redirect("runtests")
    return redirect("manage_cases") # @@@ should be run results, once it exists
