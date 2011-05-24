from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ..testexecution.models import (
    TestCycleList, TestRunList, TestRunIncludedTestCaseList, TestResultList)
from ..core import decorators as dec
from ..products.filters import ProductFieldFilter
from ..static.filters import TestResultStatusFilter
from ..static.status import TestCycleStatus, TestRunStatus
from ..users.decorators import login_redirect
from ..users.filters import UserFieldFilter

from . import filters



def home(request):
    return redirect(reverse("results_testcycles") + "?status=2")



@login_redirect
@dec.filter("cycles",
            ("status", filters.NonDraftTestCycleStatusFilter),
            ("product", ProductFieldFilter))
@dec.paginate("cycles")
@dec.sort("cycles", "product")
def testcycles(request):
    cycles = TestCycleList.ours(auth=request.auth).filter(status=[
            TestCycleStatus.ACTIVE,
            TestCycleStatus.LOCKED,
            TestCycleStatus.CLOSED])
    return TemplateResponse(
        request, "results/testcycle/cycles.html", {"cycles": cycles})



@login_redirect
@dec.filter("runs",
            ("status", filters.NonDraftTestRunStatusFilter),
            ("product", ProductFieldFilter),
            ("testCycle", filters.NonDraftTestCycleFieldFilter))
@dec.paginate("runs")
@dec.sort("runs")
def testruns(request):
    runs = TestRunList.ours(auth=request.auth).filter(status=[
            TestRunStatus.ACTIVE,
            TestRunStatus.LOCKED,
            TestRunStatus.CLOSED])
    return TemplateResponse(
        request, "results/testrun/runs.html", {"runs": runs})



@login_redirect
@dec.filter("includedcases",
            ("testRun", filters.NonDraftTestRunFieldFilter),
            ("product", ProductFieldFilter),
            ("testSuite", filters.TestSuiteFieldFilter))
@dec.paginate("includedcases")
@dec.sort("includedcases")
def testcases(request):
    includedcases = TestRunIncludedTestCaseList.ours(auth=request.auth)
    return TemplateResponse(
        request,
        "results/testcase/cases.html",
        {"includedcases": includedcases})



@login_redirect
@dec.filter("results",
            ("tester", UserFieldFilter),
            ("status", TestResultStatusFilter))
@dec.paginate("results")
@dec.sort("results")
def testresults(request, itc_id):
    itc = TestRunIncludedTestCaseList.get_by_id(itc_id, auth=request.auth)
    results = TestResultList.ours(auth=request.auth).filter(
        testCaseVersion=itc.testCaseVersion.id,
        testRun=itc.testRun.id)
    return TemplateResponse(
        request,
        "results/testcase/included_case_detail.html",
        {"includedcase": itc, "results": results})
