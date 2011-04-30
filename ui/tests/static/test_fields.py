from unittest2 import TestCase

from flufl.enum import Enum



class SomeStatus(Enum):
    DRAFT = 1
    ACTIVE = 2



class StatusValueTest(TestCase):
    def _make(self, val):
        from tcmui.static.fields import StatusValue
        return StatusValue(val)


    def test_true(self):
        self.assertIs(self._make(SomeStatus.DRAFT).DRAFT, True)


    def test_false(self):
        self.assertIs(self._make(SomeStatus.DRAFT).ACTIVE, False)


    def test_error(self):
        with self.assertRaises(AttributeError):
            self._make(SomeStatus.DRAFT).BLAH


    def test_repr(self):
        self.assertEqual(
            repr(self._make(SomeStatus.DRAFT)),
            "StatusValue(<EnumValue: SomeStatus.DRAFT [int=1]>)")


    def test_str(self):
        self.assertEqual(str(self._make(SomeStatus.DRAFT)), "Draft")


    def test_unicode(self):
        self.assertEqual(unicode(self._make(SomeStatus.DRAFT)), u"Draft")
