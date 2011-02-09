from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template.response import TemplateResponse

from ..core import sort
from ..environments.util import set_environment_url
from ..products.models import Product
from ..static import testcyclestatus, testrunstatus
from ..users.decorators import login_required

from .models import TestCycle, TestCycleList, TestRun, TestRunList, TestResult



@login_required
def cycles(request, product_id):
    product = Product.get("products/%s" % product_id, auth=request.auth)

    cycles = TestCycleList.get(auth=request.auth).filter(
        productId=product_id, testCycleStatusId=testcyclestatus.ACTIVE).sort(
        *sort.from_request(request))

    return TemplateResponse(
        request,
        "test/cycles.html",
        {"product": product,
         "cycles": cycles,
         "environmentgroups": product.environmentgroups,
         })



@login_required
def testruns(request, cycle_id):
    cycle = TestCycle.get("testcycles/%s" % cycle_id, auth=request.auth)

    testruns = TestRunList.get(auth=request.auth).filter(
        testCycleId=cycle_id,
        testRunStatusId=testrunstatus.ACTIVE,
        selfAssignAllowed=True,
        ).sort(
        *sort.from_request(request))

    return TemplateResponse(
        request,
        "test/testruns.html",
        {"product": cycle.product,
         "cycle": cycle,
         "testruns": testruns,
         "environmentgroups": cycle.environmentgroups,
         })



@login_required
def runtests(request, testrun_id):
    testrun = TestRun.get("testruns/%s" % testrun_id, auth=request.auth)

    if not testrun.environmentgroups.match(request.environments):
        return HttpResponseRedirect("%s&next=%s" % (
            set_environment_url(testrun.environmentgroups),
            request.path
            ))

    cycle = testrun.testCycle
    product = cycle.product

    return TemplateResponse(
        request,
        "test/run.html",
        {"product": product,
         "cycle": cycle,
         "testrun": testrun,
         "environmentgroups": testrun.environmentgroups,
         })



ACTIONS = {
    "start": [],
    "finishsucceed": [],
    "finishinvalidate": ["comment"],
    "finishfail": ["comment", "failedStepNumber", "actualResult"],
    }


@login_required
@require_POST
def result(request, result_id):
    result = TestResult.get(
        "testruns/results/%s" % result_id,
        auth=request.auth)

    action = request.POST.get("action", None)
    try:
        argnames = ACTIONS[action]
    except KeyError:
        return HttpResponseBadRequest(
            "%s is not a valid result action." % action)

    kwargs = {"auth": request.auth}

    for argname in argnames:
        try:
            kwargs[argname] = request.POST[argname]
        except KeyError:
            return HttpResponseBadRequest(
                "Required parameter %s missing." % argname)

    getattr(result, action)(**kwargs)

    return render_to_response(
        "test/_run_case_status.html",
        {"case": result.testCase,
         "caseversion": result.testCaseVersion,
         "result": result,
         "open": True,
         })
