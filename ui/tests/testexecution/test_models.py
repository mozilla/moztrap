from mock import patch

from ..core.builders import cvis
from ..responses import make_identity, response, make_boolean, make_locator
from ..testcases.builders import testsuites, testcaseversions
from ..utils import (
    BaseResourceTest, ResourceTestCase, setup_common_responses, locmem_cache,
    Url)
from .builders import testcycles, testruns, testrunitcs, testresults



class ResultSummaryTest(object):
    def get_one(self, http):
        raise NotImplementedError


    def test_resultsummary(self, http):
        c = self.get_one(http)

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


    def test_resultsummary_caching(self, http):
        """
        Test that result summaries are cached, and modifying a test result
        clears cached result summaries.

        """
        c = self.get_one(http)

        http.request.return_value = response(testresults.one(
                resourceIdentity=make_identity(url="testruns/results/1")))

        from tcmui.testexecution.models import TestResult
        result = TestResult.get("testruns/results/1")
        result.deliver()

        with locmem_cache():
            http.request.return_value = response(
                cvis.array({"categoryName": 1, "categoryValue": 160}))

            c.resultsummary()
            c.resultsummary()

            http.request.return_value = response(testresults.one(
                    resourceIdentity=make_identity(url="testruns/results/1")))

            result.start()
            result.finishsucceed()

            http.request.return_value = response(
                cvis.array(
                        {"categoryName": 1, "categoryValue": 159},
                        {"categoryName": 5, "categoryValue": 1}))

            newsummary = c.resultsummary()

        self.assertEqual(
            newsummary,
            {
                "BLOCKED": 0,
                "FAILED": 0,
                "INVALIDATED": 0,
                "PASSED": 0,
                "PENDING": 159,
                "STARTED": 1,
                })
        # 5 requests: get result, get summary (next one cached), start,
        # finishsucceed, newsummary
        self.assertEqual(http.request.call_count, 5)



@patch("tcmui.core.api.userAgent", spec=["request"])
class TestCycleTest(BaseResourceTest, ResultSummaryTest, ResourceTestCase):
    def get_resource_class(self):
        from tcmui.testexecution.models import TestCycle
        return TestCycle


    def get_resource_list_class(self):
        from tcmui.testexecution.models import TestCycleList
        return TestCycleList


    def get_one(self, http):
        http.request.return_value = response(testcycles.one(
                resourceIdentity=make_identity(url="testcycles/1")))

        return self.resource_class.get("testcycles/1")


    def test_unicode(self, http):
        c = self.resource_class()
        c.update_from_dict(testcycles.one(name="The Test Cycle"))

        self.assertEqual(unicode(c), u"The Test Cycle")


    def test_approveallresults(self, http):
        http.request.return_value = response(testcycles.one(
                resourceIdentity=make_identity(url="testcycles/1")))

        c = self.resource_class.get("testcycles/1")

        http.request.return_value = response(make_boolean(True))

        c.approveallresults()

        req = http.request.call_args[1]
        self.assertEqual(
            Url(req["uri"]),
            Url("http://fake.base/rest/testcycles/1/approveallresults?_type=json"))
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
            Url(req["uri"]),
            Url("http://fake.base/rest/testcycles/1/clone?_type=json"))
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
            Url(req["uri"]),
            Url("http://fake.base/rest/testcycles/1/clone?_type=json"))
        self.assertEqual(req["method"], "POST")
        self.assertEqual(req["body"], "cloneAssignments=True")



