from mock import Mock
from unittest2 import TestCase

from ..responses import make_identity
from ..utils import TestResourceTestCase


class TestUpdateQueryString(TestCase):
    @property
    def func(self):
        from ccui.core.util import update_querystring
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



class TestNarrowQueryString(TestCase):
    @property
    def func(self):
        from ccui.core.util import narrow_querystring
        return narrow_querystring


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
            "http://fake.base/?blah=__")


    def test_override_same(self):
        self.assertEqual(
            self.func("http://fake.base/?blah=yo", blah="yo"),
            "http://fake.base/?blah=yo")


    def test_basic_with_existing(self):
        self.assertEqual(
            self.func("http://fake.base/?arg=yo", blah="foo"),
            "http://fake.base/?blah=foo&arg=yo")


    def test_override_with_existing(self):
        self.assertEqual(
            self.func("http://fake.base/?arg=yo&blah=yo", blah="foo"),
            "http://fake.base/?blah=__&arg=yo")


    def test_override_multiple(self):
        self.assertEqual(
            self.func("http://fake.base/?blah=one&blah=two", blah="foo"),
            "http://fake.base/?blah=__")


    def test_override_with_empty_list(self):
        self.assertEqual(
            self.func("http://fake.base/?blah=one&blah=two", blah=[]),
            "http://fake.base/?blah=one&blah=two")


    def test_override_overlap(self):
        self.assertEqual(
            self.func("http://fake.base/?blah=one&blah=two", blah="one"),
            "http://fake.base/?blah=one")


    def test_override_multiple_overlap(self):
        self.assertEqual(
            self.func(
                "http://fake.base/?blah=one&blah=two&blah=three",
                blah=["one", "three"]),
            "http://fake.base/?blah=one&blah=three")


    def test_existing_multiple(self):
        self.assertEqual(
            self.func("http://fake.base/?blah=one&blah=two", arg="foo"),
            "http://fake.base/?blah=one&blah=two&arg=foo")



class TestAddToQueryString(TestCase):
    @property
    def func(self):
        from ccui.core.util import add_to_querystring
        return add_to_querystring


    def test_basic(self):
        self.assertEqual(
            self.func("http://fake.base/", blah="foo"),
            "http://fake.base/?blah=foo")


    def test_list(self):
        self.assertEqual(
            self.func("http://fake.base/", blah=["foo", "yo"]),
            "http://fake.base/?blah=foo&blah=yo")


    def test_augment(self):
        self.assertEqual(
            self.func("http://fake.base/?blah=yo", blah="foo"),
            "http://fake.base/?blah=yo&blah=foo")


    def test_augment_list(self):
        self.assertEqual(
            self.func("http://fake.base/?blah=yo", blah=["foo", "bar"]),
            "http://fake.base/?blah=yo&blah=foo&blah=bar")


    def test_basic_with_existing(self):
        self.assertEqual(
            self.func("http://fake.base/?arg=yo", blah="foo"),
            "http://fake.base/?blah=foo&arg=yo")


    def test_augment_with_existing(self):
        self.assertEqual(
            self.func("http://fake.base/?arg=yo&blah=yo", blah="foo"),
            "http://fake.base/?blah=yo&blah=foo&arg=yo")


    def test_augment_multiple(self):
        self.assertEqual(
            self.func("http://fake.base/?blah=one&blah=two", blah="foo"),
            "http://fake.base/?blah=one&blah=two&blah=foo")


    def test_existing_multiple(self):
        self.assertEqual(
            self.func("http://fake.base/?blah=one&blah=two", arg="foo"),
            "http://fake.base/?blah=one&blah=two&arg=foo")



class TestIdForObject(TestCase):
    @property
    def func(self):
        from ccui.core.util import id_for_object
        return id_for_object


    def test_integer(self):
        self.assertEqual(self.func(1), 1)


    def test_none(self):
        with self.assertRaises(ValueError):
            self.func(None)


    def test_string(self):
        with self.assertRaises(ValueError):
            self.func("blah")


    def test_identity_none(self):
        obj = Mock(spec=["identity"])
        obj.identity = None
        self.assertEqual(self.func(obj), None)


    def test_no_id(self):
        obj = Mock(spec=["identity"])
        obj.identity = {}
        with self.assertRaises(ValueError):
            self.func(obj)


    def test_with_id(self):
        obj = Mock(spec=["identity"])
        obj.identity = {"@id": 2}
        self.assertEqual(self.func(obj), 2)



class TestPrepForQuery(TestResourceTestCase):
    @property
    def func(self):
        from ccui.core.util import prep_for_query
        return prep_for_query


    def test_single_integer(self):
        self.assertEqual(self.func(1), "1")


    def test_multiple_integers(self):
        self.assertEqual(self.func([1, 2]), ["1", "2"])


    def test_single_string(self):
        self.assertEqual(self.func("foo"), "foo")


    def test_multiple_strings(self):
        self.assertEqual(self.func(["foo", "bar"]), ["foo", "bar"])


    def test_encode_callback(self):
        self.assertEqual(self.func("foo", lambda x: x + "bar"), "foobar")


    def test_encode_callback_multiple(self):
        self.assertEqual(
            self.func(["foo", "fu"], lambda x: x + "bar"), ["foobar", "fubar"])



class TestLcFirst(TestCase):
    @property
    def func(self):
        from ccui.core.util import lc_first
        return lc_first


    def test_lowers(self):
        self.assertEqual(self.func("SomeThing"), "someThing")

