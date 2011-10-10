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
from unittest2 import TestCase



class StatusEnumTest(TestCase):
    """
    This is just a sanity double-check to ensure we don't mistakenly change our
    enums without verifying that the platform static values have changed
    correspondingly.

    """
    def test_testcyclestatus(self):
        from ccui.static.status import TestCycleStatus
        self.assertEqual(
            TestCycleStatus._enums,
            {1: 'DRAFT', 2: 'ACTIVE', 3: 'LOCKED', 4: 'CLOSED', 5: 'DISCARDED'})


    def test_testrunstatus(self):
        from ccui.static.status import TestRunStatus
        self.assertEqual(
            TestRunStatus._enums,
            {1: 'DRAFT', 2: 'ACTIVE', 3: 'LOCKED', 4: 'CLOSED', 5: 'DISCARDED'})


    def test_testcasestatus(self):
        from ccui.static.status import TestCaseStatus
        self.assertEqual(
            TestCaseStatus._enums,
            {1: 'DRAFT', 2: 'ACTIVE', 3: 'LOCKED', 4: 'CLOSED', 5: 'DISCARDED'})


    def test_testsuitestatus(self):
        from ccui.static.status import TestSuiteStatus
        self.assertEqual(
            TestSuiteStatus._enums,
            {1: 'DRAFT', 2: 'ACTIVE', 3: 'LOCKED', 4: 'CLOSED', 5: 'DISCARDED'})


    def test_userstatus(self):
        from ccui.static.status import UserStatus
        self.assertEqual(
            UserStatus._enums, {1: 'ACTIVE', 2: 'INACTIVE', 3: 'DISABLED'})


    def test_testresultstatus(self):
        from ccui.static.status import TestResultStatus
        self.assertEqual(
            TestResultStatus._enums,
            {
                1: 'PENDING',
                2: 'PASSED',
                3: 'FAILED',
                4: 'BLOCKED',
                5: 'STARTED',
                6: 'INVALIDATED'})


    def test_approvalstatus(self):
        from ccui.static.status import ApprovalStatus
        self.assertEqual(
            ApprovalStatus._enums, {1: 'PENDING', 2: 'APPROVED', 3: 'REJECTED'})
