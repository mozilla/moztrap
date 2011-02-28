"""
Remote objects related to the "documentation" (as opposed to execution) side of
testing.

"""
from ..core.api import RemoteObject, Activatable, ListObject, fields
from ..core.models import Company
from ..environments.models import EnvironmentGroupList
from ..products.models import Product
from ..static.fields import StaticData
from ..users.models import User
from . import increment


class Tag(RemoteObject):
    company = fields.Locator(Company)
    tag = fields.Field()


    def __unicode__(self):
        return self.tag



class TagList(ListObject):
    entryclass = Tag
    api_name = "tags"
    default_url = "tags"

    entries = fields.List(fields.Object(Tag))



class TestCase(RemoteObject):
    name = fields.Field()
    description = fields.Field()
    maxAttachmentSizeInMbytes = fields.Field()
    maxNumberOfAttachments = fields.Field()
    product = fields.Locator(Product)
    testCycle = fields.Locator("TestCycle")

    versions = fields.Link("TestCaseVersionList")
    latestversion = fields.Link("TestCaseVersion")


    def __unicode__(self):
        return self.name



class TestCaseList(ListObject):
    entryclass = TestCase
    api_name = "testcases"
    default_url = "testcases"

    entries = fields.List(fields.Object(TestCase))



class TestCaseVersion(Activatable, TestCase):
    majorVersion = fields.Field()
    minorVersion = fields.Field()
    latestVersion = fields.Field()
    testCaseStatus = StaticData("TESTCASESTATUS", api_submit_name=False)
    approvalStatus = StaticData("APPROVALSTATUS", api_submit_name=False)
    approveDate = fields.Date(api_submit_name=False)
    approvedBy = fields.Locator(User, api_submit_name=False)

    environmentgroups = fields.Link(EnvironmentGroupList)
    steps = fields.Link("TestCaseStepList")

    def __unicode__(self):
        return u"%s v%s.%s (%s)" % (
            super(TestCaseVersion, self).__unicode__(),
            self.majorVersion,
            self.minorVersion,
            self.latestVersion and "latest" or "obsolete",
            )


    def approve(self, **kwargs):
        self._put(
            relative_url="approve",
            update_from_response=True,
            **kwargs)


    def reject(self, **kwargs):
        self._put(
            relative_url="reject",
            update_from_response=True,
            **kwargs)


    def versionincrement(self, incr=increment.MINOR, **kwargs):
        self._put(
            relative_url="versionincrement/%s" % incr,
            update_from_response=True,
            full_payload=True,
            **kwargs)



class TestCaseVersionList(ListObject):
    entryclass = TestCaseVersion
    api_name = "testcaseversions"
    default_url = "testcases/versions/"

    entries = fields.List(fields.Object(TestCaseVersion))

    @classmethod
    def latest(cls, **kwargs):
        return cls.get(url="testcases/latestversions/", **kwargs)



class TestCaseStep(RemoteObject):
    name = fields.Field()
    testCaseVersion = fields.Locator(TestCaseVersion)
    stepNumber = fields.Field()
    instruction = fields.Field()
    expectedResult = fields.Field()
    estimatedTimeInMin = fields.Field()


    def __unicode__(self):
        return self.name



class TestCaseStepList(ListObject):
    entryclass = TestCaseStep
    api_name = "testcasestep"


    entries = fields.List(fields.Object(TestCaseStep))



class TestSuite(Activatable, RemoteObject):
    name = fields.Field()
    description = fields.Field()
    product = fields.Locator(Product)
    testSuiteStatus = StaticData("TESTSUITESTATUS", api_submit_name=False)
    useLatestVersions = fields.Field()

    environmentgroups = fields.Link(EnvironmentGroupList)
    includedtestcases = fields.Link("TestSuiteIncludedTestCaseList")


    def addcase(self, case, **kwargs):
        payload = {
            "testCaseVersionId": case.id,
            "priorityId": 0, # @@@
            "runOrder": 0, # @@@
            }
        self._post(
            relative_url="includedtestcases",
            extra_payload=payload,
            **kwargs)


    def clone(self, **kwargs):
        obj = self.__class__()
        self._post(
            relative_url="clone",
            version_payload=False,
            update_from_response=obj,
            **kwargs)
        return obj


    def __unicode__(self):
        return self.name



class TestSuiteList(ListObject):
    entryclass = TestSuite
    api_name = "testsuites"
    default_url = "testsuites/"


    entries = fields.List(fields.Object(TestSuite))



class TestSuiteIncludedTestCase(RemoteObject):
    api_name = "includedtestcase"

    blocking = fields.Field()
    priorityId = fields.Field()
    runOrder = fields.Field()
    testCase = fields.Locator(TestCase)
    testCaseVersion = fields.Locator(TestCaseVersion)
    testSuite = fields.Locator(TestSuite)

    environmentgroups = fields.Link(EnvironmentGroupList)

    def __unicode__(self):
        return self.id



class TestSuiteIncludedTestCaseList(ListObject):
    entryclass = TestSuiteIncludedTestCase
    api_name = "includedtestcases"
    array_name = "includedtestcase"

    entries = fields.List(fields.Object(TestSuiteIncludedTestCase))
