from mock import patch

from ..attachments.builders import attachments
from ..core.builders import cvis
from ..environments.builders import environmentgroups, environments
from ..products.builders import products
from ..relatedbugs.builders import relatedbugs
from ..responses import response, make_locator, make_identity
from ..testcases.builders import (
    testsuites, testcaseversions, testcasesteps)
from ..testexecution.builders import (
    testcycles, testruns, testrunitcs, testresults, assignments)
from ..utils import ViewTestCase, COMMON_RESPONSES, Url
from ..users.builders import users


@patch("ccui.core.api.userAgent")
class DefaultResultsViewTest(ViewTestCase):
    def test_redirect(self, http):
        self.setup_responses(http)
        res = self.app.get("/results/")

        self.assertEqual(res.status_int, 302)
        self.assertEqual(
            res.headers["location"],
            "http://localhost:80/results/testcycles/?openfinder=1&status=2")


class ListViewTests(object):
    builder = None

    list_class = None

    ctx_var = None

    ctx_var_single = None

    @property
    def url(self):
        return "/results/%s/" % self.builder.plural_name


    def ajax_detail_url(self, item_id):
        return "%s_detail/%s/" % (self.url, item_id)


    def extra_responses(self):
        return {}


    def per_item_responses(self, item_id):
        return {}


    def per_item_ajax_detail_responses(self, item_id):
        return {}


    def list_item_data(self):
        return [
            {
                "name": "Thing 1",
                "resourceIdentity": make_identity(
                    id=1, url="%s/1/" % self.list_class.default_url)
                },
            {
                "name": "Thing 2",
                "resourceIdentity": make_identity(
                    id=2, url="%s/2/" % self.list_class.default_url)
                },
            ]


    item_data_check_attr = "name"


    def extra_querystring(self):
        return ""


    def test_results_list_view(self, http):
        item_data = self.list_item_data()
        responses = {
            "http://fake.base/rest/%s?_type=json&pagenumber=1&pagesize=20&companyId=1%s" % (self.list_class.default_url, self.extra_querystring()):
                response(self.builder.searchresult(*item_data)),
            # finder
            "http://fake.base/rest/products?sortfield=name&sortdirection=asc&_type=json&companyId=1":
                response(products.searchresult({})),
            }
        responses.update(self.extra_responses())
        for i in range(len(item_data)):
            responses.update({
                    })
            responses.update(self.per_item_responses(str(i + 1)))
        self.setup_responses(http, responses)

        res = self.app.get(self.url)

        self.assertEqual(res.status_int, 200)
        ctx = self.rendered["context"]
        self.assertIsInstance(ctx[self.ctx_var], self.list_class)
        self.assertEqual(len(ctx[self.ctx_var]), 2)

        # all the expected API URLs were hit
        self.assertEqual(
            set([Url(k) for k in responses.iterkeys()]),
            set(Url(args[1]["uri"])
                for args in http.request.call_args_list).difference(
                # not concerned about common responses
                set([Url(k) for k in COMMON_RESPONSES.iterkeys()])))


    def test_ajax_detail_view(self, http):
        item_data = self.list_item_data()[0]
        responses = {
            "http://fake.base/rest/%s/1?_type=json" % self.list_class.default_url:
                response(self.builder.one(**item_data))
            }
        responses.update(self.per_item_ajax_detail_responses("1"))
        self.setup_responses(http, responses)

        res = self.app.get(self.ajax_detail_url("1"))

        self.assertEqual(res.status_int, 200)
        ctx = self.rendered["context"]
        obj = ctx[self.ctx_var_single]
        self.assertIsInstance(obj, self.list_class.entryclass)

        if self.item_data_check_attr.endswith("Id"):
            attr = getattr(obj, self.item_data_check_attr[:-2])
            attr = attr.id
        else:
            attr = getattr(obj, self.item_data_check_attr)
        self.assertEqual(str(attr), str(item_data[self.item_data_check_attr]))

        # all the expected API URLs were hit
        self.assertEqual(
            set([Url(k) for k in responses.iterkeys()]),
            set(Url(args[1]["uri"])
                for args in http.request.call_args_list).difference(
                # not concerned about common responses
                set([Url(k) for k in COMMON_RESPONSES.iterkeys()])))



@patch("ccui.core.api.userAgent")
class TestCycleResultsViewTest(ViewTestCase, ListViewTests):
    builder = testcycles

    ctx_var = "cycles"

    ctx_var_single = "cycle"


    def extra_querystring(self):
        # ACTIVE/LOCKED/CLOSED, sorted by product
        return "&testCycleStatusId=2&testCycleStatusId=3&testCycleStatusId=4&sortfield=productId&sortdirection=asc"


    def per_item_responses(self, item_id):
        return {
            "http://fake.base/rest/testcycles/%s/reports/coverage/resultstatus?_type=json" % item_id:
                response(cvis.array({"categoryName": 1, "categoryValue": 160})),
            }


    def per_item_ajax_detail_responses(self, item_id):
        return {
            "http://fake.base/rest/testcycles/%s/team/members?_type=json" % item_id:
                response(users.array()),
            "http://fake.base/rest/testcycles/%s/environmentgroups?_type=json" % item_id:
                response(environmentgroups.array()),
            }


    @property
    def list_class(self):
        from ccui.testexecution.models import TestCycleList
        return TestCycleList



