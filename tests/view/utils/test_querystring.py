# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-12 Mozilla
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
"""
Tests for querystring utilities.

"""
from django.utils.unittest import TestCase



class TestUpdateQueryString(TestCase):
    @property
    def func(self):
        from cc.view.utils.querystring import update_querystring
        return update_querystring


    def test_basic(self):
        self.assertEqual(
            self.func("http://fake.base/", blah="foo"),
            "http://fake.base/?blah=foo")


    def test_list(self):
        self.assertEqual(
            self.func("http://fake.base/", blah=["foo", "yo"]),
            "http://fake.base/?blah=foo&blah=yo")


    def test_override(self):
        self.assertEqual(
            self.func("http://fake.base/?blah=yo", blah="foo"),
            "http://fake.base/?blah=foo")


    def test_override_none(self):
        self.assertEqual(
            self.func("http://fake.base/?blah=yo", blah=None),
            "http://fake.base/")


    def test_basic_with_existing(self):
        self.assertEqual(
            self.func("http://fake.base/?arg=yo", blah="foo"),
            "http://fake.base/?blah=foo&arg=yo")


    def test_override_with_existing(self):
        self.assertEqual(
            self.func("http://fake.base/?arg=yo&blah=yo", blah="foo"),
            "http://fake.base/?blah=foo&arg=yo")


    def test_override_multiple(self):
        self.assertEqual(
            self.func("http://fake.base/?blah=one&blah=two", blah="foo"),
            "http://fake.base/?blah=foo")


    def test_existing_multiple(self):
        self.assertEqual(
            self.func("http://fake.base/?blah=one&blah=two", arg="foo"),
            "http://fake.base/?blah=one&blah=two&arg=foo")
