from unittest2 import TestCase

from mock import patch, Mock

from tcmui.static.fields import StaticData
from tcmui.static.templatetags.staticdata import status_class
from tcmui.util.enum import Enum



class TestStatus1(Enum):
    _staticdata_key = "TESTSTATUS1"

    DRAFT = 1
    ACTIVE = 2



class TestStatus2(Enum):
    _staticdata_key = "TESTSTATUS2"

    ACTIVE = 1
    INACTIVE = 2
    DISABLED = 3



STATUS_ENUMS_BY_KEY = {
    "TESTSTATUS1": TestStatus1,
    "TESTSTATUS2": TestStatus2
    }



STATUS_CLASSES = {
    TestStatus1: {
        "DRAFT": "draft",
        "ACTIVE": "active",
        },
    TestStatus2: {
        "ACTIVE": "active",
        "INACTIVE": "inactive",
        "DISABLED": "disabled"
        }
    }



class MockObject(object):
    def __init__(self, **kw):
        for k, v in kw.iteritems():
            m = Mock()
            m.id = v
            setattr(self, k, m)

        for a, f in self.fields.iteritems():
            f.attrname = a


class NoStaticDataFields(MockObject):
    fields = {"somethingElse": Mock()}


class OneStaticDataField(MockObject):
    fields = {"statusOne": StaticData("TESTSTATUS1")}



class TwoStaticDataFields(MockObject):
    fields = {
        "statusOne": StaticData("TESTSTATUS1"),
        "statusTwo": StaticData("TESTSTATUS2")
        }


@patch("tcmui.static.templatetags.staticdata.STATUS_CLASSES", STATUS_CLASSES)
@patch("tcmui.static.templatetags.staticdata.STATUS_ENUMS_BY_KEY",
       STATUS_ENUMS_BY_KEY)
class StatusClassFilterTest(TestCase):
    def test_unspecified_when_one(self):
        one = OneStaticDataField(statusOne=TestStatus1.DRAFT)

        self.assertEqual(status_class(one), "draft")


    def test_specified_when_one(self):
        one = OneStaticDataField(statusOne=TestStatus1.DRAFT)

        self.assertEqual(status_class(one, "statusOne"), "draft")


    def test_bad_attr(self):
        one = OneStaticDataField(statusOne=TestStatus1.DRAFT)

        with self.assertRaises(ValueError):
            status_class(one, "doesntexist")


    def test_no_staticdata_fields(self):
        nofields = NoStaticDataFields()

        with self.assertRaises(ValueError):
            status_class(nofields)


    def test_unspecified_when_multiple(self):
        two = TwoStaticDataFields(statusOne=TestStatus1.ACTIVE,
                                  statusTwo=TestStatus2.ACTIVE)

        with self.assertRaises(ValueError):
            status_class(two)


    def test_specified_when_multiple(self):
        two = TwoStaticDataFields(statusOne=TestStatus1.ACTIVE,
                                  statusTwo=TestStatus2.DISABLED)

        self.assertEqual(status_class(two, "statusTwo"), "disabled")


