from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ..testexecution.models import TestCycleList, TestRunList
from ..core import decorators as dec
from ..users.decorators import login_redirect



def home(request):
    return redirect("results_testcycles")



@login_redirect
@dec.filter("cycles")
@dec.paginate("cycles")
@dec.sort("cycles")
def testcycles(request):
    cycles = TestCycleList.ours(auth=request.auth)
    return TemplateResponse(
        request, "results/testcycle/cycles.html", {"cycles": cycles})



@login_redirect
@dec.filter("runs")
@dec.paginate("runs")
@dec.sort("runs")
def testruns(request):
    runs = TestRunList.ours(auth=request.auth)
    return TemplateResponse(
        request, "results/testrun/runs.html", {"runs": runs})
