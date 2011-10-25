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
"""
Remote objects related to the test-execution side of testing.

"""
import math

from django.core.urlresolvers import reverse

from ..core.api import Activatable, RemoteObject, ListObject, Named, fields
from ..core.models import CategoryValueInfo, CategoryValueInfoList, Company
from ..environments.models import (
    ExplodedEnvironmentGroupList, EnvironmentGroupList, EnvironmentList)
from ..products.models import Product
from ..relatedbugs.models import ExternalBugList
from ..static.fields import StaticData
from ..static.status import TestResultStatus
from ..testcases.models import (
    TestCase, TestCaseVersion, TestSuite, TestSuiteList,
    TestSuiteIncludedTestCase)
from ..users.models import User, Team



def round_percent(val):
    """
    Takes ``val``, which is either falsy or anything coercable to a
    float. Returns an integer: zero in the former case, the float rounded to an
    integer in the latter case.

    Rounds up when under 50 and down when over 50. This ensures that the
    endpoints are special: we never call something "0" or "100" unless it
    really is exactly that.

    """
    if not val:
        return 0
    val = float(val)
    if val > 50:
        val = math.floor(val)
    else:
        val = math.ceil(val)
    return int(val)



class TestCycle(Named, Activatable, RemoteObject):
    company = fields.Locator(Company)
    product = fields.Locator(Product)
    name = fields.CharField()
    description = fields.CharField()
    status = StaticData(
        "TESTCYCLESTATUS", "testCycleStatusId", api_submit_name=False)
    startDate = fields.Date()
    endDate = fields.Date()
    communityAccessAllowed = fields.Field()
    communityAuthoringAllowed = fields.Field()

    environmentgroups = fields.Link(EnvironmentGroupList)
    environmentgroups_prefetch = fields.Link(
        ExplodedEnvironmentGroupList, api_name="environmentgroups/exploded")
    testruns = fields.Link("TestRunList")
    team = fields.Link(Team, api_name="team/members")
    resultstatus = fields.Link(
        CategoryValueInfoList,
        api_name="reports/coverage/resultstatus",
        cache="TestResultList")
    completionstatus = fields.Link(
        CategoryValueInfo,
        api_name="reports/coverage/percentcomplete",
        cache="TestResultList")

    non_field_filters = {
        "tester": "teamMemberId",
        "environment": "includedEnvironmentId",
        }


    def __unicode__(self):
        return self.name


    def get_absolute_url(self):
        return reverse(
            "testruns",
            kwargs={"cycle_id": self.id})


    def approveallresults(self, **kwargs):
        self._put(
            relative_url="approveallresults",
            invalidate_cache=["TestResultList"],
            **kwargs)


    def clone(self, assignments=False, **kwargs):
        obj = self.__class__()
        self._post(
            relative_url="clone",
            version_payload=False,
            extra_payload={"cloneAssignments": assignments},
            update_from_response=obj,
            **kwargs)
        return obj


    def resultsummary(self):
        return self.resultstatus.to_dict(TestResultStatus)


    def percentcomplete(self):
        return round_percent(self.completionstatus.categoryValue)


    def deactivate(self, **kwargs):
        self._put(
            relative_url="deactivate",
            update_from_response=True,
            invalidate_cache=(
                TestCycleList.cache_buckets(self.id) +
                TestRun.cache_buckets(self.id) +
                TestRunList.cache_buckets(self.id)
                ),
            **kwargs)



class TestCycleList(ListObject):
    entryclass = TestCycle
    api_name = "testcycles"
    default_url = "testcycles"

    entries = fields.List(fields.Object(TestCycle))



class TestRun(Named, Activatable, RemoteObject):
    company = fields.Locator(Company)
    product = fields.Locator(Product)
    testCycle = fields.Locator(TestCycle)
    name = fields.CharField()
    description = fields.CharField()
    status = StaticData(
        "TESTRUNSTATUS", "testRunStatusId", api_submit_name=False)
    selfAssignAllowed = fields.Field()
    selfAssignLimit = fields.Field()
    selfAssignPerEnvironment = fields.Field()
    useLatestVersions = fields.Field()
    autoAssignToTeam = fields.Field()
    startDate = fields.Date()
    endDate = fields.Date()

    environmentgroups = fields.Link(EnvironmentGroupList)
    environmentgroups_prefetch = fields.Link(
        ExplodedEnvironmentGroupList, api_name="environmentgroups/exploded")
    includedtestcases = fields.Link("TestRunIncludedTestCaseList")
    team = fields.Link(Team, api_name="team/members")
    testsuites = fields.Link(TestSuiteList, cache="IncludedTestSuiteList")

    non_field_filters = {
        "testSuite": "includedTestSuiteId",
        "testCase": "includedTestCaseId",
        "testCaseVersion": "includedTestCaseVersionId",
        "tester": "teamMemberId",
        "environment": "includedEnvironmentId",
        }


    def __unicode__(self):
        return self.name


    def get_absolute_url(self):
        return reverse("runtests_run", kwargs={"testrun_id": self.id})


    def addcase(self, case, **kwargs):
        payload = {
            "testCaseVersionId": case.id,
            "priorityId": 0, # @@@
            "runOrder": 0, # @@@
            }
        self._post(
            relative_url="includedtestcases",
            extra_payload=payload,
            invalidate_cache=[
                "TestRunIncludedTestCaseList", "IncludedTestSuiteList"],
            **kwargs)


    def addsuite(self, suite, **kwargs):
        self._post(
            relative_url="includedtestcases/testsuite/%s/" % suite.id,
            invalidate_cache=[
                "IncludedTestSuiteList",
                "TestRunIncludedTestCaseList"],
            **kwargs)


    def removesuite(self, suite):
        for itc in TestRunIncludedTestCaseList.get(auth=self.auth).filter(
            testRun=self, testSuite=suite):
            itc.delete(invalidate_cache=[
                    "IncludedTestSuiteList",
                    "TestRunIncludedTestCaseList"])


    def _get_suites(self):
        return self.testsuites


    def _set_suites(self, suites):
        existing = dict((s.id, s) for s in self.testsuites)
        for suite in suites:
            if suite.id not in existing:
                self.addsuite(suite)
            else:
                del existing[suite.id]
        for suite in existing.itervalues():
            self.removesuite(suite)


    suites = property(_get_suites, _set_suites)


    def approveallresults(self, **kwargs):
        self._put(
            relative_url="approveallresults",
            invalidate_cache=["TestResultList"],
            **kwargs)


    def clone(self, assignments=False, **kwargs):
        obj = self.__class__()
        self._post(
            relative_url="clone",
            version_payload=False,
            extra_payload={"cloneAssignments": assignments},
            update_from_response=obj,
            **kwargs)
        return obj


    def resultsummary(self):
        return self.testCycle.resultstatus.raw_filter(
            testRunId=self.id).to_dict(TestResultStatus)


    def percentcomplete(self):
        return round_percent(self.testCycle.completionstatus.raw_filter(
            testRunId=self.id).categoryValue)



