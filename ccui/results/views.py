# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
# 
# This file is part of Case Conductor.
# 
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ..core import decorators as dec
from ..core.filters import KeywordFilter
from ..core.util import get_object_or_404
from ..environments.filters import EnvironmentFilter
from ..products.filters import ProductFieldFilter
from ..static.filters import TestResultStatusFilter
from ..static.status import TestCycleStatus, TestRunStatus
from ..testexecution.models import (
    TestCycleList, TestRunList, TestRunIncludedTestCaseList, TestResultList)
from ..users.decorators import login_redirect
from ..users.filters import UserFieldFilter, TeamFieldFilter

from .finder import ResultsFinder
from . import filters



@dec.finder(ResultsFinder)
def home(request):
    return redirect(reverse("results_testcycles") + "?openfinder=1&status=2")



@login_redirect
@dec.finder(ResultsFinder)
@dec.filter("cycles",
            ("status", filters.NonDraftTestCycleStatusFilter),
            ("product", ProductFieldFilter),
            ("name", KeywordFilter),
            ("tester", TeamFieldFilter),
            ("environment", EnvironmentFilter),
            )
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
def testcycle_details(request, cycle_id):
    cycle = get_object_or_404(TestCycleList, cycle_id, auth=request.auth)
    return TemplateResponse(
        request,
        "results/testcycle/_cycle_details.html",
        {"cycle": cycle})



@login_redirect
@dec.finder(ResultsFinder)
@dec.filter("runs",
            ("status", filters.NonDraftTestRunStatusFilter),
            ("product", ProductFieldFilter),
            ("testCycle", filters.NonDraftTestCycleFieldFilter),
            ("name", KeywordFilter),
            ("tester", TeamFieldFilter),
            ("environment", EnvironmentFilter),
            )
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
def testrun_details(request, run_id):
    run = get_object_or_404(TestRunList, run_id, auth=request.auth)
    return TemplateResponse(
        request,
        "results/testrun/_run_details.html",
        {"run": run})



@login_redirect
@dec.finder(ResultsFinder)
@dec.filter("includedcases",
            ("status", filters.NonDraftTestCaseStatusFilter),
            ("testRun", filters.NonDraftTestRunFieldFilter),
            ("product", ProductFieldFilter),
            ("testSuite", filters.TestSuiteFieldFilter),
            ("name", KeywordFilter),
            ("environment", EnvironmentFilter),
            )
@dec.paginate("includedcases")
@dec.sort("includedcases")
def testcases(request):
    includedcases = TestRunIncludedTestCaseList.ours(auth=request.auth)
    return TemplateResponse(
        request,
        "results/testcase/cases.html",
        {"includedcases": includedcases})



@login_redirect
def testcase_details(request, itc_id):
    itc = get_object_or_404(TestRunIncludedTestCaseList, itc_id, auth=request.auth)
    return TemplateResponse(
        request,
        "results/testcase/_case_details.html",
        {"itc": itc})



@login_redirect
@dec.finder(ResultsFinder)
@dec.filter("results",
            ("tester", UserFieldFilter),
            ("status", TestResultStatusFilter),
            ("comment", KeywordFilter),
            ("environment", EnvironmentFilter),
            )
@dec.paginate("results")
@dec.sort("results", "status", "desc")
def testresults(request, itc_id):
    itc = get_object_or_404(TestRunIncludedTestCaseList, itc_id, auth=request.auth)
    results = TestResultList.ours(auth=request.auth).filter(
        testCaseVersion=itc.testCaseVersion.id,
        testRun=itc.testRun.id)
    return TemplateResponse(
        request,
        "results/testcase/included_case_detail.html",
        {"includedcase": itc, "results": results})
