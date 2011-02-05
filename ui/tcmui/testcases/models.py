"""
Remote objects related to the "documentation" (as opposed to execution) side of
testing.

"""
from ..core.api import RemoteObject, Activatable, ListObject, fields
from ..core.models import CompanyLinkedRemoteObject
from ..environments.models import EnvironmentGroupList
from ..products.models import Product
from ..static.fields import StaticData
from ..users.models import User



class Tag(CompanyLinkedRemoteObject):
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
    testCaseStatus = StaticData("TESTCASESTATUS")
    approvalStatus = StaticData("APPROVALSTATUS")
    approveDate = fields.Date()
    approvedBy = fields.Locator(User)

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


    def versionincrement(self, increment=1, **kwargs):
        self._put(
            relative_url="versionincrement/%s" % increment,
            update_from_response=True,
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
