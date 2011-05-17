from mock import patch

from ..core.builders import cvis
from ..environments.builders import environmentgroups
from ..products.builders import products
from ..responses import response
from ..testexecution.builders import testcycles
from ..utils import ViewTestCase
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



@patch("tcmui.core.api.userAgent")
class TestCycleResultsViewTest(ViewTestCase):
    @property
    def view(self):
        from tcmui.results.views import testcycles as view
        return view


    def test_basic(self, http):
        responses = {
            "http://fake.base/rest/testcycles?_type=json&pagenumber=1&pagesize=20&companyId=1":
                response(testcycles.searchresult(
                    {"name": "Cycle 1"},
                    {"name": "Cycle 2"},
                    )),
            "http://fake.base/rest/products/1?_type=json":
                response(products.one(name="A Product")),
            }
        for i in range(2):
            responses.update({
                    "http://fake.base/rest/testcycles/%s/reports/coverage/resultstatus?_type=json" % str(i + 1):
                        response(
                        cvis.array({"categoryName": 1, "categoryValue": 160})),
                    "http://fake.base/rest/testcycles/%s/environmentgroups?_type=json" % str(i + 1):
                        response(environmentgroups.array()),
                    "http://fake.base/rest/testcycles/%s/team/members?_type=json" % str(i + 1):
                        response(users.array())
                    })
        self.setup_responses(http, responses)

        res = self.get("/results/testcycles/")
        res.render()

        self.assertEqual(res.status_code, 200)
        ctx = self.rendered["context"]
        from tcmui.testexecution.models import TestCycleList
        self.assertIsInstance(ctx["cycles"], TestCycleList)
        self.assertEqual(len(ctx["cycles"]), 2)
