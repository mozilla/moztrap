"""
Remote objects related to the test-execution side of testing.

"""
from django.core.urlresolvers import reverse

from ..core.api import Activatable, RemoteObject, ListObject, Named, fields
from ..core.models import CategoryValueInfoList, Company
from ..environments.models import EnvironmentGroupList, EnvironmentList
from ..products.models import Product
from ..static.fields import StaticData
from ..static.status import TestResultStatus
from ..testcases.models import (
    TestCase, TestCaseVersion, TestSuite, TestSuiteList,
    TestSuiteIncludedTestCase)
from ..users.models import User, Team




class TestCycle(Named, Activatable, RemoteObject):
    company = fields.Locator(Company)
    product = fields.Locator(Product)
    name = fields.Field()
    description = fields.Field()
    status = StaticData(
        "TESTCYCLESTATUS", "testCycleStatusId", api_submit_name=False)
    startDate = fields.Date()
    endDate = fields.Date()
    communityAccessAllowed = fields.Field()
    communityAuthoringAllowed = fields.Field()

    environmentgroups = fields.Link(EnvironmentGroupList)
    testruns = fields.Link("TestRunList")
    team = fields.Link(Team, api_name="team/members")
    resultstatus = fields.Link(
        CategoryValueInfoList,
        api_name="reports/coverage/resultstatus",
        cache="TestResultList")

    non_field_filters = {
        "user": "teamMemberId",
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



class TestCycleList(ListObject):
    entryclass = TestCycle
    api_name = "testcycles"
    default_url = "testcycles"

    entries = fields.List(fields.Object(TestCycle))



class TestRun(Named, Activatable, RemoteObject):
    company = fields.Locator(Company)
    product = fields.Locator(Product)
    testCycle = fields.Locator(TestCycle)
    name = fields.Field()
    description = fields.Field()
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
    includedtestcases = fields.Link("TestRunIncludedTestCaseList")
    team = fields.Link(Team, api_name="team/members")
    testsuites = fields.Link(TestSuiteList, cache="IncludedTestSuiteList")
    resultstatus = fields.Link(
        CategoryValueInfoList,
        api_name="reports/coverage/resultstatus",
        cache="TestResultList")

    non_field_filters = {
        "testSuite": "includedTestSuiteId",
        "testCase": "includedTestCaseId",
        "testCaseVersion": "includedTestCaseVersionId",
        "user": "teamMemberId",
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
        return self.resultstatus.to_dict(TestResultStatus)



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
        # @@@ this is too slow to be usable, should be done platform-side
        base = dict([(ev.enumname, 0) for ev in TestResultStatus])

        results = TestResultList.get(auth=self.auth).filter(
            testRun=self.testRun.id,
            testCaseVersion=self.testCaseVersion.id)
        for result in results:
            base[result.status.status.enumname] += 1
        return base


    def suite_resultsummary(self):
        # @@@ this is too slow to be usable, should be done platform-side
        base = dict([(ev.enumname, 0) for ev in TestResultStatus])

        if self.testSuite is not None:
            results = TestResultList.get(auth=self.auth).filter(
                testRun=self.testRun.id,
                testSuite=self.testSuite.id)
            for result in results:
                base[result.status.status.enumname] += 1
        return base



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
    actualResult = fields.Field()
    actualTimeInMin = fields.Field()
    approval = StaticData(
        "APPROVALSTATUS", "approvalStatusId", api_submit_name=False)
    approvedBy = fields.Locator(User, api_submit_name=False)
    comment = fields.Field()
    failedStepNumber = fields.Field()
    product = fields.Locator(Product)
    testCase = fields.Locator(TestCase)
    testCaseVersion = fields.Locator(TestCaseVersion)
    testSuite = fields.Locator(TestSuite)
    testRun = fields.Locator(TestRun)
    status = StaticData(
        "TESTRUNRESULTSTATUS", "testRunResultStatusId", api_submit_name=False)
    tester = fields.Locator(User)

    environments = fields.Link(EnvironmentList)


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
