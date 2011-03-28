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
            "test/_run_case.html",
            {"case": assignment.testCase,
             "caseversion": assignment.testCaseVersion,
             "result": result,
             "open": False,
             })

register.tag(RunCase)
