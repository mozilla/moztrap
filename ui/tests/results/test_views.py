from mock import patch

from ..core.builders import cvis
from ..environments.builders import environmentgroups
from ..products.builders import products
from ..responses import response, make_locator
from ..testcases.builders import testsuites, testcases, testcaseversions
from ..testexecution.builders import (
    testcycles, testruns, testrunitcs, testresults, assignments)
from ..utils import ViewTestCase, COMMON_RESPONSES
from ..users.builders import users


@patch("tcmui.core.api.userAgent")
class DefaultResultsViewTest(ViewTestCase):
    @property
    def view(self):
        from tcmui.results.views import home
        return home


    def test_redirect(self, http):
        res = self.get("/results/")

        self.assertEqual(res.status_code, 302)
        self.assertEqual(
            res["Location"], "/results/testcycles/")


class ListViewTests(object):
    builder = None

    list_class = None

    ctx_var = None


    def extra_responses(self):
        return {}


    def per_item_responses(self, item_id):
        return {}


    def list_item_data(self):
        return [{"name": "Thing 1"}, {"name": "Thing 2"}]


    def test_results_list_view(self, http):
        item_data = self.list_item_data()
        responses = {
            "http://fake.base/rest/%s?_type=json&pagenumber=1&pagesize=20&companyId=1" % self.list_class.default_url:
                response(self.builder.searchresult(*item_data)),
            "http://fake.base/rest/products/1?_type=json":
                response(products.one(name="A Product")),
            }
        responses.update(self.extra_responses())
        for i in range(len(item_data)):
            responses.update({
                    "http://fake.base/rest/%s/%s/environmentgroups?_type=json" % (self.builder.plural_name, str(i + 1)):
                        response(environmentgroups.array()),
                    })
            responses.update(self.per_item_responses(str(i + 1)))
        self.setup_responses(http, responses)

        res = self.get("/results/%s/" % self.builder.plural_name)
        res.render()

        self.assertEqual(res.status_code, 200)
        ctx = self.rendered["context"]
        self.assertIsInstance(ctx[self.ctx_var], self.list_class)
        self.assertEqual(len(ctx[self.ctx_var]), 2)

        # all the expected API URLs were hit
        self.assertEqual(
            set(responses.keys()),
            set(args[1]["uri"]
                for args in http.request.call_args_list).difference(
                # not concerned about common responses
                set(COMMON_RESPONSES.keys())))



@patch("tcmui.core.api.userAgent")
class TestCycleResultsViewTest(ViewTestCase, ListViewTests):
    builder = testcycles

    ctx_var = "cycles"


    def per_item_responses(self, item_id):
        return {
            "http://fake.base/rest/testcycles/%s/reports/coverage/resultstatus?_type=json" % item_id:
                response(cvis.array({"categoryName": 1, "categoryValue": 160})),
            "http://fake.base/rest/testcycles/%s/team/members?_type=json" % item_id:
                response(users.array())
            }


    @property
    def view(self):
        from tcmui.results.views import testcycles as view
        return view


    @property
    def list_class(self):
        from tcmui.testexecution.models import TestCycleList
        return TestCycleList



@patch("tcmui.core.api.userAgent")
class TestRunResultsViewTest(ViewTestCase, ListViewTests):
    builder = testruns

    ctx_var = "runs"


    def extra_responses(self):
        return {
            "http://fake.base/rest/testcycles/1?_type=json":
                response(testcycles.one(name="A Cycle"))
            }


    def per_item_responses(self, item_id):
        return {
            "http://fake.base/rest/testruns/%s/reports/coverage/resultstatus?_type=json" % item_id:
                response(cvis.array({"categoryName": 1, "categoryValue": 160})),
            "http://fake.base/rest/testruns/%s/team/members?_type=json" % item_id:
                response(users.array())
            }


    @property
    def view(self):
        from tcmui.results.views import testruns as view
        return view


    @property
    def list_class(self):
        from tcmui.testexecution.models import TestRunList
        return TestRunList



@patch("tcmui.core.api.userAgent")
class TestCaseResultsViewTest(ViewTestCase, ListViewTests):
    builder = testrunitcs

    ctx_var = "includedcases"


    def extra_responses(self):
        return {
            "http://fake.base/rest/testcases/versions/1?_type=json":
                response(testcaseversions.one()),
            "http://fake.base/rest/testcases/1?_type=json":
                response(testcases.one()),
            "http://fake.base/rest/testruns/1?_type=json":
                response(testruns.one()),
            "http://fake.base/rest/users/1?_type=json":
                response(users.one()),
            "http://fake.base/rest/testsuites/1?_type=json":
                response(testsuites.one()),
            # summary results for included test case
            "http://fake.base/rest/testruns/results?_type=json&testCaseVersionId=1&testRunId=1":
                response(testresults.searchresult({})),
            # summary results for test suite
            "http://fake.base/rest/testruns/results?_type=json&testSuiteId=1&testRunId=1":
                response(testresults.searchresult({})),
            }


    def per_item_responses(self, item_id):
        return {
            "http://fake.base/rest/includedtestcases/%s/assignments?_type=json" % item_id:
                response(assignments.array({}))
            }


    def list_item_data(self):
        data = super(TestCaseResultsViewTest, self).list_item_data()
        # give the first item a test suite
        data[0]["testSuiteId"] = 1
        data[0]["testSuiteLocator"] = make_locator(id=1, url="testsuites/1")
        return data


    @property
    def view(self):
        from tcmui.results.views import testcases as view
        return view


    @property
    def list_class(self):
        from tcmui.testexecution.models import TestRunIncludedTestCaseList
        return TestRunIncludedTestCaseList
