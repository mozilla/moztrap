# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-12 Mozilla
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
"""Tests for suite/case importer."""

from unittest import TestCase

from tests import case

from cc.model.library.importer import ImportResult



class ImporterTestBase(object):
    """Common base class for importer tests."""
    def setUp(self):
        """Setup for importer tests; create a product version."""
        self.pv = self.F.ProductVersionFactory.create()


    def import_data(self, case_data):
        """Instantiate ``Importer``, call ``import_data`` and return result."""
        from cc.model.library.importer import Importer
        return Importer().import_data(self.pv, case_data)


class ImporterTest(ImporterTestBase, case.DBTestCase):
    """Tests for ``Importer``."""
    def test_create_caseversion(self):
        """Successful import creates a caseversion with expected values."""
        self.import_data(
            {
                "cases": [
                    {
                        "name": "Foo",
                        "steps": [{"instruction": "do this"}],
                        }
                    ]
                }
            )

        cv = self.model.CaseVersion.objects.get()
        self.assertEqual(cv.name, "Foo")
        self.assertEqual(cv.productversion, self.pv)
        self.assertEqual(cv.case.product, self.pv.product)


    def test_create_caseversion_description(self):
        """Test the description field of a new test case"""
        result = self.import_data(
            {
                "cases": [
                    {
                        "description": "case description",
                        "name": "Foo",
                        "steps": [{"instruction": "do this"}],
                        }
                    ]
                }
            )

        cv = self.model.CaseVersion.objects.get()
        self.assertEqual(cv.description, "case description")
        self.assertEqual(result.num_cases, 1)


    def test_create_caseversion_tags(self):
        """Test that case tags get created and assigned"""

        new_tags = ["tag1", "tag2", "tag3"]

        result = self.import_data(
            {
                "cases": [
                    {
                        "name": "Foo",
                        "steps": [{"instruction": "do this"}],
                        "tags": new_tags,
                        }
                    ]
                }
            )

        cv = self.model.CaseVersion.objects.get()

        case_tags = sorted([tag.name for tag in cv.tags.all()])
        self.assertEqual(case_tags, new_tags)
        self.assertEqual(result.num_cases, 1)


    def test_create_caseversion_suites(self):
        """Test that case tags get created and assigned"""

        new_suites = ["suite1 name", "suite2 name", "suite3 name"]

        result = self.import_data(
            {
                "cases": [
                    {
                        "name": "Foo",
                        "steps": [{"instruction": "do this"}],
                        "suites": new_suites,
                        }
                    ]
                }
            )

        cv = self.model.CaseVersion.objects.get()
        case_suites = sorted([suite.name for suite in cv.case.suites.all()])
        self.assertEqual(case_suites, new_suites)
        self.assertEqual(result.num_cases, 1)


    def test_create_caseversion_existing_user(self):
        """A case with created_by field filled with existing user"""

        # need a user to exist, so the import can find it.
        user = self.F.UserFactory.create(email="sumbudee@mozilla.com")

        result = self.import_data(
            {
                "cases": [
                    {
                        "created_by": "sumbudee@mozilla.com",
                        "name": "Foo",
                        "steps": [{"instruction": "do this"}]
                        }
                    ]
                }
            )

        cv = self.model.CaseVersion.objects.get()
        self.assertEqual(cv.created_by, user)
        self.assertEqual(result.num_cases, 1)


    def test_create_two_caseversions_same_user(self):
        """Two caseversions that both use the same user."""

        # need a user to exist, so the import can find it.
        user = self.model.User.objects.create(
            username="FooUser",
            email="sumbudee@mozilla.com",
            )

        case_data= {
            "cases": [
                {
                    "created_by": "sumbudee@mozilla.com",
                    "name": "Foo",
                    "steps": [{"instruction": "do this"}],
                    },
                {
                    "created_by": "sumbudee@mozilla.com",
                    "name": "Bar",
                    "steps": [{"instruction": "do this"}],
                    }
                ]
            }

        with self.assertNumQueries(17):
           result = self.import_data(case_data)


        cv1 = self.model.CaseVersion.objects.get(name="Foo")
        self.assertEqual(cv1.created_by, user)
        cv2 = self.model.CaseVersion.objects.get(name="Bar")
        self.assertEqual(cv2.created_by, user)
        self.assertEqual(result.num_cases, 2)


    def test_create_caseversion_no_existing_user(self):
        """A caseversion with a user that does not exist in the db."""

        result = self.import_data(
            {
                "cases": [
                    {
                        "created_by": "sumbudee@mozilla.com",
                        "name": "Foo",
                        "steps": [{"instruction": "do this"}],
                        }
                    ]
                }
            )

        cv = self.model.CaseVersion.objects.get()
        self.assertEqual(cv.created_by, None)
        self.assertEqual(result.num_cases, 1)
        self.assertEqual(
            result.warnings[0]["reason"],
            ImportResult.WARN_USER_NOT_FOUND,
            )


    def test_create_caseversion_existing_tag(self):
        """A caseversion that uses an existing product tag"""

        # need a tag to exist, so the import can find it.
        tag = self.model.Tag.objects.create(
            name="FooTag",
            product=self.pv.product,
            )

        result = self.import_data(
                {
                "cases": [
                        {
                        "name": "Foo",
                        "steps": [{"instruction": "do this"}],
                        "tags": ["FooTag"],
                        }
                ]
            }
        )

        cv = self.model.CaseVersion.objects.get()
        self.assertEqual(cv.tags.get(), tag)
        self.assertEqual(result.num_cases, 1)


    def test_create_caseversion_existing_suite(self):
        """A case that uses an existing suite."""

        # need a suite to exist, so the import can find it.
        suite = self.model.Suite.objects.create(
            name="FooSuite",
            product=self.pv.product,
            )

        result = self.import_data(
                {
                "cases": [
                        {
                        "name": "Foo",
                        "steps": [{"instruction": "do this"}],
                        "suites": ["FooSuite"],
                        }
                ]
            }
        )

        cv = self.model.CaseVersion.objects.get()
        self.assertEqual(cv.case.suites.get(), suite)
        self.assertEqual(result.num_cases, 1)
        self.assertEqual(result.num_suites, 0)


    def test_case_no_name_skip(self):
        """A case with no name is skipped."""
        result = self.import_data(
            {
                "cases": [
                    {
                        "description": "Foo",
                        }
                    ]
                }
            )

        self.assertFalse(list(self.model.CaseVersion.objects.all()))
        self.assertEqual(result.num_cases, 0)
        self.assertEqual(
            result.warnings[0]["reason"],
            ImportResult.SKIP_CASE_NO_NAME,
            )


    def test_case_name_conflict_skip(self):
        """A case with same name already exists."""
        self.F.CaseVersionFactory.create(productversion=self.pv, name="Foo")

        case_to_import = {
            "cases": [
                {
                    "name": "Foo",
                    }
                ]
            }

        result = self.import_data(case_to_import)

        self.assertEqual(result.num_cases, 0)
        self.assertEqual(
            result.warnings[0]["reason"],
            ImportResult.SKIP_CASE_NAME_CONFLICT,
            )


    def test_no_step_warning(self):
        """A case with no steps emits a warning."""
        result = self.import_data(
            {
                "cases": [
                    {
                        "name": "Foo",
                        }
                    ]
                }
            )

        cv = self.model.CaseVersion.objects.get()
        self.assertEqual(cv.steps.count(), 0)
        self.assertEqual(result.num_cases, 1)
        self.assertEqual(result.warnings[0]["item"], cv)
        self.assertEqual(
            result.warnings[0]["reason"],
            ImportResult.WARN_NO_STEPS,
            )


    def test_steps(self):
        """Steps are created with correct instruction and expected values."""

        new_steps = [
            {
                "instruction": "instr1",
                "expected": "exp1"
            },
            {
                "instruction": "instr2",
                "expected": "exp2"
            },
            {
                "instruction": "instr3",
                "expected": "exp3"
            },
        ]

        result = self.import_data(
            {
                "cases": [
                    {
                        "name": "Foo",
                        "steps": new_steps,
                        }
                    ]
                }
            )

        cv = self.model.CaseVersion.objects.get()

        self.assertEqual(
            [(s.number, s.instruction, s.expected) for s in cv.steps.order_by(
                "number")],
            [(i + 1, s["instruction"], s["expected"]) for i, s in enumerate(
                new_steps)],
            )


    def test_create_suite(self):
        """Successful import creates a suite with expected values."""
        self.import_data(
            {
                "suites": [
                    {
                        "name": "Foo",
                        "description": "indescribable"
                        }
                    ]
                }
            )

        s = self.model.Suite.objects.get()
        self.assertEqual(s.name, "Foo")
        self.assertEqual(s.description, "indescribable")


    def test_suite_no_name_skip(self):
        """A suite with no name is skipped."""
        result = self.import_data(
            {
                "suites": [
                    {
                        "description": "Foo",
                        }
                    ]
                }
            )

        self.assertFalse(self.model.Suite.objects.count(), 0)
        self.assertEqual(result.num_suites, 0)
        self.assertEqual(
            result.warnings[0]["reason"],
            ImportResult.SKIP_SUITE_NO_NAME,
            )


    def test_result_object(self):
        """Successful import returns a result summary object."""
        result = self.import_data(
            {
                "cases": [
                    {
                        "name": "Foo",
                        "steps": [{"instruction": "do this"}]
                        }
                    ]
                }
            )

        result_list = result.get_as_list()
        self.assertTrue("Imported 1 cases" in result_list)
        self.assertTrue("Imported 0 suites" in result_list)



class ImporterTransactionTest(ImporterTestBase, case.TransactionTestCase):
    """Tests for ``Importer`` transactional behavior."""
    def test_step_no_instruction_skip(self):
        """Skip import on case with step and no instruction."""
        result = self.import_data(
            {
                "cases": [
                    {
                        "name": "Foo",
                        "steps": [{"expected": "did this"}]
                        }
                    ]
                }
            )

        cv = self.model.CaseVersion.objects.all()
        self.assertFalse(list(cv))
        self.assertEqual(result.num_cases, 0)
        self.assertEqual(
            result.warnings[0]["reason"],
            ImportResult.SKIP_STEP_NO_INSTRUCTION,
            )

