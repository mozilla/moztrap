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
from tests import case
from cc.model.library.importer import ImportResult



class ImporterTest(case.DBTestCase):
    """Tests for ``Importer``."""
    def setUp(self):
        """Setup for importer tests; create a product version."""
        self.pv = self.F.ProductVersionFactory.create()


    def import_data(self, case_data):
        """Instantiate ``Importer``, call ``import_data`` and return result."""
        from cc.model.library.importer import Importer
        return Importer().import_data(self.pv, case_data)


    def test_create_caseversion(self):
        """Successful import creates a caseversion with expected values."""
        self.import_data(
            {
                "cases": [
                    {
                        "name": "Foo",
                        "steps": [{"instruction": "do this"}]
                        }
                    ]
                }
            )

        cv = self.model.CaseVersion.objects.get()
        self.assertEqual(cv.name, "Foo")
        self.assertEqual(cv.productversion, self.pv)
        self.assertEqual(cv.case.product, self.pv.product)


    def test_create_caseversion_all_fields(self):
        """
        A case with all fields filled, including match with existing email.
        """

        # need a user to exist, so the import can find it.
        user = self.model.User.objects.create(
            username="FooUser",
            email="sumbudee@mozilla.com",
            )
        new_tags = ["tag1", "tag2", "tag3"]
        new_suites = ["suite1 name", "suite2 name", "suite3 name"]

        result = self.import_data(
            {
                "cases": [
                    {
                        "created_by": "sumbudee@mozilla.com",
                        "description": "case description",
                        "name": "Foo",
                        "steps": [
                            {
                                "instruction": "action text",
                                "expected": "expected text"
                            }
                        ],
                        "suites": new_suites,
                        "tags": new_tags,
                        }
                    ]
                }
            )

        cv = self.model.CaseVersion.objects.get()
        self.assertEqual(cv.name, "Foo")
        self.assertEqual(cv.description, "case description")
        self.assertEqual(cv.created_by, user)

        case_tags = sorted([tag.name for tag in cv.tags.all()])
        self.assertEqual(case_tags, new_tags)

        self.assertEqual(cv.productversion, self.pv)
        self.assertEqual(cv.case.product, self.pv.product)

        self.assertEqual(result.num_cases, 1)
        self.assertEqual(result.num_suites, 3)
        self.assertEqual(result.warnings, [])


    def test_create_two_caseversions_same_user(self):
        """Two caseversions that both use the same user."""

        # need a user to exist, so the import can find it.
        user = self.model.User.objects.create(
            username="FooUser",
            email="sumbudee@mozilla.com",
            )


        result = self.import_data(
                {
                "cases": [
                        {
                        "created_by": "sumbudee@mozilla.com",
                        "name": "Foo",
                        "steps": [
                                {
                                "instruction": "action text",
                                "expected": "expected text"
                            }
                        ],
                        },
                        {
                        "created_by": "sumbudee@mozilla.com",
                        "name": "Bar",
                        "steps": [
                                {
                                "instruction": "action text",
                                "expected": "expected text"
                            }
                        ],
                        }
                ]
            }
        )

        cv1 = self.model.CaseVersion.objects.get(name="Foo")
        self.assertEqual(cv1.name, "Foo")
        self.assertEqual(cv1.created_by, user)
        self.assertEqual(cv1.productversion, self.pv)
        self.assertEqual(cv1.case.product, self.pv.product)

        cv2 = self.model.CaseVersion.objects.get(name="Bar")
        self.assertEqual(cv2.name, "Bar")
        self.assertEqual(cv2.created_by, user)
        self.assertEqual(cv2.productversion, self.pv)
        self.assertEqual(cv2.case.product, self.pv.product)


        self.assertEqual(result.num_cases, 2)
        self.assertEqual(result.num_suites, 0)
        self.assertEqual(result.warnings, [])


    def test_create_caseversion_no_existing_user(self):
        """A caseversion with a user that does not exist in the db."""

        result = self.import_data(
            {
                "cases": [
                    {
                        "created_by": "sumbudee@mozilla.com",
                        "name": "Foo",
                        "steps": [
                            {
                                "instruction": "action text",
                            }
                        ],
                        }
                    ]
                }
            )

        cv = self.model.CaseVersion.objects.get()
        self.assertEqual(cv.name, "Foo")
        self.assertEqual(cv.created_by, None)
        self.assertEqual(cv.productversion, self.pv)
        self.assertEqual(cv.case.product, self.pv.product)

        self.assertEqual(result.num_cases, 1)
        self.assertEqual(result.num_suites, 0)
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
                        "steps": [
                                {
                                "instruction": "action text",
                                "expected": "expected text"
                            }
                        ],
                        "tags": ["FooTag"],
                        }
                ]
            }
        )

        cv = self.model.CaseVersion.objects.get()
        self.assertEqual(cv.name, "Foo")
        self.assertEqual(cv.tags.get(), tag)
        self.assertEqual(cv.productversion, self.pv)
        self.assertEqual(cv.case.product, self.pv.product)

        self.assertEqual(result.num_cases, 1)
        self.assertEqual(result.num_suites, 0)
        self.assertEqual(result.warnings, [])


    def test_create_caseversion_existing_suite(self):
        """A case that uses an existing suite."""

        # need a tag to exist, so the import can find it.
        suite = self.model.Suite.objects.create(
            name="FooSuite",
            product=self.pv.product,
            )

        result = self.import_data(
                {
                "cases": [
                        {
                        "name": "Foo",
                        "steps": [
                                {
                                "instruction": "action text",
                                "expected": "expected text"
                            }
                        ],
                        "suites": ["FooSuite"],
                        }
                ]
            }
        )

        cv = self.model.CaseVersion.objects.get()
        self.assertEqual(cv.name, "Foo")
        self.assertEqual(cv.case.suites.get(), suite)
        self.assertEqual(cv.productversion, self.pv)
        self.assertEqual(cv.case.product, self.pv.product)

        self.assertEqual(result.num_cases, 1)
        self.assertEqual(result.num_suites, 0)
        self.assertEqual(result.warnings, [])


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

        cv = self.model.CaseVersion.objects.all()
        self.assertFalse(list(cv))

        self.assertEqual(result.num_cases, 0)
        self.assertEqual(result.num_suites, 0)
        self.assertEqual(
            result.warnings[0]["reason"],
            ImportResult.SKIP_CASE_NO_NAME,
            )


    def test_case_name_conflict_skip(self):
        """A case with same name already exists."""
        case_to_import = {
            "cases": [
                {
                    "name": "Foo",
                    }
                ]
            }

        self.import_data(case_to_import)
        result = self.import_data(case_to_import)


        cv = self.model.CaseVersion.objects.get()
        self.assertEqual(cv.name, "Foo")
        self.assertEqual(cv.productversion, self.pv)
        self.assertEqual(cv.case.product, self.pv.product)

        self.assertEqual(result.num_cases, 0)
        self.assertEqual(result.num_suites, 0)
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
        self.assertEqual(cv.name, "Foo")
        self.assertEqual(cv.productversion, self.pv)
        self.assertEqual(cv.case.product, self.pv.product)

        self.assertEqual(result.num_cases, 1)
        self.assertEqual(result.num_suites, 0)
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
        self.assertEqual(cv.name, "Foo")
        self.assertEqual(cv.productversion, self.pv)
        self.assertEqual(cv.case.product, self.pv.product)

        #@@@ Placeholder till Carl tells me the graceful way to do this...  :)
        case_steps = cv.steps.order_by("instruction")
        for step in case_steps:
            i = step.number - 1
            self.assertEqual(step.instruction, new_steps[i]["instruction"])
            self.assertEqual(step.expected, new_steps[i]["expected"])

        self.assertEqual(result.num_cases, 1)
        self.assertEqual(result.num_suites, 0)
        self.assertEqual(result.warnings, [])


    def test_step_no_instruction_skip(self):
        """Skip import on case with step and no instruction."""

        """
        @@@ Need this to be in a class extending the the TransactionTestCase
        base class.  The case should be something like this:

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

        self.assertEqual(result.num_cases, 0)
        self.assertEqual(result.num_suites, 0)
        self.assertEqual(result.warnings, [])

        cv = self.model.CaseVersion.objects.all()
        self.assertFalse(list(cv))
        """

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

        s = self.model.Suite.objects.all()
        self.assertFalse(list(s))

        self.assertEqual(result.num_cases, 0)
        self.assertEqual(result.num_suites, 0)
        self.assertEqual(
            result.warnings[0]["reason"],
            ImportResult.SKIP_SUITE_NO_NAME,
            )


    def test_existing_and_new_suite(self):
        pass


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

        self.assertEqual(result.num_cases, 1)
        self.assertEqual(result.num_suites, 0)
        self.assertEqual(result.warnings, [])

        result_list = result.get_as_list()
        self.assertTrue("Imported 1 cases" in result_list)
        self.assertTrue("Imported 0 suites" in result_list)



