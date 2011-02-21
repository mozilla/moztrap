from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ..products.models import ProductList
from ..users.decorators import login_required

from .forms import TestCaseForm



@login_required
def add_testcase(request):
    form = TestCaseForm(
        request.POST or None,
        products=ProductList.ours(auth=request.auth))
    if request.method == "POST":
        if form.is_valid():
            testcase = form.save()
            messages.success(
                request,
                "The test case '%s' has been created."  % testcase.name)
            return redirect("products")

    return TemplateResponse(
        request,
        "manage/testcase/add_case.html",
        {"form": form })

