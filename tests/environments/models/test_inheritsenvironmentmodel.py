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
Tests for ``InheritsEnvironmentsModel``.

"""
from django.test import TestCase



class InheritsEnvironmentsModelTest(TestCase):
    """Tests for InheritsEnvironmentsModel base class."""
    @property
    def InheritsEnvironmentsModel(self):
        from cc.environments.models import InheritsEnvironmentsModel
        return InheritsEnvironmentsModel


    def test_parent(self):
        """parent property is not implemented in base class."""
        t = self.InheritsEnvironmentsModel()
        with self.assertRaises(NotImplementedError):
            t.parent
