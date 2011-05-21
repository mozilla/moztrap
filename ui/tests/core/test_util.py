from mock import Mock
from unittest2 import TestCase



class TestUpdateQueryString(TestCase):
    @property
    def func(self):
        from tcmui.core.util import update_querystring
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



class TestAddToQueryString(TestCase):
    @property
    def func(self):
        from tcmui.core.util import add_to_querystring
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
        from tcmui.core.util import id_for_object
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



class TestLcFirst(TestCase):
    @property
    def func(self):
        from tcmui.core.util import lc_first
        return lc_first


    def test_lowers(self):
        self.assertEqual(self.func("SomeThing"), "someThing")

