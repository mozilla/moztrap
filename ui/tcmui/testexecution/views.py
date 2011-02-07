from django.http import Http404
from django.template.response import TemplateResponse

from ..core import sort
from ..products.models import Product
from ..static import testcyclestatus, testrunstatus
from ..users.decorators import login_required

from .models import TestCycle, TestCycleList, TestRunList



@login_required
def cycles(request, product_id):
    product = Product.get("products/%s" % product_id, auth=request.auth)

    cycles = TestCycleList.get(auth=request.auth).filter(
        productId=product_id, testCycleStatusId=testcyclestatus.ACTIVE).sort(
        *sort.from_request(request))

    return TemplateResponse(
        request, "test/cycles.html", {"product": product, "cycles": cycles})



@login_required
def testruns(request, product_id, cycle_id):
    cycle = TestCycle.get("testcycles/%s" % cycle_id, auth=request.auth)
    product = cycle.product
    if int(product.id) != int(product_id):
        raise Http404

    testruns = TestRunList.get(auth=request.auth).filter(
        testCycleId=cycle_id, testRunStatusId=testrunstatus.ACTIVE).sort(
        *sort.from_request(request))

    return TemplateResponse(
        request,
        "test/testruns.html",
        {"product": cycle.product,
         "cycle": cycle,
         "testruns": testruns
         })
