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
"""
Views for test execution.

"""
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django.contrib.auth.decorators import permission_required

from ... import model

from ..lists import decorators as lists

from .finders import RunTestsFinder




@permission_required("execution.execute")
@lists.finder(RunTestsFinder)
def select(request):
    return TemplateResponse(
        request,
        "runtests/select.html",
        {}
        )



@permission_required("execution.execute")
def finder_environments(request, run_id):
    run = get_object_or_404(model.Run, pk=run_id)

    return TemplateResponse(
        request,
        "runtests/_environment_form.html",
        {
            "testrun": run,
            # @@@ form: EnvironmentSelectionForm
            }
        )
