from django.shortcuts import redirect
from django.template.response import TemplateResponse

from tcmui.testexecution.models import TestCycleList
from tcmui.users.decorators import login_redirect



def home(request):
    return redirect("manage_testcycles")



@login_redirect
def testcycles(request):
    cycles = TestCycleList.ours(auth=request.auth)
    return TemplateResponse(
        request,
        "manage/testcycle/cycles.html",
        {"cycles": cycles}
        )
