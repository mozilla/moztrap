from mock import patch

from ..environments.builders import (
    environmenttypes, environmentgroups, environments)
from ..responses import response
from ..utils import ResourceTestCase, BaseResourceTest
from .builders import companies, cvis



@patch("tcmui.core.api.userAgent")
class CompanyTest(BaseResourceTest, ResourceTestCase):
    def get_resource_class(self):
        from tcmui.core.models import Company
        return Company


    def get_resource_list_class(self):
        from tcmui.core.models import CompanyList
        return CompanyList


    def test_unicode(self, http):
        c = self.resource_class()
        c.update_from_dict(companies.one(name="The Company"))

        self.assertEqual(unicode(c), u"The Company")


    def test_autogenerate_env_groups(self, http):
        from tcmui.environments.models import (
            EnvironmentGroupList, Environment, EnvironmentType)

        c = self.resource_class()
        c.update_from_dict(companies.one(_url="companies/1"))

        egt = EnvironmentType()
        egt.update_from_dict(environmenttypes.one(groupType=True))

        eta = EnvironmentType()
        eta.update_from_dict(environmenttypes.one(groupType=False, _id=1))

        etb = EnvironmentType()
        etb.update_from_dict(environmenttypes.one(groupType=False, _id=2))

        enva1 = Environment()
        enva1.update_from_dict(environments.one(_id=3, environmentType=eta))
        enva2 = Environment()
        enva2.update_from_dict(environments.one(_id=4, environmentType=eta))

        envb1 = Environment()
        envb1.update_from_dict(environments.one(_id=5, environmentType=etb))
        envb2 = Environment()
        envb2.update_from_dict(environments.one(_id=6, environmentType=etb))

        http.request.return_value = response(
            environmentgroups.array({}, {}, {}, {}))

        generated = c.autogenerate_env_groups([enva1, enva2, envb1, envb2], egt)

        self.assertIsInstance(generated, EnvironmentGroupList)
        self.assertEqual(len(generated), 4)
        req = http.request.call_args[1]
        self.assertEqual(req["uri"], "http://fake.base/rest/companies/1/environmentgroups/environmenttypes/1/autogenerate?_type=json")
        self.assertEqual(req["body"], "environmentIds=3&environmentIds=4&environmentIds=5&environmentIds=6&originalVersionId=0")


    def test_autogenerate_env_groups_no_type(self, http):
        from tcmui.environments.models import (
            EnvironmentGroupList, Environment, EnvironmentType)

        c = self.resource_class()
        c.update_from_dict(companies.one(_url="companies/1"))

        eta = EnvironmentType()
        eta.update_from_dict(environmenttypes.one(groupType=False, _id=1))

        etb = EnvironmentType()
        etb.update_from_dict(environmenttypes.one(groupType=False, _id=2))

        enva1 = Environment()
        enva1.update_from_dict(environments.one(_id=3, environmentType=eta))
        enva2 = Environment()
        enva2.update_from_dict(environments.one(_id=4, environmentType=eta))

        envb1 = Environment()
        envb1.update_from_dict(environments.one(_id=5, environmentType=etb))
        envb2 = Environment()
        envb2.update_from_dict(environments.one(_id=6, environmentType=etb))

        http.request.return_value = response(
            environmentgroups.array({}, {}, {}, {}))

        generated = c.autogenerate_env_groups([enva1, enva2, envb1, envb2])

        self.assertIsInstance(generated, EnvironmentGroupList)
        self.assertEqual(len(generated), 4)
        req = http.request.call_args[1]
        self.assertEqual(req["uri"], "http://fake.base/rest/companies/1/environmentgroups/autogenerate?_type=json")
        self.assertEqual(req["body"], "environmentIds=3&environmentIds=4&environmentIds=5&environmentIds=6&originalVersionId=0")



@patch("tcmui.core.api.userAgent")
class CategoryValueInfoTest(BaseResourceTest, ResourceTestCase):
    def get_resource_class(self):
        from tcmui.core.models import CategoryValueInfo
        return CategoryValueInfo


    def get_resource_list_class(self):
        from tcmui.core.models import CategoryValueInfoList
        return CategoryValueInfoList


    def test_unicode(self, http):
        c = self.resource_class()
        c.update_from_dict(cvis.one(categoryName=2, categoryValue=5))

        self.assertEqual(unicode(c), u"2: 5")


    def test_to_dict(self, http):
        c = self.resource_list_class()
        c.update_from_dict(
            cvis.array({"categoryName":2, "categoryValue": 5}))

        from flufl.enum import Enum
        class SampleEnum(Enum):
            ONE = 1
            TWO = 2

        self.assertEqual(c.to_dict(SampleEnum), {"ONE": 0, "TWO": 5})


    def test_to_dict_default(self, http):
        c = self.resource_list_class()
        c.update_from_dict(
            cvis.array({"categoryName":2, "categoryValue": 5}))

        from flufl.enum import Enum
        class SampleEnum(Enum):
            ONE = 1
            TWO = 2

        self.assertEqual(c.to_dict(SampleEnum, default=2), {"ONE": 2, "TWO": 5})