class TestRunList(ListObject):
    entryclass = TestRun
    api_name = "testruns"
    default_url = "testruns"

    entries = fields.List(fields.Object(TestRun))



class TestRunIncludedTestCase(TestSuiteIncludedTestCase):
    testRun = fields.Locator(TestRun)
    testCycle = fields.Locator(TestCycle)

    assignments = fields.Link("TestCaseAssignmentList")


    non_field_filters = {
        "name": "name",
        "status": "testCaseStatusId",
        }


    def assign(self, tester, **kwargs):
        payload = {"testerId": tester.id}
        assignment = TestCaseAssignment()
        self._post(
            relative_url="assignments",
            extra_payload=payload,
            update_from_response=assignment,
            **kwargs)
        assignment.auth = self.auth
        return assignment


    def approveallresults(self, **kwargs):
        self.testRun._put(
            relative_url="approvetestcaseresults/%s" % self.testCase.id,
            invalidate_cache=["TestResultList"],
            **kwargs)


    def resultsummary(self):
        return self.testRun.testCycle.resultstatus.raw_filter(
            testRunId=self.testRun.id, testCaseId=self.testCase.id).to_dict(
            TestResultStatus)



class TestRunIncludedTestCaseList(ListObject):
    entryclass = TestRunIncludedTestCase
    api_name = "includedtestcases"
    array_name = "Includedtestcase"
    default_url = "testruns/includedtestcases"

    entries = fields.List(fields.Object(TestRunIncludedTestCase))



class TestCaseAssignment(RemoteObject):
    product = fields.Locator(Product)
    testCase = fields.Locator(TestCase)
    testCaseVersion = fields.Locator(TestCaseVersion)
    testSuite = fields.Locator(TestSuite)
    tester = fields.Locator(User)
    testRun = fields.Locator(TestRun)

    environmentgroups = fields.Link(EnvironmentGroupList)
    results = fields.Link("TestResultList")

    def __unicode__(self):
        return self.id



class TestCaseAssignmentList(ListObject):
    # don't cache assignment lists, assignments get auto-generated
    cache = False

    entryclass = TestCaseAssignment
    api_name = "testcaseassignments"
    default_url = "testruns/assignments"

    entries = fields.List(fields.Object(TestCaseAssignment))



class TestResult(RemoteObject):
    company = fields.Locator(Company)
    product = fields.Locator(Product)
    actualResult = fields.CharField()
    actualTimeInMin = fields.Field()
    approval = StaticData(
        "APPROVALSTATUS", "approvalStatusId", api_submit_name=False)
    approvedBy = fields.Locator(User, api_submit_name=False)
    comment = fields.CharField()
    failedStepNumber = fields.Field()
    product = fields.Locator(Product)
    testCase = fields.Locator(TestCase)
    testCaseVersion = fields.Locator(TestCaseVersion)
    testSuite = fields.Locator(TestSuite)
    testRun = fields.Locator(TestRun)
    status = StaticData(
        "TESTRUNRESULTSTATUS", "testRunResultStatusId", api_submit_name=False)
    tester = fields.Locator(User)

    relatedbugs = fields.ReadOnlyLink(ExternalBugList)
    environments = fields.Link(EnvironmentList)

    non_field_filters = {
        "environment": "includedEnvironmentId",
        }


    def __unicode__(self):
        return self.id


    def start(self, **kwargs):
        self._put(
            relative_url="start",
            update_from_response=True,
            **kwargs)


    def approve(self, **kwargs):
        self._put(
            relative_url="approve",
            update_from_response=True,
            **kwargs)


    def finishsucceed(self, **kwargs):
        self._put(
            relative_url="finishsucceed",
            update_from_response=True,
            **kwargs)


    def finishinvalidate(self, comment, **kwargs):
        self._put(
            relative_url="finishinvalidate",
            extra_payload={"comment": comment},
            update_from_response=True,
            **kwargs)


    def finishfail(self, failedStepNumber, actualResult, **kwargs):
        self._put(
            relative_url="finishfail",
            extra_payload={
                "failedStepNumber": failedStepNumber,
                "actualResult": actualResult
                },
            update_from_response=True,
            **kwargs)


    def reject(self, comment, **kwargs):
        self._put(
            relative_url="reject",
            extra_payload={"comment": comment},
            update_from_response=True,
            **kwargs)



class TestResultList(ListObject):
    entryclass = TestResult
    api_name = "testresults"
    default_url = "testruns/results"

    entries = fields.List(fields.Object(TestResult))
