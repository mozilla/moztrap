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
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.middleware.csrf import get_token

from ... import model

from ..lists import decorators as lists

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
def finder_environments(request, run_id):
    """Ajax-load environment-selection form."""
    run = get_object_or_404(model.Run, pk=run_id)

    return TemplateResponse(
        request,
        "runtests/_environment_form.html",
        {
            "testrun": run,
            "form": EnvironmentSelectionForm
            }
        )



@permission_required("execution.execute")
def set_environment(request, run_id):
    """Select valid environment for given run and save it in session."""
    run = get_object_or_404(model.Run, pk=run_id)
    current = request.session.get("environments", None)

    if request.method == "POST":
        form = EnvironmentSelectionForm(
            request.POST,
            current=current)

        if form.is_valid():
            request.session["environments"] = form.save()
            return redirect("runtests_run", run_id=run_id)
    else:
        form = EnvironmentSelectionForm(current=current)

    return TemplateResponse(
        request,
        "runtests/environment.html",
        {
            "form": form,
            "run": run,
            }
        )



@permission_required("execution.execute")
@lists.finder(RunTestsFinder)
def run(request, run_id):
    # force the CSRF cookie to be set
    # @@@ replace with ensure_csrf_cookie decorator in Django 1.4
    get_token(request)

    run = get_object_or_404(model.Run, pk=run_id)

    if not run.status == model.Run.STATUS.active:
        messages.info(
            request,
            "That test run is currently not open for testing. "
            "Please select a different test run.")
        return redirect("runtests")

    # @@@ if not run.environment.match(request.environments):
    # @@@    return redirect("runtests_environment", testrun_id=testrun_id)

    productversion = run.productversion
    product = productversion.product

    # for prepopulating finder
    productversions = model.ProductVersion.objects.filter(product=product)
    runs = model.Run.objects.order_by("name").filter(
        productversion=productversion, status=model.Run.STATUS.active)

    return TemplateResponse(
        request,
        "runtests/run.html",
        {
            "product": run.productversion.product,
            "productversion": run.productversion,
            "run": run,
            "cases": [], # @@@ runcaseversions in this run
            "finder": {
                # finder decorator populates top column, products
                "productversions": productversions,
                "runs": runs,
                },
            }
        )
