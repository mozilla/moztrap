from django.core.urlresolvers import reverse
from django.template import Library

from ...products.models import Product
from ...testcases.models import TestSuite
from ...testexecution.models import TestCycle, TestRun



register = Library()



URLS = {
    "runtests": {
        Product: "runtests_finder_cycles",
        TestCycle: "runtests_finder_runs",
        TestRun: "runtests_finder_environments",
        },
    "manage": {
        Product: "manage_finder_cycles",
        TestCycle: "manage_finder_runs",
        TestRun: "manage_finder_suites",
        }
    }



@register.filter
def finder_sub_url(obj, finder_type):
    try:
        url_pattern = URLS[finder_type][obj.__class__]
    except KeyError:
        return ""
    return reverse(url_pattern, kwargs={"parent_id": obj.id})



SUB_NAMES = {
    Product: "cycles",
    TestCycle: "runs",
    TestRun: "suites",
    TestSuite: "cases",
    }



@register.filter
def finder_sub_name(obj):
    try:
        return SUB_NAMES[obj.__class__]
    except KeyError:
        return ""



GOTO_URLS = {
    "manage": {
        Product: ("manage_testcycles", "product"),
        TestCycle: ("manage_testruns", "testCycle"),
        TestRun: ("manage_testsuites", "run"),
        TestSuite: ("manage_testcases", "suite"),
        },
    }


@register.filter
def finder_goto_url(obj, finder_type):
    try:
        url_pattern, filter_name = GOTO_URLS[finder_type][obj.__class__]
    except KeyError:
        return ""
    return reverse(url_pattern) + "?%s=%s" % (filter_name, obj.id)
