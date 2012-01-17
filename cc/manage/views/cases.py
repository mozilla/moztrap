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
Manage views.

"""
from django.template.response import TemplateResponse

from django.contrib.auth.decorators import login_required

from ...core.sort import sort
from ...library.models import CaseVersion



@login_required
@sort("caseversions")
def cases(request):
    return TemplateResponse(
        request,
        "manage/product/testcase/cases.html",
        {
            "caseversions": CaseVersion.objects.all(), # @@@ just latest
            }
        )
