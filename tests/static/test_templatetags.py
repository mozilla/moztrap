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
from flufl.enum import Enum
from unittest2 import TestCase



class SomeStatus(Enum):
    DRAFT = 1
    ACTIVE = 2



class StatusFilterTest(TestCase):
    def _status(self, status1, status2):
        from ccui.static.templatetags.staticdata import status

        return status(status1, status2)


    def test_true(self):
        self.assertIs(self._status(SomeStatus.DRAFT, SomeStatus.DRAFT), True)


    def test_false(self):
        self.assertIs(self._status(SomeStatus.DRAFT, SomeStatus.ACTIVE), False)



class StatusClassFilterTest(TestCase):
    def _class(self, status):
        from ccui.static.fields import StatusValue
        from ccui.static.templatetags.staticdata import status_class

        return status_class(StatusValue(status))


    def test_simple(self):
        self.assertEqual(self._class(SomeStatus.DRAFT), "draft")
