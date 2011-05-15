from mock import patch

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
