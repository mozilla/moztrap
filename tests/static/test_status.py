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
