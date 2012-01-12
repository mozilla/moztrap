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
Tests for ``HasEnvironmentsModel``.

"""
from django.test import TestCase

from cc.environments.models import HasEnvironmentsModel



class HasEnvironmentsModelTest(TestCase):
    """Tests for HasEnvironmentsModel base class."""
    def test_parent(self):
        """parent property is None in base class."""
        t = HasEnvironmentsModel()
        self.assertIsNone(t.parent)


    def test_cascade_envs_to(self):
        """cascade_envs_to returns empty dict in base class."""
        self.assertEqual(HasEnvironmentsModel.cascade_envs_to([], True), {})
