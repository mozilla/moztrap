# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-2012 Mozilla
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
Manage views for runs.

"""
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

from cc import model

from cc.view.filters import RunFilterSet
from cc.view.lists import decorators as lists
from cc.view.utils.ajax import ajax

from ..finders import ManageFinder

from . import forms



@never_cache
@login_required
@lists.actions(
    model.Run,
    ["delete", "clone", "activate", "deactivate"],
    permission="execution.manage_runs")
@lists.finder(ManageFinder)
@lists.filter("runs", filterset_class=RunFilterSet)
@lists.sort("runs")
@ajax("manage/run/list/_runs_list.html")
def runs_list(request):
    """List runs."""
    return TemplateResponse(
        request,
        "manage/run/runs.html",
        {
            "runs": model.Run.objects.select_related(),
            }
        )



@never_cache
@login_required
def run_details(request, run_id):
    """Get details snippet for a run."""
    run = get_object_or_404(
        model.Run, pk=run_id)
    return TemplateResponse(
        request,
        "manage/run/list/_run_details.html",
        {
            "run": run
            }
        )



@never_cache
@permission_required("execution.manage_runs")
def run_add(request):
    """Add a run."""
    if request.method == "POST":
        form = forms.AddRunForm(request.POST, user=request.user)
        run = form.save_if_valid()
        if run is not None:
            messages.success(
                request, "Run '{0}' added.".format(
                    run.name)
                )
            return redirect("manage_runs")
    else:
        form = forms.AddRunForm(user=request.user)
    return TemplateResponse(
        request,
        "manage/run/add_run.html",
        {
            "form": form
            }
        )



@never_cache
@permission_required("execution.manage_runs")
def run_edit(request, run_id):
    """Edit a run."""
    run = get_object_or_404(
        model.Run, pk=run_id)
    if request.method == "POST":
        form = forms.EditRunForm(
            request.POST, instance=run, user=request.user)
        saved_run = form.save_if_valid()
        if saved_run is not None:
            messages.success(request, "Saved '{0}'.".format(saved_run.name))
            return redirect("manage_runs")
    else:
        form = forms.EditRunForm(
            instance=run, user=request.user)
    return TemplateResponse(
        request,
        "manage/run/edit_run.html",
        {
            "form": form,
            "run": run,
            }
        )
