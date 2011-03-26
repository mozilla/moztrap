from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ..core import sort, pagination
from ..products.models import ProductList
from ..testexecution.models import TestCycleList
from ..users.decorators import login_redirect

from .forms import TestCycleForm


def home(request):
    return redirect("manage_testcycles")



@login_redirect
def testcycles(request):
    pagesize, pagenum = pagination.from_request(request)
    cycles = TestCycleList.ours(auth=request.auth).sort(
        *sort.from_request(request)).paginate(
        pagesize, pagenum)
    paginator = pagination.Paginator(cycles.totalResults, pagesize, pagenum)
    return TemplateResponse(
        request,
        "manage/testcycle/cycles.html",
        {"cycles": cycles, "pager": paginator}
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
