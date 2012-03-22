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
Results views for runcaseversions.

"""
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from cc.view.utils.auth import login_maybe_required

from cc import model

from cc.view.filters import ResultFilterSet
from cc.view.lists import decorators as lists
from cc.view.utils.ajax import ajax

from ..finders import ResultsFinder



@login_maybe_required
@lists.finder(ResultsFinder)
@lists.filter("results", filterset_class=ResultFilterSet)
@lists.sort("results")
@ajax("results/result/list/_results_list.html")
def results_list(request, rcv_id):
    """List results for a given runcaseversion."""
    rcv = get_object_or_404(model.RunCaseVersion, pk=rcv_id)
    return TemplateResponse(
        request,
        "results/result/results.html",
        {
            "results": model.Result.objects.filter(
                runcaseversion=rcv).select_related(),
            "runcaseversion": rcv,
            }
        )
