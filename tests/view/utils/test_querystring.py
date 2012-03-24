"""
Tests for querystring utilities.

"""
from tests import case



class TestUpdateQueryString(case.TestCase):
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
