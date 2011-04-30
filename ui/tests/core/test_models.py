from mock import patch

from ..utils import ResourceTestCase, BaseResourceTest




@patch("remoteobjects.http.userAgent")
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
    RESOURCE_NAME_PLURAL = "companies"


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

