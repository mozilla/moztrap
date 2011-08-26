from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ..users.decorators import login_redirect
from ..testexecution.models import TestRunList

from .forms import EnvironmentSelectionForm



@login_redirect
def set_environment(request, testrun_id):
    """
    Given a test run ID, allow the user to choose a valid environment-group
    from among those valid for that test run, set that environment-group ID in
    the user's session, and redirect to that test run.

    """
    run = TestRunList.get_by_id(testrun_id, auth=request.auth)

    form = EnvironmentSelectionForm(
        request.POST or None,
        groups=run.environmentgroups,
        current=request.session.get("environments", None))

    if request.method == "POST" and form.is_valid():
        request.session["environments"] = form.save()
        return redirect("runtests_run", testrun_id=testrun_id)

    return TemplateResponse(
        request,
        "runtests/environment.html",
        {"form": form,
         "testrun": run,
         })
