# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-2012 Mozilla
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
Tests for Environment model.

"""
from django.test import TestCase

from .... import factories as F



class EnvironmentTest(TestCase):
    def test_unicode(self):
        """Unicode representation is concatenated element names."""
        e = F.EnvironmentFactory.create_full_set(
            {"OS": ["OS X"], "Language": ["English"]})[0]

        self.assertEqual(unicode(e), u"English, OS X")


    def test_iteration(self):
        """Iteration yields elements in category name order."""
        e = F.EnvironmentFactory.create_full_set(
            {"OS": ["OS X"], "Language": ["English"]})[0]

        self.assertEqual([el.name for el in e], [u"English", u"OS X"])
