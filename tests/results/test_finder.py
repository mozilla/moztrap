# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
# 
# This file is part of Case Conductor.
# 
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
from mock import Mock, patch
from unittest2 import TestCase

from ..responses import response
from ..testcases.builders import testcases
from ..testexecution.builders import testrunitcs
from ..utils import setup_responses



class ResultsFinderTest(TestCase):
    @property
    def finder(self):
        from ccui.results.finder import ResultsFinder
        return ResultsFinder


    @property
    def itc(self):
        from ccui.testexecution.models import TestRunIncludedTestCase
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


    @patch("ccui.core.api.userAgent")
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
