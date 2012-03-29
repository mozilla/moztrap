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


    def test_default_active(self):
        """New suite defaults to active state."""
        s = self.F.SuiteFactory()

        self.assertEqual(s.status, "active")


    def test_unique_constraint(self):
        """Can't have two SuiteCases with same suite and case."""
        sc = self.F.SuiteCaseFactory.create()

        new = self.F.SuiteCaseFactory.build(
            case=sc.case, suite=sc.suite)

        with self.assertRaises(ValidationError):
            new.full_clean()


    def test_unique_constraint_with_unset_case_and_suite(self):
        """Uniqueness checking doesn't blow up if suite/case unset."""
        new = self.model.SuiteCase()

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
