from mock import patch

from ..responses import response
from ..testexecution.builders import testcycles
from ..utils import ViewTestCase



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
        self.setup_responses(http, {
                "http://fake.base/rest/testcycles?_type=json&companyId=1":
                    response(testcycles.searchresult(
                        {"name": "Cycle 1"},
                        {"name": "Cycle 2"},
                        {"name": "Cycle 3"},
                        ))
                })

        res = self.get("/results/testcycles/")
        res.render()

        self.assertEqual(res.status_code, 200)
        ctx = self.rendered["context"]
        from tcmui.testexecution.models import TestCycleList
        self.assertIsInstance(ctx["cycles"], TestCycleList)
        self.assertEqual(len(ctx["cycles"]), 3)
