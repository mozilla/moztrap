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

from django.contrib.auth.decorators import login_required, permission_required

from ....model.library.models import CaseVersion, Case

from ... import lists
from ...lists.filters import ChoicesFilter
from ...utils.ajax import ajax

from .forms import AddCaseForm, EditCaseForm, AddBulkCaseForm



@login_required
@lists.actions(Case, ["clone", "delete"], fall_through=True)
@lists.actions(CaseVersion, ["activate", "deactivate"])
@lists.filter("caseversions", ChoicesFilter("status", choices=[("draft", "draft"), ("active", "active")]))
@ajax("manage/product/testcase/list/_cases_list.html")
@lists.sort("caseversions")
def cases_list(request):
    return TemplateResponse(
        request,
        "manage/product/testcase/cases.html",
        {
            "caseversions": CaseVersion.objects.filter(
                latest=True).select_related("case"),
            }
        )



@login_required
def case_details(request, caseversion_id):
    caseversion = get_object_or_404(CaseVersion, pk=caseversion_id)
    return TemplateResponse(
        request,
        "manage/product/testcase/list/_case_details.html",
        {
            "caseversion": caseversion
            }
        )



@permission_required("library.create_cases")
def case_add(request):
    if request.method == "POST":
        form = AddCaseForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("manage_cases")
    else:
        form = AddCaseForm(user=request.user)
    return TemplateResponse(
        request,
        "manage/product/testcase/add_case.html",
        {
            "form": form
            }
        )



@permission_required("library.create_cases")
def case_add_bulk(request):
    if request.method == "POST":
        form = AddBulkCaseForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("manage_cases")
    else:
        form = AddBulkCaseForm(user=request.user)
    return TemplateResponse(
        request,
        "manage/product/testcase/add_case_bulk.html",
        {
            "form": form
            }
        )



@permission_required("library.manage_cases")
def case_edit(request, caseversion_id):
    caseversion = get_object_or_404(CaseVersion, pk=caseversion_id)
    if request.method == "POST":
        form = EditCaseForm(
            request.POST,
            request.FILES,
            instance=caseversion,
            user=request.user)
        if form.is_valid():
            form.save()
            return redirect("manage_cases")
    else:
        form = EditCaseForm(instance=caseversion, user=request.user)
    return TemplateResponse(
        request,
        "manage/product/testcase/edit_case.html",
        {
            "form": form
            }
        )
