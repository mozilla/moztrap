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
from django import template
from django.template.loader import render_to_string

from classytags.core import Tag, Options
from classytags.arguments import Argument

from ..models import TestCaseAssignmentList

register = template.Library()



class RunCase(Tag):
    name = "run_case"
    options = Options(
        Argument("includedtestcase"),
        Argument("user"),
        Argument("environments")
        )


    def render_tag(self, context, includedtestcase, user, environments):
        assignments = TestCaseAssignmentList.get(auth=user.auth).filter(
            testCaseVersion=includedtestcase.testCaseVersion.id,
            testRun=includedtestcase.testRun.id,
            tester=user.id)
        if len(assignments):
            assignment = assignments[0]
        else:
            assignment = includedtestcase.assign(user, auth=user.auth)

        # @@@ need a better way to filter results by environment group
        result = None
        for res in assignment.results:
            if res.environments.match(environments):
                result = res
                break

        if result is None:
            # @@@ no environment match - should never happen.
            return u""

        return render_to_string(
            "runtests/_run_case.html",
            {"case": assignment.testCase,
             "caseversion": assignment.testCaseVersion,
             "result": result,
             "open": False,
             })

register.tag(RunCase)
