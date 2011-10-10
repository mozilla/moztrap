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
from django.core.urlresolvers import reverse

from ..core.finder import Finder, Column
from ..products.models import ProductList
from ..static.status import TestRunStatus, TestCycleStatus
from ..testexecution.models import TestCycleList, TestRunList



class RunTestsFinder(Finder):
    template_base = "runtests/finder"

    columns = [
        Column("products", "_products.html", ProductList, "product"),
        Column("cycles", "_cycles.html", TestCycleList, "testCycle",
               status=TestCycleStatus.ACTIVE),
        Column("runs", "_runs.html", TestRunList, "run",
               status=TestRunStatus.ACTIVE),
        ]


    def child_query_url(self, obj):
        if isinstance(obj, TestRunList.entryclass):
            return reverse(
                "runtests_finder_environments", kwargs={"run_id": obj.id}
                )
        return super(RunTestsFinder, self).child_query_url(obj)
