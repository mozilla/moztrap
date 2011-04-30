from flufl.enum import Enum
from unittest2 import TestCase



class SomeStatus(Enum):
    DRAFT = 1
    ACTIVE = 2



class StatusFilterTest(TestCase):
    def _status(self, status1, status2):
        from tcmui.static.templatetags.staticdata import status

        return status(status1, status2)


    def test_true(self):
        self.assertIs(self._status(SomeStatus.DRAFT, SomeStatus.DRAFT), True)


    def test_false(self):
        self.assertIs(self._status(SomeStatus.DRAFT, SomeStatus.ACTIVE), False)



class StatusClassFilterTest(TestCase):
    def _class(self, status):
        from tcmui.static.fields import StatusValue
        from tcmui.static.templatetags.staticdata import status_class

        return status_class(StatusValue(status))


    def test_simple(self):
        self.assertEqual(self._class(SomeStatus.DRAFT), "draft")
