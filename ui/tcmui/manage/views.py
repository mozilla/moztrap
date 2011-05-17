from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ..core import sort
from ..products.models import ProductList
from ..testexecution.models import TestCycleList, TestRunList
from ..testcases.models import TestSuiteList, TestCaseVersionList
from ..users.decorators import login_redirect
from ..users.models import UserList

from ..core import decorators as dec
from .forms import TestCycleForm, TestRunForm, TestSuiteForm, TestCaseForm



def home(request):
    return redirect("manage_testcycles")



@login_redirect
@dec.actions(TestCycleList, ["activate", "deactivate", "delete", "clone"])
@dec.filter("cycles")
@dec.paginate("cycles")
@dec.sort("cycles")
def testcycles(request):
    return TemplateResponse(
        request,
        "manage/testcycle/cycles.html",
        {"cycles": TestCycleList.ours(auth=request.auth)}
        )



@login_redirect
def add_testcycle(request):
    form = TestCycleForm(
        request.POST or None,
        product_choices=ProductList.ours(auth=request.auth),
        team_choices=UserList.ours(auth=request.auth),
        auth=request.auth)
    if request.method == "POST" and form.is_valid():
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



@login_redirect
@dec.actions(TestRunList, ["delete"], fall_through=True)
def edit_testcycle(request, cycle_id):
    cycle = TestCycleList.get_by_id(cycle_id, auth=request.auth)
    form = TestCycleForm(
        request.POST or None,
        instance=cycle,
        product_choices=[cycle.product],
        team_choices=UserList.ours(auth=request.auth),
        auth=request.auth)
    if request.method == "POST" and form.is_valid():
        cycle = form.save()
        messages.success(
            request,
            "The test cycle '%s' has been saved."  % cycle.name)
        return redirect("manage_testcycles")

    testruns = TestRunList.ours(auth=request.auth).filter(
        testCycle=cycle.id).sort(
        *sort.from_request(request))

    return TemplateResponse(
        request,
        "manage/testcycle/edit_cycle.html",
        {
            "form": form,
            "cycle": cycle,
            "testruns": testruns,
            }
        )



@login_redirect
@dec.actions(TestRunList, ["activate", "deactivate", "delete", "clone"])
@dec.filter("runs")
@dec.paginate("runs")
@dec.sort("runs")
def testruns(request):
    return TemplateResponse(
        request,
        "manage/testrun/runs.html",
        {"runs": TestRunList.ours(auth=request.auth)}
        )



@login_redirect
def add_testrun(request):
    tcid = request.GET.get("cycle")
    suites = TestSuiteList.ours(auth=request.auth)
    if tcid is not None:
        cycle = TestCycleList.get_by_id(tcid, auth=request.auth)
        suites = suites.filter(product=cycle.product.id)
    form = TestRunForm(
        request.POST or None,
        initial=tcid and {"test_cycle": tcid} or {},
        test_cycle_choices=TestCycleList.ours(auth=request.auth),
        # @@@ should be narrowed by company, and dynamically by product
        suites_choices=suites,
        team_choices=UserList.ours(auth=request.auth),
        auth=request.auth)
    if request.method == "POST" and form.is_valid():
        run = form.save()
        messages.success(
            request,
            "The test run '%s' has been created."  % run.name)
        return redirect("manage_testruns")
    return TemplateResponse(
        request,
        "manage/testrun/add_run.html",
        {"form": form}
        )



@login_redirect
def edit_testrun(request, run_id):
    run = TestRunList.get_by_id(run_id, auth=request.auth)
    form = TestRunForm(
        request.POST or None,
        instance=run,
        test_cycle_choices=[run.testCycle],
        suites_choices=TestSuiteList.ours(auth=request.auth).filter(
            product=run.testCycle.product.id),
        team_choices=UserList.ours(auth=request.auth),
        auth=request.auth)
    if request.method == "POST" and form.is_valid():
        run = form.save()
        messages.success(
            request,
            "The test run '%s' has been saved."  % run.name)
        return redirect("manage_testruns")

    return TemplateResponse(
        request,
        "manage/testrun/edit_run.html",
        {
            "form": form,
            "run": run,
            }
        )



@login_redirect
@dec.actions(TestSuiteList, ["activate", "deactivate", "delete", "clone"])
@dec.filter("suites")
@dec.paginate("suites")
@dec.sort("suites")
def testsuites(request):
    return TemplateResponse(
        request,
        "manage/testsuite/suites.html",
        {"suites": TestSuiteList.ours(auth=request.auth)}
        )



@login_redirect
def add_testsuite(request):
    form = TestSuiteForm(
        request.POST or None,
        product_choices=ProductList.ours(auth=request.auth),
        # @@@ should be narrowed by company, and dynamically by product
        cases_choices=TestCaseVersionList.latest(auth=request.auth),
        auth=request.auth)
    if request.method == "POST" and form.is_valid():
        suite = form.save()
        messages.success(
            request,
            "The test suite '%s' has been created."  % suite.name)
        return redirect("manage_testsuites")
    return TemplateResponse(
        request,
        "manage/testsuite/add_suite.html",
        {"form": form}
        )



@login_redirect
def edit_testsuite(request, suite_id):
    suite = TestSuiteList.get_by_id(suite_id, auth=request.auth)
    form = TestSuiteForm(
        request.POST or None,
        instance=suite,
        product_choices=[suite.product],
        cases_choices=TestCaseVersionList.latest(auth=request.auth).filter(
            product=suite.product.id),
        auth=request.auth)
    if request.method == "POST" and form.is_valid():
        suite = form.save()
        messages.success(
            request,
            "The test suite '%s' has been saved."  % suite.name)
        return redirect("manage_testsuites")

    return TemplateResponse(
        request,
        "manage/testsuite/edit_suite.html",
        {
            "form": form,
            "suite": suite,
            }
        )



@login_redirect
@dec.actions(
    TestCaseVersionList,
    ["approve", "reject", "activate", "deactivate", "delete"])
@dec.filter("cases")
@dec.paginate("cases")
@dec.sort("cases")
def testcases(request):
    return TemplateResponse(
        request,
        "manage/testcase/cases.html",
        {"cases": TestCaseVersionList.ours(
                url="testcases/latestversions", auth=request.auth)}
        )



@login_redirect
def add_testcase(request):
    form = TestCaseForm(
        request.POST or None,
        product_choices=ProductList.ours(auth=request.auth),
        auth=request.auth)
    if request.method == "POST":
        if form.is_valid():
            testcase = form.save()
            messages.success(
                request,
                "The test case '%s' has been created."  % testcase.name)
            return redirect("manage_testcases")

    return TemplateResponse(
        request,
        "manage/testcase/add_case.html",
        {"form": form })



@login_redirect
def edit_testcase(request, case_id):
    case = TestCaseVersionList.get_by_id(case_id, auth=request.auth)
    form = TestCaseForm(
        request.POST or None,
        instance=case,
        product_choices=[case.product],
        auth=request.auth)
    if request.method == "POST" and form.is_valid():
        case = form.save()
        messages.success(
            request,
            "The test case '%s' has been saved."  % case.name)
        return redirect("manage_testcases")

    return TemplateResponse(
        request,
        "manage/testcase/edit_case.html",
        {
            "form": form,
            "case": case,
            }
        )
