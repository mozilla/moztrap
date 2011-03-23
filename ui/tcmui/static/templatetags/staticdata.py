from django import template

from .. import testresultstatus


register = template.Library()



STATUS_CLASSES = {
    testresultstatus.FAILED: u"failed",
    testresultstatus.PASSED: u"passed",
    testresultstatus.STARTED: u"started",
    testresultstatus.INVALIDATED: u"invalidated",
    }



@register.filter
def status_class(result):
    return STATUS_CLASSES.get(int(result.testRunResultStatus.id), u"")
