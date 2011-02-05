"""
Remote objects related to the "documentation" (as opposed to execution) side of
testing.

"""
from ..core.api import Activatable, RemoteObject, ListObject, fields
from ..environments.models import EnvironmentGroupList
from ..products.models import Product
from ..static.fields import StaticData
from ..testcases.models import TestCase, TestCaseVersion



class TestCycle(Activatable, RemoteObject):
    product = fields.Locator(Product)
    name = fields.Field()
    description = fields.Field()
    testCycleStatus = StaticData("TESTCYCLESTATUS")
    startDate = fields.Date()
    endDate = fields.Date()

    environmentgroups = fields.Link(EnvironmentGroupList)
    testruns = fields.Link("TestRunList")


    def __unicode__(self):
        return self.name



class TestCycleList(ListObject):
    entryclass = TestCycle
    api_name = "testcycles"
    default_url = "testcycles"

    entries = fields.List(fields.Object(TestCycle))



class TestRun(Activatable, RemoteObject):
    product = fields.Locator(Product)
    testCycle = fields.Locator(TestCycle)
    name = fields.Field()
    description = fields.Field()
    testRunStatus = StaticData("TESTRUNSTATUS")
    selfAssignAllowed = fields.Field()
    selfAssignLimit = fields.Field()
    selfAssignPerEnvironment = fields.Field()
    useLatestVersions = fields.Field()
    startDate = fields.Date()
    endDate = fields.Date()

    environmentgroups = fields.Link(EnvironmentGroupList)
    includedtestcases = fields.Link("IncludedTestCaseList")


    def __unicode__(self):
        return self.name


    def add(self, case, **kwargs):
        payload = {"%sid" % case.__class__.__name__.lower(): case.id}
        self._post(
            relative_url="includedtestcases",
            extra_payload=payload,
            **kwargs)



class TestRunList(ListObject):
    entryclass = TestRun
    api_name = "testruns"
    default_url = "testruns"

    entries = fields.List(fields.Object(TestRun))



class IncludedTestCase(RemoteObject):
    blocking = fields.Field()
    priorityId = fields.Field()
    runOrder = fields.Field()
    testCase = fields.Locator(TestCase)
    testCaseVersion = fields.Locator(TestCaseVersion)
    # @@@ testSuite = fields.Locator(TestSuite)
    testRun = fields.Locator(TestRun)


    def __unicode__(self):
        return self.id



class IncludedTestCaseList(ListObject):
    entryclass = IncludedTestCase
    api_name = "includedtestcases"

    entries = fields.List(fields.Object(IncludedTestCase))
