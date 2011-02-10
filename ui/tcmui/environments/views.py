from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ..users.decorators import login_required

from .forms import EnvironmentSelectionForm
from .models import EnvironmentGroup



@login_required
def set_environment(request):
    """
    Given a list of environment-group IDs (in the GET querystring), allow the
    user to choose a valid environment-group from among those, set that
    environment-group ID in the user's session, and redirect to the list of
    test cycles for that environment (or a "next" URL given in querystring).

    """
    next = request.REQUEST.get("next", "products")

    groups = [
        EnvironmentGroup.get(
            "environmentgroups/%s" % gid,
            auth=request.auth)
        for gid in request.GET.getlist("gid")
        ]

    form = EnvironmentSelectionForm(
        request.POST or None,
        groups=groups,
        current=request.session.get("environments", None))

    if request.method == "POST" and form.is_valid():
        request.session["environments"] = form.save()
        return redirect(next)

    return TemplateResponse(
        request,
        "test/environment.html",
        {"form": form,
         "next": next
         })
