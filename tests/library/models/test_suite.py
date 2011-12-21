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
Tests for Suite model.

"""
from django.test import TestCase

from ..builders import create_suite, create_suitecase



class SuiteTest(TestCase):
    @property
    def Suite(self):
        from cc.library.models import Suite
        return Suite


    def test_unicode(self):
        """Unicode representation is name of Suite."""
        self.assertEqual(unicode(create_suite(name="Foo")), u"Foo")


    def test_clone_cases(self):
        """Cloning a suite clones its member SuiteCases."""
        sc = create_suitecase()

        new = sc.suite.clone()

        self.assertEqual(new.cases.get(), sc.case)