@patch("tcmui.core.api.userAgent")
class TestRunTest(BaseResourceTest, ResultSummaryTest, ResourceTestCase):
    def get_resource_class(self):
        from tcmui.testexecution.models import TestRun
        return TestRun


    def get_resource_list_class(self):
        from tcmui.testexecution.models import TestRunList
        return TestRunList


    def get_one(self, http):
        http.request.return_value = response(testruns.one(
                resourceIdentity=make_identity(url="testruns/1")))

        return self.resource_class.get("testruns/1")


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
            Url(req["uri"]),
            Url("http://fake.base/rest/testruns/1/approveallresults?_type=json"))
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
            Url(req["uri"]),
            Url("http://fake.base/rest/testruns/1/clone?_type=json"))
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
            Url(req["uri"]),
            Url("http://fake.base/rest/testruns/1/clone?_type=json"))
        self.assertEqual(req["method"], "POST")
        self.assertEqual(req["body"], "cloneAssignments=True")


    def test_addsuite(self, http):
        from tcmui.testcases.models import TestSuite

        r = self.resource_class()
        r.update_from_dict(testruns.one(
                resourceIdentity=make_identity(
                    id=1, url="testruns/1", version=2)))

        s = TestSuite()
        s.update_from_dict(testsuites.one())

        http.request.return_value = response(make_boolean(True))
        r.addsuite(s)

        req = http.request.call_args[1]
        self.assertEqual(
            Url(req["uri"]),
            Url("http://fake.base/rest/testruns/1/includedtestcases/testsuite/1/?_type=json"))
        self.assertEqual(req["method"], "POST")
        self.assertEqual(req["body"], "originalVersionId=2")



    def test_addsuite_invalidates_cache(self, http):
        from tcmui.testcases.models import TestSuite

        r = self.resource_class()
        r.update_from_dict(testruns.one())

        s = TestSuite()
        s.update_from_dict(testsuites.one())

        with locmem_cache():
            http.request.return_value = response(testsuites.array())
            suites1 = list(r.suites)

            http.request.return_value = response(make_boolean(True))
            r.addsuite(s)

            http.request.return_value = response(testsuites.array({}))
            suites2 = list(r.suites)

        self.assertEqual(len(suites1), 0)
        self.assertEqual(len(suites2), 1)


    def test_addcase_invalidates_suitecache(self, http):
        from tcmui.testcases.models import TestCaseVersion

        r = self.resource_class()
        r.update_from_dict(testruns.one())

        c = TestCaseVersion()
        c.update_from_dict(testcaseversions.one())

        with locmem_cache():
            http.request.return_value = response(testsuites.array())
            suites1 = list(r.suites)

            http.request.return_value = response(make_boolean(True))
            r.addcase(c)

            http.request.return_value = response(testsuites.array({}))
            suites2 = list(r.suites)

        self.assertEqual(len(suites1), 0)
        self.assertEqual(len(suites2), 1)


    def test_addcase_invalidates_includedcase_cache(self, http):
        from tcmui.testcases.models import TestCaseVersion

        r = self.resource_class()
        r.update_from_dict(testruns.one())

        c = TestCaseVersion()
        c.update_from_dict(testcaseversions.one())

        with locmem_cache():
            http.request.return_value = response(testrunitcs.array())
            cases1 = list(r.includedtestcases)

            http.request.return_value = response(make_boolean(True))
            r.addcase(c)

            http.request.return_value = response(testrunitcs.array({}))
            cases2 = list(r.includedtestcases)

        self.assertEqual(len(cases1), 0)
        self.assertEqual(len(cases2), 1)


@patch("tcmui.core.api.userAgent")
class TestRunIncludedTestCaseTest(BaseResourceTest, ResourceTestCase):
    def get_resource_class(self):
        from tcmui.testexecution.models import TestRunIncludedTestCase
        return TestRunIncludedTestCase


    def get_resource_list_class(self):
        from tcmui.testexecution.models import TestRunIncludedTestCaseList
        return TestRunIncludedTestCaseList


    def test_resultsummary(self, http):
        setup_common_responses(http, {
                "http://fake.base/rest/testruns/includedtestcases/1?_type=json":
                    response(testrunitcs.one()),

                "http://fake.base/rest/testruns/results?_type=json&testCaseVersionId=1&testRunId=1":
                    response(testresults.searchresult(
                        {"testRunResultStatusId": 1},
                        {"testRunResultStatusId": 1},
                        {"testRunResultStatusId": 2},
                        {"testRunResultStatusId": 2},
                        {"testRunResultStatusId": 2},
                        {"testRunResultStatusId": 5},
                        )),
            })


        c = self.resource_class.get("testruns/includedtestcases/1")

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


    def test_suite_resultsummary(self, http):
        setup_common_responses(http, {
                "http://fake.base/rest/testruns/includedtestcases/1?_type=json":
                    response(testrunitcs.one(
                        testSuiteId=1,
                        testSuiteLocator=make_locator(
                            id=1, url="testsuites/1"))),

                "http://fake.base/rest/testruns/results?_type=json&testSuiteId=1&testRunId=1": response(
                    testresults.searchresult(
                        {"testRunResultStatusId": 1},
                        {"testRunResultStatusId": 1},
                        {"testRunResultStatusId": 2},
                        {"testRunResultStatusId": 2},
                        {"testRunResultStatusId": 2},
                        {"testRunResultStatusId": 5},
                        )),
            })


        c = self.resource_class.get("testruns/includedtestcases/1")

        self.assertEqual(
            c.suite_resultsummary(),
            {
                "BLOCKED": 0,
                "FAILED": 0,
                "INVALIDATED": 0,
                "PASSED": 3,
                "PENDING": 2,
                "STARTED": 1,
                })


    def test_suite_resultsummary_no_suite(self, http):
        setup_common_responses(http, {
                "http://fake.base/rest/testruns/includedtestcases/1?_type=json":
                    response(testrunitcs.one()),
            })


        c = self.resource_class.get("testruns/includedtestcases/1")

        self.assertEqual(
            c.suite_resultsummary(),
            {
                "BLOCKED": 0,
                "FAILED": 0,
                "INVALIDATED": 0,
                "PASSED": 0,
                "PENDING": 0,
                "STARTED": 0,
                })
