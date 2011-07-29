from mock import Mock, patch
from unittest2 import TestCase

from ..responses import response
from ..testcases.builders import testcases
from ..testexecution.builders import testrunitcs
from ..utils import setup_responses



class ResultsFinderTest(TestCase):
    @property
    def finder(self):
        from tcmui.results.finder import ResultsFinder
        return ResultsFinder


    @property
    def itc(self):
        from tcmui.testexecution.models import TestRunIncludedTestCase
        return TestRunIncludedTestCase


    def test_goto_url(self):
        f = self.finder()

        obj = Mock()
        obj._spec_class = self.itc
        obj.id = 7

        self.assertEqual(f.goto_url(obj), "/results/testcase/7/")


    def test_child_column_for_obj(self):
        f = self.finder()

        obj = Mock()
        obj._spec_class = self.itc

        self.assertEqual(f.child_column_for_obj(obj), "results")


    @patch("tcmui.core.api.userAgent")
    def test_objects(self, http):
        f = self.finder()

        setup_responses(
            http,
            {
                "http://fake.base/rest/testruns/includedtestcases?sortfield=name&sortdirection=asc&_type=json&companyId=1":
                    response(testrunitcs.searchresult({})),
                }
            )

        objects = f.objects("cases")

        self.assertEqual(objects[0].name, "The Test Case")
