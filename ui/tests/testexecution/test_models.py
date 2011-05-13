from mock import patch

from ..responses import (
    response, make_locator, make_identity, make_boolean, make_array, make_one)
from ..utils import BaseResourceTest, ResourceTestCase



@patch("tcmui.core.api.userAgent")
class TestCycleTest(BaseResourceTest, ResourceTestCase):
    RESOURCE_DEFAULTS = {
        "communityAccessAllowed": False,
        "communityAuthoringAllowed": False,
        "companyId": 1,
        "companyLocator": make_locator(id=1, url="companies/1"),
        "description": "",
        "name": "Default Test Cycle",
        "productId": 1,
        "productLocator": make_locator(id=1, url="products/1"),
        "startDate": "2011-01-01T00:00:00Z",
        "testCycleStatusId": 1,
        }


    RESOURCE_NAME = "testcycle"
    RESOURCE_NAME_PLURAL = "testcycles"


    def get_resource_class(self):
        from tcmui.testexecution.models import TestCycle
        return TestCycle


    def get_resource_list_class(self):
        from tcmui.testexecution.models import TestCycleList
        return TestCycleList


    def test_unicode(self, http):
        c = self.resource_class()
        c.update_from_dict(self.make_one(name="The Test Cycle"))

        self.assertEqual(unicode(c), u"The Test Cycle")


    def test_get_absolute_url(self, http):
        c = self.resource_class()
        c.update_from_dict(self.make_one(resourceIdentity=make_identity(id=2)))

        self.assertEqual(c.get_absolute_url(), "/cycle/2/")


    def test_approveallresults(self, http):
        http.request.return_value = response(self.make_one(
                resourceIdentity=make_identity(url="testcycles/1")))

        c = self.resource_class.get("testcycles/1")

        http.request.return_value = response(make_boolean(True))

        c.approveallresults()

        req = http.request.call_args[1]
        self.assertEqual(
            req["uri"],
            "http://fake.base/rest/testcycles/1/approveallresults?_type=json")
        self.assertEqual(req["method"], "PUT")


    def test_clone(self, http):
        http.request.return_value = response(self.make_one(
                resourceIdentity=make_identity(url="testcycles/1")))

        c = self.resource_class.get("testcycles/1")

        http.request.return_value = response(self.make_one(
                name="Cloned Test Cycle",
                resourceIdentity=make_identity(id=2, url="testcycles/2")))

        new = c.clone()

        self.assertEqual(new.name, "Cloned Test Cycle")
        self.assertIsInstance(new, self.resource_class)
        req = http.request.call_args[1]
        self.assertEqual(
            req["uri"], "http://fake.base/rest/testcycles/1/clone?_type=json")
        self.assertEqual(req["method"], "POST")
        self.assertEqual(req["body"], "cloneAssignments=False")


    def test_clone_assignments(self, http):
        http.request.return_value = response(self.make_one(
                resourceIdentity=make_identity(url="testcycles/1")))

        c = self.resource_class.get("testcycles/1")

        http.request.return_value = response(self.make_one(
                name="Cloned Test Cycle",
                resourceIdentity=make_identity(id=2, url="testcycles/2")))

        new = c.clone(assignments=True)

        self.assertEqual(new.name, "Cloned Test Cycle")
        self.assertIsInstance(new, self.resource_class)
        req = http.request.call_args[1]
        self.assertEqual(
            req["uri"], "http://fake.base/rest/testcycles/1/clone?_type=json")
        self.assertEqual(req["method"], "POST")
        self.assertEqual(req["body"], "cloneAssignments=True")


    def test_resultsummary(self, http):
        http.request.return_value = response(self.make_one(
                resourceIdentity=make_identity(url="testcycles/1")))

        c = self.resource_class.get("testcycles/1")

        http.request.return_value = response(
            make_array(
                "CategoryValueInfo",
                "CategoryValueInfo",
                make_one(
                    "CategoryValueInfo", categoryName=1, categoryValue=159),
                make_one(
                    "CategoryValueInfo", categoryName=5, categoryValue=1)))

        self.assertEqual(
            c.resultsummary(),
            {
                "BLOCKED": 0,
                "FAILED": 0,
                "INVALIDATED": 0,
                "PASSED": 0,
                "PENDING": 159,
                "STARTED": 1,
                })
