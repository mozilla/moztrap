from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ..core import sort
from ..products.models import ProductList
from ..testexecution.models import TestCycleList
from ..users.decorators import login_redirect

from .forms import TestCycleForm


def home(request):
    return redirect("manage_testcycles")



@login_redirect
def testcycles(request):
    cycles = TestCycleList.ours(auth=request.auth).sort(
        *sort.from_request(request))
    return TemplateResponse(
        request,
        "manage/testcycle/cycles.html",
        {"cycles": cycles}
        )



@login_redirect
def add_testcycle(request):
    form = TestCycleForm(
        request.POST or None,
        products=ProductList.ours(auth=request.auth))
    if request.method == "POST":
        if form.is_valid():
            cycle = form.save()
            messages.success(
                request,
                "The test cycle '%s' has been created."  % cycle.name)
            return redirect("manage_testcycles")
    return TemplateResponse(
        request,
        "manage/testcycle/add_cycle.html",
        {"form": form}
        )
