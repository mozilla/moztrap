from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache

from ..core import decorators as dec
from ..core.conf import conf
from ..core.filters import KeywordFilter
from ..products.filters import ProductFieldFilter
from ..products.models import ProductList
from ..static import filters as status_filters
from ..static.status import TestCaseStatus, TestSuiteStatus
from ..testexecution.filters import TestCycleFieldFilter
from ..testexecution.models import TestCycleList, TestRunList
from ..testcases.models import TestSuiteList, TestCaseVersionList
from ..users.decorators import login_redirect
from ..users.models import UserList

from .forms import TestCycleForm, TestRunForm, TestSuiteForm, TestCaseForm



def home(request):
    return redirect(reverse("manage_testcycles") + "?finder=1")



@login_redirect
@dec.actions(TestCycleList, ["activate", "deactivate", "delete", "clone"])
@dec.filter("cycles",
            ("status", status_filters.TestCycleStatusFilter),
            ("product", ProductFieldFilter),
            ("name", KeywordFilter))
@dec.paginate("cycles")
@dec.sort("cycles")
@dec.ajax("manage/product/testcycle/_cycles_list.html")
def testcycles(request):
    return TemplateResponse(
        request,
        "manage/product/testcycle/cycles.html",
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
        "manage/product/testcycle/add_cycle.html",
        {"form": form}
        )



@never_cache
@login_redirect
@dec.actions(TestRunList, ["clone", "delete"], fall_through=True)
@dec.sort("testruns")
@dec.ajax("manage/product/testcycle/_runs_list.html")
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
        testCycle=cycle.id)

    return TemplateResponse(
        request,
        "manage/product/testcycle/edit_cycle.html",
        {
            "form": form,
            "cycle": cycle,
            "testruns": testruns,
            }
        )



@login_redirect
def testcycle_details(request, cycle_id):
    cycle = TestCycleList.get_by_id(cycle_id, auth=request.auth)
    return TemplateResponse(
        request,
        "manage/product/testcycle/_cycle_details.html",
        {"cycle": cycle})



@login_redirect
@dec.actions(TestRunList, ["activate", "deactivate", "delete", "clone"])
@dec.filter("runs",
            ("status", status_filters.TestRunStatusFilter),
            ("product", ProductFieldFilter),
            ("testCycle", TestCycleFieldFilter),
            ("name", KeywordFilter))
@dec.paginate("runs")
@dec.sort("runs")
@dec.ajax("manage/product/testrun/_runs_list.html")
def testruns(request):
    return TemplateResponse(
        request,
        "manage/product/testrun/runs.html",
        {"runs": TestRunList.ours(auth=request.auth)}
        )



@login_redirect
def add_testrun(request):
    tcid = request.GET.get("cycle")
    suites = TestSuiteList.ours(auth=request.auth)
    form = TestRunForm(
        request.POST or None,
        initial=tcid and {"test_cycle": tcid} or {},
        test_cycle_choices=TestCycleList.ours(auth=request.auth),
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
        "manage/product/testrun/add_run.html",
        {"form": form}
        )



@never_cache
@login_redirect
def edit_testrun(request, run_id):
    run = TestRunList.get_by_id(run_id, auth=request.auth)
    form = TestRunForm(
        request.POST or None,
        instance=run,
        test_cycle_choices=[run.testCycle],
        suites_choices=TestSuiteList.ours(auth=request.auth).filter(
            product=run.product, status=TestSuiteStatus.ACTIVE),
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
        "manage/product/testrun/edit_run.html",
        {
            "form": form,
            "run": run,
            }
        )



@login_redirect
def testrun_details(request, run_id):
    run = TestRunList.get_by_id(run_id, auth=request.auth)
    return TemplateResponse(
        request,
        "manage/product/testrun/_run_details.html",
        {"run": run})



@login_redirect
@dec.actions(TestSuiteList, ["activate", "deactivate", "delete", "clone"])
@dec.filter("suites",
            ("status", status_filters.TestSuiteStatusFilter),
            ("product", ProductFieldFilter),
            ("name", KeywordFilter))
@dec.paginate("suites")
@dec.sort("suites")
@dec.ajax("manage/product/testsuite/_suites_list.html")
def testsuites(request):
    return TemplateResponse(
        request,
        "manage/product/testsuite/suites.html",
        {"suites": TestSuiteList.ours(auth=request.auth)}
        )



@login_redirect
def add_testsuite(request):
    form = TestSuiteForm(
        request.POST or None,
        product_choices=ProductList.ours(auth=request.auth),
        cases_choices=TestCaseVersionList.latest(auth=request.auth).filter(
            company=conf.TCM_COMPANY_ID, status=TestCaseStatus.ACTIVE),
        auth=request.auth)
    if request.method == "POST" and form.is_valid():
        suite = form.save()
        messages.success(
            request,
            "The test suite '%s' has been created."  % suite.name)
        return redirect("manage_testsuites")
    return TemplateResponse(
        request,
        "manage/product/testsuite/add_suite.html",
        {"form": form}
        )



@never_cache
@login_redirect
def edit_testsuite(request, suite_id):
    suite = TestSuiteList.get_by_id(suite_id, auth=request.auth)
    form = TestSuiteForm(
        request.POST or None,
        instance=suite,
        product_choices=[suite.product],
        cases_choices=TestCaseVersionList.latest(auth=request.auth).filter(
            product=suite.product.id, status=TestCaseStatus.ACTIVE),
        auth=request.auth)
    if request.method == "POST" and form.is_valid():
        suite = form.save()
        messages.success(
            request,
            "The test suite '%s' has been saved."  % suite.name)
        return redirect("manage_testsuites")

    return TemplateResponse(
        request,
        "manage/product/testsuite/edit_suite.html",
        {
            "form": form,
            "suite": suite,
            }
        )



@login_redirect
def testsuite_details(request, suite_id):
    suite = TestSuiteList.get_by_id(suite_id, auth=request.auth)
    return TemplateResponse(
        request,
        "manage/product/testsuite/_suite_details.html",
        {"suite": suite})



@login_redirect
@dec.actions(
    TestCaseVersionList,
    ["approve", "reject", "activate", "deactivate", "delete"])
@dec.filter("cases",
            ("status", status_filters.TestCaseStatusFilter),
            ("approval", status_filters.ApprovalStatusFilter),
            ("product", ProductFieldFilter),
            ("name", KeywordFilter),
            ("step", KeywordFilter),
            ("result", KeywordFilter),
            )
@dec.paginate("cases")
@dec.sort("cases")
@dec.ajax("manage/product/testcase/_cases_list.html")
def testcases(request):
    return TemplateResponse(
        request,
        "manage/product/testcase/cases.html",
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
        "manage/product/testcase/add_case.html",
        {"form": form })



@never_cache
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
        "manage/product/testcase/edit_case.html",
        {
            "form": form,
            "case": case,
            }
        )



@login_redirect
def testcase_details(request, case_id):
    case = TestCaseVersionList.get_by_id(case_id, auth=request.auth)
    return TemplateResponse(
        request,
        "manage/product/testcase/_case_details.html",
        {"case": case})
