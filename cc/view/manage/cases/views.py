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
Manage views for cases.

"""
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

from cc import model

from cc.view.filters import CaseVersionFilterSet
from cc.view.lists import decorators as lists
from cc.view.utils.ajax import ajax

from ..finders import ManageFinder

from . import forms



@never_cache
@login_required
@lists.actions(
    model.Case,
    ["delete"],
    permission="library.manage_cases",
    fall_through=True)
@lists.actions(
    model.CaseVersion,
    ["clone", "activate", "deactivate"],
    permission="library.manage_cases")
@lists.finder(ManageFinder)
@lists.filter("caseversions", filterset_class=CaseVersionFilterSet)
@lists.sort("caseversions")
@ajax("manage/case/list/_cases_list.html")
def cases_list(request):
    """List caseversions."""
    return TemplateResponse(
        request,
        "manage/case/cases.html",
        {
            "caseversions": model.CaseVersion.objects.select_related("case"),
            }
        )



@never_cache
@login_required
def case_details(request, caseversion_id):
    """Get details snippet for a caseversion."""
    caseversion = get_object_or_404(model.CaseVersion, pk=caseversion_id)
    return TemplateResponse(
        request,
        "manage/case/list/_case_details.html",
        {
            "caseversion": caseversion
            }
        )



@never_cache
@permission_required("library.create_cases")
def case_add(request):
    """Add a single case."""
    if request.method == "POST":
        form = forms.AddCaseForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            case = form.save()
            messages.success(
                request, "Test case '{0}' added.".format(
                    case.versions.all()[0].name)
                )
            return redirect("manage_cases")
    else:
        form = forms.AddCaseForm(user=request.user, initial=request.GET)
    return TemplateResponse(
        request,
        "manage/case/add_case.html",
        {
            "form": form
            }
        )



@never_cache
@permission_required("library.create_cases")
def case_add_bulk(request):
    """Add cases in bulk."""
    if request.method == "POST":
        form = forms.AddBulkCaseForm(
            request.POST, request.FILES, user=request.user)
        if form.is_valid():
            cases = form.save()
            messages.success(
                request, "Added {0} test case{1}.".format(
                    len(cases), "" if len(cases) == 1 else "s")
                )
            return redirect("manage_cases")
    else:
        form = forms.AddBulkCaseForm(user=request.user)
    return TemplateResponse(
        request,
        "manage/case/add_case_bulk.html",
        {
            "form": form
            }
        )



@never_cache
@permission_required("library.manage_cases")
def caseversion_edit(request, caseversion_id):
    """Edit a caseversion."""
    caseversion = get_object_or_404(model.CaseVersion, pk=caseversion_id)
    if request.method == "POST":
        form = forms.EditCaseVersionForm(
            request.POST,
            request.FILES,
            instance=caseversion,
            user=request.user)
        cv = form.save_if_valid()
        if cv is not None:
            messages.success(request, "Saved '{0}'.".format(cv.name))
            return redirect("manage_cases")
    else:
        form = forms.EditCaseVersionForm(
            instance=caseversion, user=request.user)
    return TemplateResponse(
        request,
        "manage/case/edit_case.html",
        {
            "form": form,
            "caseversion": caseversion,
            }
        )


@require_POST
@permission_required("library.manage_cases")
def caseversion_clone(request, caseversion_id):
    """Clone caseversion for productversion, and redirect to edit new clone."""
    try:
        productversion = model.ProductVersion.objects.get(
            pk=request.POST["productversion"])
    except (model.ProductVersion.DoesNotExist, KeyError):
        return redirect(
            "manage_caseversion_edit", caseversion_id=caseversion_id)

    caseversion = get_object_or_404(model.CaseVersion, pk=caseversion_id)

    # if it exists already, just redirect to edit it
    try:
        target = model.CaseVersion.objects.get(
            case=caseversion.case, productversion=productversion)
    except model.CaseVersion.DoesNotExist:
        target = caseversion.clone(
            overrides={
                "productversion": productversion,
                "name": caseversion.name
                }
            )
        messages.success(
            request,
            "Created new version of '{0}' for {1}.".format(
                caseversion.name, productversion)
            )

    return redirect("manage_caseversion_edit", caseversion_id=target.id)
