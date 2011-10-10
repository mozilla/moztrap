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
from unittest2 import TestCase
from mock import Mock



class Error(object):
    def __init__(self, response_error):
        self.response_error = response_error



class ErrorMessageAndFieldsTest(TestCase):
    def assert_results(self, obj, err, ret):
        from ccui.core.errors import error_message_and_fields
        self.assertEqual(error_message_and_fields(obj, Error(err)), ret)


    def test_simple(self):
        self.assert_results(
            object(), "duplicate.name",
            ("The name  is already in use.", ["name", "cases"]))


    def test_field_interpolation(self):
        m = Mock()
        m.name = "Some object"
        self.assert_results(
            m, "duplicate.name",
            ("The name Some object is already in use.", ["name", "cases"]))


    def test_name_interpolation(self):
        class TestSuite(object):
            def __unicode__(self):
                return "thinger"

        self.assert_results(
            TestSuite(), "changing.used.entity",
            ("thinger is in use elsewhere and cannot be modified.", []))


    def test_classname_lookup(self):
        class TestSuite(object):
            pass

        class TestRun(object):
            pass

        self.assert_results(
            TestSuite(), "activating.incomplete.entity",
            ("Test suite is empty; add some test cases.", []))

        self.assert_results(
            TestRun(), "activating.incomplete.entity",
            ("Activate or unlock parent test cycle first.", []))


    def test_bad_error_code(self):
        self.assert_results(
            object(), "some.wierd.error",
            ('Unknown conflict "some.wierd.error"; please correct and try again.',
             []))


class ErrorMessageTest(ErrorMessageAndFieldsTest):
    """
    ``error_message`` should always return the first element of the return
    value of ``error_message_and_fields``.

    """
    def assert_results(self, obj, err, ret):
        from ccui.core.errors import error_message
        self.assertEqual(error_message(obj, Error(err)), ret[0])
