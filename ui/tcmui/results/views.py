from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ..testexecution.models import TestCycleList



def home(request):
    return redirect("results_testcycles")



def testcycles(request):
    cycles = TestCycleList.ours(auth=request.auth)
    return TemplateResponse(
        request, "results/testcycle/cycles.html", {"cycles": cycles})
