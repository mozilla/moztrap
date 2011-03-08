import httplib

from mock import patch
from unittest2 import TestCase

from .responses import response, make_company



@patch("remoteobjects.http.userAgent")
class CompanyTest(TestCase):
    @property
    def resource(self):
        from tcmui.core.models import Company
        return Company


    def test_get_one(self, http):
        http.request.return_value = response(
            httplib.OK, make_company(name="Test Company"))

        c = self.resource.get("companies/3")

        self.assertEqual(c.name, "Test Company")
