from mock import patch

from ..core.builders import cvis
from ..environments.builders import environmentgroups
from ..products.builders import products
from ..responses import response
from ..testexecution.builders import testcycles, testruns
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


    def test_list_view(self, http):
        responses = {
            "http://fake.base/rest/%s?_type=json&pagenumber=1&pagesize=20&companyId=1" % self.builder.plural_name:
                response(self.builder.searchresult(
                    {"name": "Thing 1"},
                    {"name": "Thing 2"},
                    )),
            "http://fake.base/rest/products/1?_type=json":
                response(products.one(name="A Product")),
            }
        responses.update(self.extra_responses())
        for i in range(2):
            responses.update({
                    "http://fake.base/rest/%s/%s/reports/coverage/resultstatus?_type=json" % (self.builder.plural_name, str(i + 1)):
                        response(
                        cvis.array({"categoryName": 1, "categoryValue": 160})),
                    "http://fake.base/rest/%s/%s/environmentgroups?_type=json" % (self.builder.plural_name, str(i + 1)):
                        response(environmentgroups.array()),
                    "http://fake.base/rest/%s/%s/team/members?_type=json" % (self.builder.plural_name, str(i + 1)):
                        response(users.array())
                    })
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


    @property
    def view(self):
        from tcmui.results.views import testruns as view
        return view


    @property
    def list_class(self):
        from tcmui.testexecution.models import TestRunList
        return TestRunList
