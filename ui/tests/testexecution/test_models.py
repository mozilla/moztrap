from mock import patch

from ..core.builders import cvis
from ..responses import make_identity, response, make_boolean
from ..static.builders import codevalues
from ..utils import BaseResourceTest, ResourceTestCase
from .builders import testcycles, testruns, testrunitcs, testresults



@patch("tcmui.core.api.userAgent")
class TestCycleTest(BaseResourceTest, ResourceTestCase):
    def get_resource_class(self):
        from tcmui.testexecution.models import TestCycle
        return TestCycle


    def get_resource_list_class(self):
        from tcmui.testexecution.models import TestCycleList
        return TestCycleList


    def test_unicode(self, http):
        c = self.resource_class()
        c.update_from_dict(testcycles.one(name="The Test Cycle"))

        self.assertEqual(unicode(c), u"The Test Cycle")


    def test_get_absolute_url(self, http):
        c = self.resource_class()
        c.update_from_dict(testcycles.one(resourceIdentity=make_identity(id=2)))

        self.assertEqual(c.get_absolute_url(), "/cycle/2/")


    def test_approveallresults(self, http):
        http.request.return_value = response(testcycles.one(
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
        http.request.return_value = response(testcycles.one(
                resourceIdentity=make_identity(url="testcycles/1")))

        c = self.resource_class.get("testcycles/1")

        http.request.return_value = response(testcycles.one(
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
        http.request.return_value = response(testcycles.one(
                resourceIdentity=make_identity(url="testcycles/1")))

        c = self.resource_class.get("testcycles/1")

        http.request.return_value = response(testcycles.one(
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
        http.request.return_value = response(testcycles.one(
                resourceIdentity=make_identity(url="testcycles/1")))

        c = self.resource_class.get("testcycles/1")

        http.request.return_value = response(
            cvis.array(
                    {"categoryName": 1, "categoryValue": 159},
                    {"categoryName": 5, "categoryValue": 1}))

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



@patch("tcmui.core.api.userAgent")
class TestRunTest(BaseResourceTest, ResourceTestCase):
    def get_resource_class(self):
        from tcmui.testexecution.models import TestRun
        return TestRun


    def get_resource_list_class(self):
        from tcmui.testexecution.models import TestRunList
        return TestRunList


    def test_unicode(self, http):
        c = self.resource_class()
        c.update_from_dict(testruns.one(name="The Test Run"))

        self.assertEqual(unicode(c), u"The Test Run")


    def test_get_absolute_url(self, http):
        c = self.resource_class()
        c.update_from_dict(testruns.one(resourceIdentity=make_identity(id=2)))

        self.assertEqual(c.get_absolute_url(), "/run/2/")


    def test_approveallresults(self, http):
        http.request.return_value = response(testruns.one(
                resourceIdentity=make_identity(url="testruns/1")))

        c = self.resource_class.get("testruns/1")

        http.request.return_value = response(make_boolean(True))

        c.approveallresults()

        req = http.request.call_args[1]
        self.assertEqual(
            req["uri"],
            "http://fake.base/rest/testruns/1/approveallresults?_type=json")
        self.assertEqual(req["method"], "PUT")


    def test_clone(self, http):
        http.request.return_value = response(testruns.one(
                resourceIdentity=make_identity(url="testruns/1")))

        c = self.resource_class.get("testruns/1")

        http.request.return_value = response(testruns.one(
                name="Cloned Test Run",
                resourceIdentity=make_identity(id=2, url="testruns/2")))

        new = c.clone()

        self.assertEqual(new.name, "Cloned Test Run")
        self.assertIsInstance(new, self.resource_class)
        req = http.request.call_args[1]
        self.assertEqual(
            req["uri"], "http://fake.base/rest/testruns/1/clone?_type=json")
        self.assertEqual(req["method"], "POST")
        self.assertEqual(req["body"], "cloneAssignments=False")


    def test_clone_assignments(self, http):
        http.request.return_value = response(testruns.one(
                resourceIdentity=make_identity(url="testruns/1")))

        c = self.resource_class.get("testruns/1")

        http.request.return_value = response(testruns.one(
                name="Cloned Test Cycle",
                resourceIdentity=make_identity(id=2, url="testruns/2")))

        new = c.clone(assignments=True)

        self.assertEqual(new.name, "Cloned Test Cycle")
        self.assertIsInstance(new, self.resource_class)
        req = http.request.call_args[1]
        self.assertEqual(
            req["uri"], "http://fake.base/rest/testruns/1/clone?_type=json")
        self.assertEqual(req["method"], "POST")
        self.assertEqual(req["body"], "cloneAssignments=True")


    def test_resultsummary(self, http):
        http.request.return_value = response(testruns.one(
                resourceIdentity=make_identity(url="testruns/1")))

        c = self.resource_class.get("testruns/1")

        http.request.return_value = response(
            cvis.array(
                    {"categoryName": 1, "categoryValue": 159},
                    {"categoryName": 5, "categoryValue": 1}))

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



@patch("tcmui.core.api.userAgent")
class TestRunIncludedTestCaseTest(BaseResourceTest, ResourceTestCase):
    def get_resource_class(self):
        from tcmui.testexecution.models import TestRunIncludedTestCase
        return TestRunIncludedTestCase


    def get_resource_list_class(self):
        from tcmui.testexecution.models import TestRunIncludedTestCaseList
        return TestRunIncludedTestCaseList


    def test_resultsummary(self, http):
        http.request.return_value = response(testrunitcs.one(
                resourceIdentity=make_identity(url="testruns/1")))

        c = self.resource_class.get("testruns/1")
        c.deliver()

        # set up responses for both results list and result status static data
        def request(*args, **kwargs):
            uri = kwargs["uri"]
            if "/results" in uri:
                return response(
                    testresults.searchresult(
                        {"testRunResultStatusId": 1},
                        {"testRunResultStatusId": 1},
                        {"testRunResultStatusId": 2},
                        {"testRunResultStatusId": 2},
                        {"testRunResultStatusId": 2},
                        {"testRunResultStatusId": 5},
                        ))
            return response(
                codevalues.array(
                    {"description": "PENDING", "id": 1},
                    {"description": "PASSED", "id": 2},
                    {"description": "FAILED", "id": 3},
                    {"description": "BLOCKED", "id": 4},
                    {"description": "STARTED", "id": 5},
                    {"description": "INVALIDATED", "id": 6},
                    ))

        http.request.side_effect = request

        self.assertEqual(
            c.resultsummary(),
            {
                "BLOCKED": 0,
                "FAILED": 0,
                "INVALIDATED": 0,
                "PASSED": 3,
                "PENDING": 2,
                "STARTED": 1,
                })
