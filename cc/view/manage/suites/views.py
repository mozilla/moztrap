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
Manage views for suites.

"""
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

from cc import model

from cc.view.lists import decorators as lists
from cc.view.utils.ajax import ajax

from ..finders import ManageFinder

from .filters import SuiteFilterSet
from . import forms



@login_required
@lists.actions(
    model.Suite,
    ["delete", "clone", "activate", "deactivate"],
    permission="library.manage_suites")
@lists.finder(ManageFinder)
@lists.filter("suites", filterset_class=SuiteFilterSet)
@lists.sort("suites")
@ajax("manage/suite/list/_suites_list.html")
def suites_list(request):
    """List suites."""
    return TemplateResponse(
        request,
        "manage/suite/suites.html",
        {
            "suites": model.Suite.objects.select_related().annotate(
                case_count=Count("cases")),
            }
        )



@login_required
def suite_details(request, suite_id):
    """Get details snippet for a suite."""
    suite = get_object_or_404(
        model.Suite, pk=suite_id)
    return TemplateResponse(
        request,
        "manage/suite/list/_suite_details.html",
        {
            "suite": suite
            }
        )



@permission_required("library.manage_suites")
def suite_add(request):
    """Add a suite."""
    if request.method == "POST":
        form = forms.AddSuiteForm(request.POST, user=request.user)
        if form.is_valid():
            suite = form.save()
            messages.success(
                request, "Suite '{0}' added.".format(
                    suite.name)
                )
            return redirect("manage_suites")
    else:
        form = forms.AddSuiteForm(user=request.user)
    return TemplateResponse(
        request,
        "manage/suite/add_suite.html",
        {
            "form": form
            }
        )



@permission_required("library.manage_suites")
def suite_edit(request, suite_id):
    """Edit a suite."""
    suite = get_object_or_404(
        model.Suite, pk=suite_id)
    if request.method == "POST":
        form = forms.EditSuiteForm(
            request.POST, instance=suite, user=request.user)
        if form.is_valid():
            cv = form.save()
            messages.success(request, "Saved '{0}'.".format(cv.name))
            return redirect("manage_suites")
    else:
        form = forms.EditSuiteForm(
            instance=suite, user=request.user)
    return TemplateResponse(
        request,
        "manage/suite/edit_suite.html",
        {
            "form": form,
            "suite": suite,
            }
        )
