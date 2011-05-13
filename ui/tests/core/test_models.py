from mock import patch

from ..utils import ResourceTestCase, BaseResourceTest




@patch("tcmui.core.api.userAgent")
class CompanyTest(BaseResourceTest, ResourceTestCase):
    RESOURCE_DEFAULTS = {
        "name": "Default company name",
        "address": "Default company address",
        "city": "Default company city",
        "country": 239,
        "phone": "123-456-7890",
        "url": "www.example.com",
        "zip": "12345",
        }


    RESOURCE_NAME = "company"


    def get_resource_class(self):
        from tcmui.core.models import Company
        return Company


    def get_resource_list_class(self):
        from tcmui.core.models import CompanyList
        return CompanyList


    def test_unicode(self, http):
        c = self.resource_class()
        c.update_from_dict(self.make_one(name="The Company"))

        self.assertEqual(unicode(c), u"The Company")



@patch("tcmui.core.api.userAgent")
class CategoryValueInfoTest(BaseResourceTest, ResourceTestCase):
    RESOURCE_DEFAULTS = {
        "categoryName": 1,
        "categoryValue": 1,
        }

    RESOURCE_ADD_TIMELINE = False
    RESOURCE_ADD_IDENTITY = False


    RESOURCE_NAME = "CategoryValueInfo"


    def get_resource_class(self):
        from tcmui.core.models import CategoryValueInfo
        return CategoryValueInfo


    def get_resource_list_class(self):
        from tcmui.core.models import CategoryValueInfoList
        return CategoryValueInfoList


    def test_unicode(self, http):
        c = self.resource_class()
        c.update_from_dict(self.make_one(categoryName=2, categoryValue=5))

        self.assertEqual(unicode(c), u"2: 5")


    def test_to_dict(self, http):
        c = self.resource_list_class()
        c.update_from_dict(
            self.make_array({"categoryName":2, "categoryValue": 5}))

        from flufl.enum import Enum
        class SampleEnum(Enum):
            ONE = 1
            TWO = 2

        self.assertEqual(c.to_dict(SampleEnum), {"ONE": 0, "TWO": 5})


    def test_to_dict_default(self, http):
        c = self.resource_list_class()
        c.update_from_dict(
            self.make_array({"categoryName":2, "categoryValue": 5}))

        from flufl.enum import Enum
        class SampleEnum(Enum):
            ONE = 1
            TWO = 2

        self.assertEqual(c.to_dict(SampleEnum, default=2), {"ONE": 2, "TWO": 5})
