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
from itertools import islice, dropwhile

from django.shortcuts import render

from .apilog import get_records, formatter



def apilog(request):
    records = get_records()

    template_name = "debug/apilog/viewer.html"

    if request.is_ajax():
        template_name = "debug/apilog/_records.html"
        last = int(request.GET.get("last", 0))
        if last:
            records = dropwhile(lambda (i, r): i >= last, records)

    records = ((i, formatter.format(r)) for i, r in records)

    return render(
        request,
        template_name,
        {
            "records": islice(records, 20)
            }
        )
