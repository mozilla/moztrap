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
"""
Tests for Cycle model.

"""
import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from ..builders import create_cycle



class CycleTest(TestCase):
    @property
    def Cycle(self):
        from cc.execution.models import Cycle
        return Cycle


    def test_unicode(self):
        c = self.Cycle(name="Firefox 10")

        self.assertEqual(unicode(c), u"Firefox 10")


    def test_invalid_dates(self):
        """Cycle validates that start date is not after end date."""
        today = datetime.date(2011, 12, 13)
        c = create_cycle(
            start=today,
            end=today-datetime.timedelta(days=1))

        with self.assertRaises(ValidationError):
            c.full_clean()


    def test_valid_dates(self):
        """Cycle validation allows start date before or same as end date."""
        today = datetime.date(2011, 12, 13)
        c = create_cycle(
            start=today,
            end=today+datetime.timedelta(days=1))

        c.full_clean()
