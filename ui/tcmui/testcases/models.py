"""
Remote objects related to the "documentation" (as opposed to execution) side of
testing.

"""
from ..core.api import RemoteObject, Activatable, ListObject, fields
from ..environments.models import EnvironmentGroupList
from ..products.models import Product
from ..static.fields import StaticData
from ..users.models import User



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

    def __unicode__(self):
        return u"%s v%s.%s (%s)" % (
            super(TestCaseVersion, self).__unicode__(),
            self.majorVersion,
            self.minorVersion,
            self.latestVersion and "latest" or "obsolete",
            )


    # @@@ Not currently working, neither are activate/deactivate
    def approve(self, **kwargs):
        self._put(
            relative_url="approve",
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
