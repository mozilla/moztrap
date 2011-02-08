from django.template.response import TemplateResponse

from ..core import sort
from ..products.models import Product
from ..static import testcyclestatus, testrunstatus
from ..users.decorators import login_required

from .models import TestCycle, TestCycleList, TestRun, TestRunList



@login_required
def cycles(request, product_id):
    product = Product.get("products/%s" % product_id, auth=request.auth)

    cycles = TestCycleList.get(auth=request.auth).filter(
        productId=product_id, testCycleStatusId=testcyclestatus.ACTIVE).sort(
        *sort.from_request(request))

    return TemplateResponse(
        request, "test/cycles.html", {"product": product, "cycles": cycles})



@login_required
def testruns(request, cycle_id):
    cycle = TestCycle.get("testcycles/%s" % cycle_id, auth=request.auth)

    testruns = TestRunList.get(auth=request.auth).filter(
        testCycleId=cycle_id,
        testRunStatusId=testrunstatus.ACTIVE,
# @@@        selfAssignAllowed=True,
        ).sort(
        *sort.from_request(request))

    return TemplateResponse(
        request,
        "test/testruns.html",
        {"product": cycle.product,
         "cycle": cycle,
         "testruns": testruns
         })



@login_required
def runtests(request, testrun_id):
    testrun = TestRun.get("testruns/%s" % testrun_id, auth=request.auth)
    cycle = testrun.testCycle
    product = cycle.product

    return TemplateResponse(
        request,
        "test/run.html",
        {"product": product,
         "cycle": cycle,
         "testrun": testrun
         })
