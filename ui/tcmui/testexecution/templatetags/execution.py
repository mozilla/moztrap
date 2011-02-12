from django import template
from django.template.loader import render_to_string

from classytags.core import Tag, Options
from classytags.arguments import Argument

from ..models import TestCaseAssignmentList
from .. import testresultstatus

register = template.Library()



class RunCase(Tag):
    name = "run_case"
    options = Options(
        Argument("includedtestcase"),
        Argument("user"),
        Argument("environments")
        )


    def render_tag(self, context, includedtestcase, user, environments):
        # @@@ once double-assignment raises error, maybe just try to assign
        #     and catch that error
        assignments = TestCaseAssignmentList.get(auth=user.auth).filter(
            testCaseVersionId=includedtestcase.testCaseVersion.id,
            testRunId=includedtestcase.testRun.id,
            testerId=user.id)
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


STATUS_CLASSES = {
    testresultstatus.FAILED: u"failed",
    testresultstatus.PASSED: u"passed",
    testresultstatus.STARTED: u"started",
    testresultstatus.INVALIDATED: u"invalidated",
    }

@register.filter
def status_class(result):
    return STATUS_CLASSES.get(int(result.testRunResultStatus.id), u"")