@patch("ccui.core.api.userAgent")
class TestRunResultsViewTest(ViewTestCase, ListViewTests):
    builder = testruns

    ctx_var = "runs"

    ctx_var_single = "run"

    def extra_querystring(self):
        # ACTIVE, LOCKED, and CLOSED status (not DRAFT or DISCARDED)
        return "&testRunStatusId=2&testRunStatusId=3&testRunStatusId=4"


    def extra_responses(self):
        return {
            "http://fake.base/rest/testcycles?testCycleStatusId=2&testCycleStatusId=3&_type=json":
                response(testcycles.searchresult({})),
            }


    def per_item_responses(self, item_id):
        return {
            "http://fake.base/rest/testcycles/1/reports/coverage/resultstatus?_type=json&testRunId=%s" % item_id:
                response(cvis.array({"categoryName": 1, "categoryValue": 160})),
            }


    def per_item_ajax_detail_responses(self, item_id):
        return {
            "http://fake.base/rest/testruns/%s/team/members?_type=json" % item_id:
                response(users.array()),
            "http://fake.base/rest/testruns/%s/environmentgroups?_type=json" % item_id:
                response(environmentgroups.array()),
            }


    @property
    def list_class(self):
        from ccui.testexecution.models import TestRunList
        return TestRunList



@patch("ccui.core.api.userAgent")
class TestCaseResultsViewTest(ViewTestCase, ListViewTests):
    builder = testrunitcs

    ctx_var = "includedcases"

    ctx_var_single = "itc"

    url = "/results/testcases/"


    def ajax_detail_url(self, item_id):
        return "%s_detail/%s/" % (self.url, item_id)


    def extra_responses(self):
        return {
            # suites for filtering on
            "http://fake.base/rest/testsuites/?_type=json":
                response(testsuites.searchresult({})),
            # runs for filtering on
            "http://fake.base/rest/testruns?_type=json&testRunStatusId=2&testRunStatusId=3":
                response(testruns.searchresult({})),
            }


    def per_item_responses(self, item_id):
        return {
            "http://fake.base/rest/testcases/versions/%s?_type=json" % item_id:
                response(testcaseversions.one()),
            }


    def per_item_ajax_detail_responses(self, item_id):
        return {
            "http://fake.base/rest/testcases/versions/%s?_type=json" % item_id:
                response(testcaseversions.one()),
            "http://fake.base/rest/testruns/includedtestcases/%s/assignments?_type=json" % item_id:
                response(assignments.array({})),
            "http://fake.base/rest/testruns/includedtestcases/%s/environmentgroups?_type=json" % item_id:
                response(environmentgroups.array()),
            "http://fake.base/rest/testcases/versions/%s/steps?_type=json" % item_id:
                response(testcasesteps.array({})),
            "http://fake.base/rest/testcases/versions/%s/attachments?_type=json" % item_id:
                response(attachments.array({})),
            "http://fake.base/rest/testcases/1/relatedbugs?_type=json":
                response(relatedbugs.array({})),
            }


    def list_item_data(self):
        return [
            {
                "testCaseId": 1,
                "testCaseLocator": make_locator(
                    id=1, url="testcases/1", name="The Test Case"),
                "testCaseVersionId": 1,
                "testCaseVersionLocator": make_locator(
                    id=1,
                    url="testcases/versions/1",
                    name="The Test Case Version"),
                "testSuiteId": 1,
                "testSuiteLocator": make_locator(
                    id=1, url="testsuites/1", name="The Test Suite"),
                "resourceIdentity": make_identity(
                    id=1, url="%s/1/" % self.list_class.default_url)
                },
            {
                "testCaseId": 2,
                "testCaseLocator": make_locator(
                    id=2, url="testcases/1", name="The Test Case"),
                "testCaseVersionId": 2,
                "testCaseVersionLocator": make_locator(
                    id=2,
                    url="testcases/versions/2",
                    name="The Test Case Version"),
                "resourceIdentity": make_identity(
                    id=2, url="%s/2/" % self.list_class.default_url)
                },
            ]


    item_data_check_attr = "testCaseVersionId"


    @property
    def list_class(self):
        from ccui.testexecution.models import TestRunIncludedTestCaseList
        return TestRunIncludedTestCaseList



@patch("ccui.core.api.userAgent")
class TestResultsViewTest(ViewTestCase, ListViewTests):
    builder = testresults

    ctx_var = "results"

    url = "/results/testcase/1/"


    @property
    def list_class(self):
        from ccui.testexecution.models import TestResultList
        return TestResultList


    def extra_querystring(self):
        return "&testCaseVersionId=1&testRunId=1&sortfield=testRunResultStatusId&sortdirection=desc"


    def extra_responses(self):
        return {
            "http://fake.base/rest/testruns/includedtestcases/1?_type=json":
                response(testrunitcs.one()),
            "http://fake.base/rest/testcases/versions/1?_type=json":
                response(testcaseversions.one(
                    resourceIdentity=make_identity(
                        id=1, url="testcases/versions/1"))),
            # calculating summary results for included-case header
            "http://fake.base/rest/testruns/results?_type=json&testCaseVersionId=1&testRunId=1":
                response(testresults.searchresult({})),
            "http://fake.base/rest/testcases/versions/1/steps?_type=json":
                response(testcasesteps.array({})),
            "http://fake.base/rest/testcases/versions/1/attachments?_type=json":
                response(attachments.array({})),
            "http://fake.base/rest/testcases/1/relatedbugs?_type=json":
                response(relatedbugs.array({})),
            }


    def per_item_responses(self, item_id):
        return {
            "http://fake.base/rest/testruns/results/%s/environments?_type=json" % item_id:
                response(environments.array({})),
            }


    def get(self, uri, *args, **kwargs):
        req = self.factory.get(uri, *args, **kwargs)
        req.auth = self.auth
        from ccui.core.api import url_final_integer
        return self.view(req, url_final_integer(uri))


    def test_ajax_detail_view(self, http):
        pass
