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
Tests for Suite model.

"""
from django.core.exceptions import ValidationError

from tests import case



class SuiteTest(case.DBTestCase):
    def test_unicode(self):
        """Unicode representation is name of Suite."""
        self.assertEqual(unicode(self.F.SuiteFactory(name="Foo")), u"Foo")


    def test_clone_cases(self):
        """Cloning a suite clones its member SuiteCases."""
        sc = self.F.SuiteCaseFactory()

        new = sc.suite.clone()

        self.assertEqual(new.cases.get(), sc.case)


    def test_clone_sets_draft_state(self):
        """Clone of active suite is still draft."""
        s = self.F.SuiteFactory(status="active")

        new = s.clone()

        self.assertEqual(new.status, "draft")


    def test_unique_constraint(self):
        """Can't have two SuiteCases with same suite and case."""
        sc = self.F.SuiteCaseFactory.create()

        new = self.F.SuiteCaseFactory.build(
            case=sc.case, suite=sc.suite)

        with self.assertRaises(ValidationError):
            new.full_clean()


    def test_unique_constraint_doesnt_prevent_edit(self):
        """Unique constraint still allows saving an edited existing object."""
        sc = self.F.SuiteCaseFactory.create()

        sc.instruction = "new instruction"

        sc.full_clean()


    def test_unique_constraint_ignores_deleted(self):
        """Deleted suitecase doesn't prevent new with same suite and case."""
        sc = self.F.SuiteCaseFactory.create()
        sc.delete()

        self.F.SuiteCaseFactory.create(
            case=sc.case, suite=sc.suite)
