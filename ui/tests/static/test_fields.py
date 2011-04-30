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
