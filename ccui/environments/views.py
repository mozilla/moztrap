# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
# 
# This file is part of Case Conductor.
# 
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ..core.util import get_object_or_404
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
    run = get_object_or_404(TestRunList, testrun_id, auth=request.auth)

    form = EnvironmentSelectionForm(
        request.POST or None,
        groups=run.environmentgroups_prefetch,
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
