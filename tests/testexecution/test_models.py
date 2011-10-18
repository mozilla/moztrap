from mock import patch
from unittest2 import TestCase

from ..core.builders import cvis
from ..responses import make_identity, response, make_boolean
from ..testcases.builders import testsuites, testcaseversions
from ..utils import BaseResourceTest, ResourceTestCase, locmem_cache, Url
from .builders import testcycles, testruns, testrunitcs, testresults



class RoundPercentTest(TestCase):
    """
    These tests assert identity rather than equality, because we really want an
    integer here, and 1.0 == 1.

    """
    def func(self, val):
        from ccui.testexecution.models import round_percent
        return round_percent(val)


    def test_none(self):
        self.assertIs(self.func(None), 0)


    def test_zero(self):
        self.assertIs(self.func(0), 0)


    def test_empty_string(self):
        self.assertIs(self.func(""), 0)


    def test_zero_in_string(self):
        self.assertIs(self.func("0"), 0)


    def test_fraction_in_string(self):
        self.assertIs(self.func("0.625"), 1)


    def test_float(self):
        self.assertIs(self.func(0.625), 1)


    def test_99(self):
        """
        We don't ever want to see 100% unless it's really 100%.

        """
        self.assertIs(self.func(99.9), 99)


    def test_0(self):
        """
        We don't ever want to see 0% unless it's really 0%.

        """
        self.assertIs(self.func(0.01), 1)



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

        from ccui.testexecution.models import TestResult
        result = TestResult.get("testruns/results/1")
        result.deliver()

        starting_call_count = http.request.call_count

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
        # 4 requests: get summary (next one cached),
        #             start, finishsucceed, newsummary
        self.assertEqual(
            http.request.call_count - starting_call_count,
            4,
            http.request.call_args_list)



@patch("ccui.core.api.userAgent", spec=["request"])
class TestCycleTest(BaseResourceTest, ResultSummaryTest, ResourceTestCase):
    def get_resource_class(self):
        from ccui.testexecution.models import TestCycle
        return TestCycle


    def get_resource_list_class(self):
        from ccui.testexecution.models import TestCycleList
        return TestCycleList


    def get_one(self, http):
        http.request.return_value = response(testcycles.one(
                resourceIdentity=make_identity(url="testcycles/1")))

        obj = self.resource_class.get("testcycles/1")
        obj.deliver()

        return obj


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



@patch("ccui.core.api.userAgent")
class TestRunTest(BaseResourceTest, ResultSummaryTest, ResourceTestCase):
    def get_resource_class(self):
        from ccui.testexecution.models import TestRun
        return TestRun


    def get_resource_list_class(self):
        from ccui.testexecution.models import TestRunList
        return TestRunList


    def get_one(self, http):
        http.request.return_value = response(testruns.one(
                _url="testruns/1"))

        obj = self.resource_class.get("testruns/1")
        obj.deliver()

        return obj


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
        from ccui.testcases.models import TestSuite

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
        from ccui.testcases.models import TestSuite

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


    def test_removesuite(self, http):
        from ccui.testcases.models import TestSuite

        r = self.resource_class()
        r.update_from_dict(testruns.one(
                resourceIdentity=make_identity(id=2, url="testruns/2")))

        s = TestSuite()
        s.update_from_dict(testsuites.one(
                resourceIdentity=make_identity(id=3, url="testsuites/3")))

        http.request.return_value = response(
            testrunitcs.array(
                {
                    "resourceIdentity": make_identity(
                        id=1, url="testruns/includedtestcases/1", version=3)
                    }
                )
            )
        r.removesuite(s)

        reqs = [ca[1] for ca in http.request.call_args_list]
        self.assertEqual(
            [r["uri"] for r in reqs],
            ["http://fake.base/rest/testruns/includedtestcases?_type=json&testSuiteId=3&testRunId=2",
             "http://fake.base/rest/testruns/includedtestcases/1?_type=json"])
        self.assertEqual(
            [r["method"] for r in reqs],
            ["GET", "DELETE"])
        self.assertEqual(
            [r.get("body", None) for r in reqs],
            [None, "originalVersionId=3"])


    def test_removesuite_invalidates_cache(self, http):
        from ccui.testcases.models import TestSuite

        r = self.resource_class()
        r.update_from_dict(testruns.one())

        s = TestSuite()
        s.update_from_dict(testsuites.one())

        with locmem_cache():
            http.request.return_value = response(testsuites.array(s.api_data))
            suites1 = list(r.suites)

            http.request.return_value = response(testrunitcs.array({}))
            r.removesuite(s)

            http.request.return_value = response(testsuites.array())
            suites2 = list(r.suites)

        self.assertEqual(len(suites1), 1)
        self.assertEqual(len(suites2), 0)


    def test_addcase_invalidates_suitecache(self, http):
        from ccui.testcases.models import TestCaseVersion

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
        from ccui.testcases.models import TestCaseVersion

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


@patch("ccui.core.api.userAgent")
class TestRunIncludedTestCaseTest(
    BaseResourceTest, ResultSummaryTest, ResourceTestCase):
    def get_resource_class(self):
        from ccui.testexecution.models import TestRunIncludedTestCase
        return TestRunIncludedTestCase


    def get_resource_list_class(self):
        from ccui.testexecution.models import TestRunIncludedTestCaseList
        return TestRunIncludedTestCaseList


    def get_one(self, http):
        http.request.return_value = response(testrunitcs.one(
                _url="testruns/1/includedtestcases/1"))

        obj = self.resource_class.get("testruns/1/includedtestcases/1")
        obj.deliver()

        http.request.return_value = response(testruns.one(
                _url="testruns/1"))

        obj.testRun.deliver()

        return obj
