# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-12 Mozilla
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
"""
Views for test execution.

"""
import json

from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

from django.contrib import messages
from django.contrib.auth.decorators import permission_required

from ... import model

from ..lists import decorators as lists
from ..utils.ajax import ajax

from .finders import RunTestsFinder
from .forms import EnvironmentSelectionForm




@permission_required("execution.execute")
@lists.finder(RunTestsFinder)
def select(request):
    """Select an active test run to execute tests from."""
    return TemplateResponse(
        request,
        "runtests/select.html",
        {}
        )



@permission_required("execution.execute")
@ajax("runtests/_environment_form.html")
def set_environment(request, run_id):
    """Select valid environment for given run and save it in session."""
    run = get_object_or_404(model.Run, pk=run_id)

    try:
        current = int(request.GET.get("environment", None))
    except (TypeError, ValueError):
        current = None

    form_kwargs = {
        "current": current,
        "environments": run.environments.all()
        }

    if request.method == "POST":
        form = EnvironmentSelectionForm(
            request.POST,
            **form_kwargs)

        if form.is_valid():
            envid = form.save()
            return redirect("runtests_run", run_id=run_id, env_id=envid)
    else:
        form = EnvironmentSelectionForm(**form_kwargs)

    return TemplateResponse(
        request,
        "runtests/environment.html",
        {
            "form": form,
            "run": run,
            "environments_json": json.dumps(form.elementids_by_envid.values())
            }
        )



@permission_required("execution.execute")
@lists.finder(RunTestsFinder)
@lists.sort("runcaseversions")
def run(request, run_id, env_id):
    run = get_object_or_404(model.Run.objects.select_related(), pk=run_id)

    if not run.status == model.Run.STATUS.active:
        messages.info(
            request,
            "That test run is currently not open for testing. "
            "Please select a different test run.")
        return redirect("runtests")

    try:
        environment = run.environments.get(pk=env_id)
    except model.Environment.DoesNotExist:
        return redirect("runtests_environment", run_id=run_id)

    return TemplateResponse(
        request,
        "runtests/run.html",
        {
            "environment": environment,
            "product": run.productversion.product,
            "productversion": run.productversion,
            "run": run,
            "runcaseversions": run.runcaseversions.select_related(
                "caseversion"),
            "finder": {
                # finder decorator populates top column (products), we
                # prepopulate the other two columns
                "productversions": model.ProductVersion.objects.filter(
                    product=run.productversion.product),
                "runs": model.Run.objects.order_by("name").filter(
                    productversion=run.productversion,
                    status=model.Run.STATUS.active),
                },
            }
        )
