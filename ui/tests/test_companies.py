import httplib
import json

from mock import patch
from unittest2 import TestCase

from .responses import (FakeResponse, response, make_company, make_identity,
                        make_companies)



@patch("remoteobjects.http.userAgent")
class CompanyTest(TestCase):
    @property
    def resource(self):
        from tcmui.core.models import Company
        return Company


    def creds(self, *args, **kwargs):
        from tcmui.core.api import Credentials
        return Credentials(*args, **kwargs)


    def test_get_data(self, http):
        http.request.return_value = response(
            httplib.OK, make_company(name="Test Company"))

        c = self.resource.get("companies/3")

        self.assertEqual(c.name, "Test Company")


    def test_unicode_conversion(self, http):
        http.request.return_value = response(
            httplib.OK, make_company(name="Test Company"))

        c = self.resource.get("companies/3")

        self.assertEqual(type(c.name), unicode)


    def test_get_url(self, http):
        http.request.return_value = response(
            httplib.OK, make_company(name="Test Company"))

        c = self.resource.get("companies/3")
        c.deliver()

        self.assertEqual(
            http.request.call_args[1]["uri"],
            "http://fake.base/rest/companies/3?_type=json")


    def test_get_id(self, http):
        http.request.return_value = response(
            httplib.OK, make_company(
                name="Test Company",
                resourceIdentity=make_identity(id="3")))

        c = self.resource.get("companies/3")

        self.assertEqual(c.id, "3")


    def test_get_location(self, http):
        http.request.return_value = response(
            httplib.OK, make_company(
                name="Test Company",
                resourceIdentity=make_identity(url="companies/3/")))

        c = self.resource.get("companies/3")
        c.deliver()

        self.assertEqual(c._location, "http://fake.base/rest/companies/3/")


    def test_create(self, http):
        c = self.resource(name="Some Company", address="123 N Main")

        self.assertEqual(c.address, "123 N Main")


    def test_no_auth_no_auth_headers(self, http):
        http.request.return_value = response(
            httplib.OK, make_company(name="Test Company"))

        c = self.resource.get("companies/3")
        c.deliver()

        headers = http.request.call_args[1]["headers"]
        self.assertFalse("cookie" in headers)
        self.assertFalse("authorization" in headers)


    def test_auth_headers_password(self, http):
        http.request.return_value = response(
            httplib.OK, make_company(name="Test Company"))

        c = self.resource.get(
            "companies/3",
            auth=self.creds("user@example.com", password="blah"))
        c.deliver()

        headers = http.request.call_args[1]["headers"]
        self.assertTrue("authorization" in headers)
        self.assertFalse("cookie" in headers)


    def test_auth_headers_cookie(self, http):
        http.request.return_value = response(
            httplib.OK, make_company(name="Test Company"))

        c = self.resource.get(
            "companies/3",
            auth=self.creds("user@example.com", cookie="USERTOKEN: blah"))
        c.deliver()

        headers = http.request.call_args[1]["headers"]
        self.assertFalse("authorization" in headers)
        self.assertTrue("cookie" in headers)


    def test_get_persists_auth(self, http):
        http.request.return_value = response(
            httplib.OK, make_company(name="Test Company"))

        creds = self.creds("user@example.com", cookie="USERTOKEN: blah")

        c = self.resource.get("companies/3", auth=creds)
        c.deliver()

        self.assertEqual(c.auth, creds)


    def test_get_full_url(self, http):
        http.request.return_value = response(
            httplib.OK, make_company(name="Test Company"))

        c = self.resource.get("http://some.other.url/companies/3")
        c.deliver()

        self.assertEqual(
            http.request.call_args[1]["uri"],
            "http://some.other.url/companies/3?_type=json")


    def test_unauthorized(self, http):
        http.request.return_value = response(
            httplib.UNAUTHORIZED, "some error", {"content-type": "text/plain"})

        c = self.resource.get("companies/3")
        with self.assertRaises(self.resource.Unauthorized) as cm:
            c.deliver()

        self.assertEqual(
            cm.exception.args[0],
            "401  requesting Company "
            'http://fake.base/rest/companies/3?_type=json: some error')


    def test_json_error(self, http):
        http.request.return_value = response(
            httplib.CONFLICT, {"errors":[{"error":"email.in.use"}]})

        c = self.resource.get("companies/3")
        with self.assertRaises(self.resource.Conflict) as cm:
            c.deliver()

        self.assertEqual(
            cm.exception.args[0],
            "409  requesting Company "
            "http://fake.base/rest/companies/3?_type=json: email.in.use")


    def test_bad_response(self, http):
        http.request.return_value = response(
            777, "Something is very wrong.")

        c = self.resource.get("companies/3")
        with self.assertRaises(self.resource.BadResponse) as cm:
            c.deliver()

        self.assertEqual(
            cm.exception.args[0],
            "Unexpected response requesting Company "
            "http://fake.base/rest/companies/3?_type=json: 777 ")


    def test_missing_location_header(self, http):
        http.request.return_value = response(
            302, "")

        c = self.resource.get("companies/3")
        with self.assertRaises(self.resource.BadResponse) as cm:
            c.deliver()

        self.assertEqual(
            cm.exception.args[0],
            "'Location' header missing from 302  response requesting Company "
            "http://fake.base/rest/companies/3?_type=json")


    def test_bad_content_type(self, http):
        http.request.return_value = response(
            httplib.OK, "blah", {"content-type": "text/plain"})

        c = self.resource.get("companies/3")
        with self.assertRaises(self.resource.BadResponse) as cm:
            c.deliver()

        self.assertEqual(
            cm.exception.args[0],
            "Bad response fetching Company "
            "http://fake.base/rest/companies/3?_type=json: "
            "content-type text/plain is not an expected type")


    def test_unicode_response(self, http):
        http.request.return_value = (
            FakeResponse(
                httplib.OK,
                headers={"content-type": "application/json"}),
            unicode(json.dumps(make_company(name="Test Company")))
            )

        c = self.resource.get("companies/3")

        self.assertEqual(type(c.name), unicode)


    def test_cache_attribute(self, http):
        with patch("tcmui.core.models.Company.cache", True):
            with patch("remoteobjects.RemoteObject.get") as mock:
                self.resource.get("companies/3")

        from tcmui.core.api import cachedUserAgent

        mock.assert_called_with('companies/3', http=cachedUserAgent)



@patch("remoteobjects.http.userAgent")
class CompanyListTest(TestCase):
    @property
    def resource(self):
        from tcmui.core.models import CompanyList
        return CompanyList


    def creds(self, *args, **kwargs):
        from tcmui.core.api import Credentials
        return Credentials(*args, **kwargs)


    def test_get_data_one(self, http):
        http.request.return_value = response(
            httplib.OK, make_companies({"name":"Test Company"}))

        c = self.resource.get()

        self.assertEqual(c[0].name, "Test Company")


    def test_get_data_multiple(self, http):
        http.request.return_value = response(
            httplib.OK, make_companies(
                {"name": "Test Company"},
                {"name": "Second Test"}))

        c = self.resource.get()

        self.assertEqual(c[1].name, "Second Test")
