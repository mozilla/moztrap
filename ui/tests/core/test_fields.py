import datetime

from unittest2 import TestCase



class BaseFieldTests(TestCase):
    @property
    def field_cls(self):
        from tcmui.core.fields import Field
        return Field


    @property
    def cls(self):
        class Bag(object):
            def __init__(self, **kw):
                for k, v in kw.items():
                    setattr(self, k, v)

        return Bag


    def field_and_cls(self, *args, **kwargs):
        f = self.field_cls(*(self.prepend_args + args), **kwargs)
        cls = self.cls
        f.install("attname", cls)
        return f, cls


    def field(self, *args, **kwargs):
        return self.field_and_cls(*args, **kwargs)[0]


    @property
    def prepend_args(self):
        return ()


    def test_default_names(self):
        f = self.field()

        self.assertEqual(f.api_name, "ns1.attname")
        self.assertEqual(f.api_filter_name, "attname")
        self.assertEqual(f.api_submit_name, "attname")


    def test_set_api_name(self):
        f = self.field(api_name="apiname")

        self.assertEqual(f.api_name, "ns1.apiname")
        self.assertEqual(f.api_filter_name, "apiname")
        self.assertEqual(f.api_submit_name, "apiname")


    def test_set_api_submit_name(self):
        f = self.field(api_submit_name="apisubmitname")

        self.assertEqual(f.api_name, "ns1.attname")
        self.assertEqual(f.api_filter_name, "attname")
        self.assertEqual(f.api_submit_name, "apisubmitname")


    def test_set_api_name_and_api_submit_name(self):
        f = self.field(api_name="apiname", api_submit_name="apisubmitname")

        self.assertEqual(f.api_name, "ns1.apiname")
        self.assertEqual(f.api_filter_name, "apiname")
        self.assertEqual(f.api_submit_name, "apisubmitname")


    def test_decode_nil(self):
        f = self.field()
        self.assertEqual(f.decode({"@xsi.nil": "true"}), None)


    def test_decode(self):
        f = self.field()
        self.assertEqual(f.decode("blah"), "blah")


    def test_encode(self):
        f = self.field()
        self.assertEqual(f.encode("blah"), "blah")


    def test_no_submit_data(self):
        f, cls = self.field_and_cls(api_submit_name=False)
        self.assertEqual(f.submit_data(cls()), {})


    def test_submit_none(self):
        f, cls = self.field_and_cls()
        self.assertEqual(f.submit_data(cls(attname=None)), {})


    def test_submit(self):
        f, cls = self.field_and_cls()
        self.assertEqual(
            f.submit_data(cls(attname="blah")), {"attname": "blah"})


    def test_non_filterable(self):
        class NonFilterableField(self.field_cls):
            api_filter_name = False

        f = NonFilterableField(*self.prepend_args)
        f.install("attname", self.cls)

        self.assertEqual(f.api_filter_name, False)



class FieldTest(BaseFieldTests):
    def test_encode_returns_dict(self):
        class ComplexField(self.field_cls):
            def encode(self, value):
                return {
                    "%s_part1" % self.api_submit_name: value[0],
                    "%s_part2" % self.api_submit_name: value[1],
                    }

        f = ComplexField()
        cls = self.cls
        f.install("attname", cls)

        self.assertEqual(
            f.submit_data(cls(attname=["one", "two"])),
            {"attname_part1": "one", "attname_part2": "two"})


    def test_submit_dict(self):
        f, cls = self.field_and_cls()
        self.assertEqual(
            f.submit_data(cls(attname={"a": 1})), {"attname": {"a": 1}})



class DateFieldTest(BaseFieldTests):
    @property
    def field_cls(self):
        from tcmui.core.fields import Date
        return Date


    def test_decode(self):
        f = self.field_cls()

        self.assertEqual(
            f.decode("2011-04-28T00:46:00Z"), datetime.date(2011, 4, 28))


    def test_encode(self):
        f = self.field()

        self.assertEqual(
            f.encode(datetime.date(2011, 4, 28)), "2011/04/28")


    def test_submit(self):
        f, cls = self.field_and_cls()

        self.assertEqual(
            f.submit_data(cls(attname=datetime.date(2011, 4, 28))),
            {"attname": "2011/04/28"})



class LocatorFieldTest(BaseFieldTests):
    @property
    def field_cls(self):
        from tcmui.core.fields import Locator
        return Locator


    @property
    def target_cls(self):
        return self.cls


    def field_cls_and_target(self, *args, **kwargs):
        target = self.target_cls
        f = self.field_cls(target, *args, **kwargs)
        cls = self.cls
        f.install("attname", cls)
        return f, cls, target


    @property
    def prepend_args(self):
        return (self.target_cls,)


    def field_and_cls(self, *args, **kwargs):
        return self.field_cls_and_target(*args, **kwargs)[:2]


    def test_default_names(self):
        f = self.field()

        self.assertEqual(f.api_name, "ns1.attnameLocator")
        self.assertEqual(f.api_filter_name, "attnameId")
        self.assertEqual(f.api_submit_name, "attnameId")


    def test_set_api_name(self):
        f = self.field(api_name="apiname")

        self.assertEqual(f.api_name, "ns1.apiname")
        self.assertEqual(f.api_filter_name, "apinameId")
        self.assertEqual(f.api_submit_name, "apinameId")


    def test_set_api_submit_name(self):
        f = self.field(api_submit_name="apisubmitname")

        self.assertEqual(f.api_name, "ns1.attnameLocator")
        self.assertEqual(f.api_filter_name, "attnameId")
        self.assertEqual(f.api_submit_name, "apisubmitname")


    def test_set_api_name_and_api_submit_name(self):
        f = self.field(api_name="apiname", api_submit_name="apisubmitname")

        self.assertEqual(f.api_name, "ns1.apiname")
        self.assertEqual(f.api_filter_name, "apinameId")
        self.assertEqual(f.api_submit_name, "apisubmitname")


    def test_encode(self):
        f, cls, target_cls = self.field_cls_and_target()
        self.assertEqual(f.encode(target_cls(identity={"@id": 1})), 1)


    def test_submit(self):
        f, cls, target_cls = self.field_cls_and_target()
        self.assertEqual(
            f.submit_data(cls(attname=target_cls(identity={"@id": 1}))),
            {"attnameId": 1})
