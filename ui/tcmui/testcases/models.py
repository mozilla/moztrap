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
    company = fields.Locator(Company)
    testCycle = fields.Locator("TestCycle")

    versions = fields.Link("TestCaseVersionList")
    latestversion = fields.Link("TestCaseVersion")


    def __unicode__(self):
        return self.name


    @classmethod
    def cache_dependent_buckets(cls, id=None):
        # modifying a TestCase will modify its TestCaseVersion
        return (
            TestCaseList.cache_buckets(id) +
            TestCaseVersion.cache_buckets(id) +
            TestCaseVersionList.cache_buckets(id))



class TestCaseList(ListObject):
    entryclass = TestCase
    api_name = "testcases"
    default_url = "testcases"

    entries = fields.List(fields.Object(TestCase))


    @classmethod
    def cache_dependent_buckets(cls, id=None):
        # POSTing a new TestCase to TestCaseList will also create a new
        # TestCaseVersion (thus invalidating the cache for TestCaseVersionList)
        return (
            super(TestCaseList, cls).cache_dependent_buckets() +
            TestCaseVersionList.cache_buckets(id))



class TestCaseVersion(Activatable, TestCase):
    majorVersion = fields.Field()
    minorVersion = fields.Field()
    latestVersion = fields.Field()
    testCaseId = fields.Field()
    automated = fields.Field()
    automationUri = fields.Field()
    status = StaticData(
        "TESTCASESTATUS", "testCaseStatusId", api_submit_name=False)
    approval = StaticData(
        "APPROVALSTATUS", "approvalStatusId", api_submit_name=False)
    approveDate = fields.Date(api_submit_name=False)
    approvedBy = fields.Locator(User, api_submit_name=False)

    environmentgroups = fields.Link(EnvironmentGroupList)
    steps = fields.Link("TestCaseStepList")


    non_field_filters = {
        "step": "instruction",
        "result": "expectedResult",
        }


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
    status = StaticData(
        "TESTSUITESTATUS", "testSuiteStatusId", api_submit_name=False)
    useLatestVersions = fields.Field()

    environmentgroups = fields.Link(EnvironmentGroupList)
    includedtestcases = fields.Link("TestSuiteIncludedTestCaseList")


    def addcase(self, case, **kwargs):
        # @@@ https://bugzilla.mozilla.org/show_bug.cgi?id=665135
        if case.product.id != self.product.id:
            e = self.Conflict(
                "Can't add case %s from product %s to suite %s from product %s"
                % (case, case.product.id, self, self.product.id))
            e.response_error = "wrong.product"
            raise e
        payload = {
            "testCaseVersionId": case.id,
            "priorityId": 0, # @@@
            "runOrder": 0, # @@@
            }
        self._post(
            relative_url="includedtestcases",
            extra_payload=payload,
            invalidate_cache=["TestSuiteIncludedTestCaseList"],
            **kwargs)


    def _get_cases(self):
        return TestCaseVersionList(
            entries=[
                itc.testCaseVersion for itc in
                self.includedtestcases.sort("runOrder")])


    def _set_cases(self, cases):
        existing = dict(
            (itc.testCaseVersion.id, itc) for itc in self.includedtestcases)
        for case in cases:
            if case.id not in existing:
                self.addcase(case)
            else:
                del existing[case.id]
        for itc in existing.itervalues():
            itc.delete()


    cases = property(_get_cases, _set_cases)


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

    company = fields.Locator(Company)
    product = fields.Locator(Product)
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
    array_name = "Includedtestcase"

    entries = fields.List(fields.Object(TestSuiteIncludedTestCase))
