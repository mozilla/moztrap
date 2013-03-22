"""Tests for suite/case importer."""
from tests import case

from mock import patch

from moztrap.model.library.importer import ImportResult, SuiteImporter



class ImporterTestBase(object):
    """Common base class for importer tests."""
    def setUp(self):
        """Setup for importer tests; create a product version."""
        self.pv = self.F.ProductVersionFactory.create()


    def import_data(self, case_data):
        """Instantiate ``Importer``, call ``import_data`` and return result."""
        from moztrap.model.library.importer import Importer
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


    def test_create_caseversion_idprefix(self):
        """Successful import creates a caseversion with an idprefix."""
        self.import_data(
            {
                "cases": [
                    {
                        "name": "Foo",
                        "idprefix": "wow",
                        "steps": [{"instruction": "do this"}],
                        }
                ]
            }
        )

        cv = self.model.CaseVersion.objects.get()
        self.assertEqual(cv.name, "Foo")
        self.assertEqual(cv.case.idprefix, "wow")
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

        case_tags = [tag.name for tag in cv.tags.all()]
        self.assertEqual(set(case_tags), set(new_tags))
        self.assertEqual(result.num_cases, 1)


    def test_create_caseversion_suites(self):
        """Test that case suites get created and assigned"""

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
        case_suites = [suite.name for suite in cv.case.suites.all()]
        self.assertEqual(set(case_suites), set(new_suites))
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
        """
        Two caseversions that both use the same user.  Test that import caches
        the user and doesn't have to query for it a second time.

        Expect 19 queries for this import:

        Query 1: Ensure this caseversion does not already exist for this
        productversion::

            SELECT (1) AS `a` FROM `library_caseversion` WHERE
            (`library_caseversion`.`deleted_on` IS NULL AND
            `library_caseversion`.`name` = Foo AND
            `library_caseversion`.`productversion_id` = 12 ) LIMIT 1

        Query 2: Find the user for this email::

            SELECT `auth_user`.`id`, `auth_user`.`username`,
            `auth_user`.`first_name`, `auth_user`.`last_name`,
            `auth_user`.`email`, `auth_user`.`password`,
            `auth_user`.`is_staff`, `auth_user`.`is_active`,
            `auth_user`.`is_superuser`, `auth_user`.`last_login`,
            `auth_user`.`date_joined` FROM `auth_user` WHERE
            `auth_user`.`email` = sumbudee@mozilla.com

        Transaction: SAVEPOINT s140735243669888_x1

        Query 3: Create the first new case object::

            INSERT INTO `library_case` (`created_on`, `created_by_id`,
            `modified_on`, `modified_by_id`, `deleted_on`, `deleted_by_id`,
            `product_id`) VALUES (2012-03-07 19:35:34, None, 2012-03-07
            19:35:34, None, None, None, 12)

        Queries 4-8: Create the first new caseversion object::

            INSERT INTO `library_caseversion` (`created_on`, `created_by_id`,
            `modified_on`, `modified_by_id`, `deleted_on`, `deleted_by_id`,
            `status`, `productversion_id`, `case_id`, `name`, `description`,
            `latest`, `envs_narrowed`) VALUES (2012-03-07 19:35:34, 2,
            2012-03-07 19:35:34, 2, None, None, draft, 12, 10, Foo, , False,
            False)

             SELECT `environments_environment`.`id`,
            `environments_environment`.`created_on`,
            `environments_environment`.`created_by_id`,
            `environments_environment`.`modified_on`,
            `environments_environment`.`modified_by_id`,
            `environments_environment`.`deleted_on`,
            `environments_environment`.`deleted_by_id`,
            `environments_environment`.`profile_id` FROM
            `environments_environment` INNER JOIN
            `core_productversion_environments` ON
            (`environments_environment`.`id` =
            `core_productversion_environments`.`environment_id`) WHERE
            (`environments_environment`.`deleted_on` IS NULL AND
            `core_productversion_environments`.`productversion_id` = 12 )

             SELECT `library_caseversion`.`id`,
            `library_caseversion`.`created_on`,
            `library_caseversion`.`created_by_id`,
            `library_caseversion`.`modified_on`,
            `library_caseversion`.`modified_by_id`,
            `library_caseversion`.`deleted_on`,
            `library_caseversion`.`deleted_by_id`,
            `library_caseversion`.`status`,
            `library_caseversion`.`productversion_id`,
            `library_caseversion`.`case_id`, `library_caseversion`.`name`,
            `library_caseversion`.`description`,
            `library_caseversion`.`latest`,
            `library_caseversion`.`envs_narrowed` FROM `library_caseversion`
            INNER JOIN `core_productversion` ON
            (`library_caseversion`.`productversion_id` =
            `core_productversion`.`id`) WHERE
            (`library_caseversion`.`deleted_on` IS NULL AND
            `library_caseversion`.`case_id` = 10 ) ORDER BY
            `core_productversion`.`order` DESC LIMIT 1

             UPDATE `library_caseversion` SET `latest` = False WHERE
            (`library_caseversion`.`deleted_on` IS NULL AND
            `library_caseversion`.`case_id` = 10 )

             UPDATE `library_caseversion` SET `created_on` = 2012-03-07
            19:35:34, `created_by_id` = 2, `modified_on` = 2012-03-07 19:35:34,
            `modified_by_id` = 2, `deleted_on` = NULL, `deleted_by_id` = NULL,
            `status` = draft, `productversion_id` = 12, `case_id` = 10, `name`
            = Foo, `description` = , `latest` = True, `envs_narrowed` = False
            WHERE `library_caseversion`.`id` = 10

        Query 9: During save, check if there are other caseversions for this
                 case to sync names.
            SELECT `library_caseversion`.`id`, `library_caseversion`
            .`created_on`,
            `library_caseversion`.`created_by_id`, `library_caseversion`
            .`modified_on`,
            `library_caseversion`.`modified_by_id`, `library_caseversion`
            .`deleted_on`,
            `library_caseversion`.`deleted_by_id`, `library_caseversion`
            .`cc_version`,
            `library_caseversion`.`status`, `library_caseversion`
            .`productversion_id`,
            `library_caseversion`.`case_id`, `library_caseversion`.`name`,
            `library_caseversion`.`description`, `library_caseversion`
            .`latest`,
            `library_caseversion`.`envs_narrowed` FROM `library_caseversion`
             INNER JOIN
            `core_productversion` ON (`library_caseversion`
            .`productversion_id` =
            `core_productversion`.`id`) WHERE (`library_caseversion`
            .`deleted_on` IS
            NULL AND `library_caseversion`.`case_id` = 1 ) ORDER BY
            `library_caseversion`.`case_id` ASC,
            `core_productversion`.`order` ASC

        Query 10: Add the new step to the caseversion::

            INSERT INTO `library_casestep` (`created_on`, `created_by_id`,
            `modified_on`, `modified_by_id`, `deleted_on`, `deleted_by_id`,
            `caseversion_id`, `number`, `instruction`, `expected`) VALUES
            (2012-03-07 19:35:34, None, 2012-03-07 19:35:34, None, None, None,
            10, 1, do this, )

        Transaction: RELEASE SAVEPOINT s140735243669888_x1

        Query 11: Ensure the second caseversion with this name and pv doesn't
        exist::

            SELECT (1) AS `a` FROM `library_caseversion` WHERE
            (`library_caseversion`.`deleted_on` IS NULL AND
            `library_caseversion`.`name` = Bar AND
            `library_caseversion`.`productversion_id` = 12 ) LIMIT 1

        Transaction: SAVEPOINT s140735243669888_x2

        **NOTE: We didn't have to search for the user again, since it was
        cached**

        Query 12: Create the second new case::

            INSERT INTO `library_case` (`created_on`, `created_by_id`,
            `modified_on`, `modified_by_id`, `deleted_on`, `deleted_by_id`,
            `product_id`) VALUES (2012-03-07 19:35:34, None, 2012-03-07
            19:35:34, None, None, None, 12)

        Queries 13-17: Create the second new caseversion::

             INSERT INTO `library_caseversion` (`created_on`, `created_by_id`,
             `modified_on`, `modified_by_id`, `deleted_on`, `deleted_by_id`,
             `status`, `productversion_id`, `case_id`, `name`, `description`,
             `latest`, `envs_narrowed`) VALUES (2012-03-07 19:35:34, 2,
             2012-03-07 19:35:34, 2, None, None, draft, 12, 11, Bar, , False,
             False)

              SELECT `environments_environment`.`id`,
             `environments_environment`.`created_on`,
             `environments_environment`.`created_by_id`,
             `environments_environment`.`modified_on`,
             `environments_environment`.`modified_by_id`,
             `environments_environment`.`deleted_on`,
             `environments_environment`.`deleted_by_id`,
             `environments_environment`.`profile_id` FROM
             `environments_environment` INNER JOIN
             `core_productversion_environments` ON
             (`environments_environment`.`id` =
             `core_productversion_environments`.`environment_id`) WHERE
             (`environments_environment`.`deleted_on` IS NULL AND
             `core_productversion_environments`.`productversion_id` = 12 )

              SELECT `library_caseversion`.`id`,
             `library_caseversion`.`created_on`,
             `library_caseversion`.`created_by_id`,
             `library_caseversion`.`modified_on`,
             `library_caseversion`.`modified_by_id`,
             `library_caseversion`.`deleted_on`,
             `library_caseversion`.`deleted_by_id`,
             `library_caseversion`.`status`,
             `library_caseversion`.`productversion_id`,
             `library_caseversion`.`case_id`, `library_caseversion`.`name`,
             `library_caseversion`.`description`,
             `library_caseversion`.`latest`,
             `library_caseversion`.`envs_narrowed` FROM `library_caseversion`
             INNER JOIN `core_productversion` ON
             (`library_caseversion`.`productversion_id` =
             `core_productversion`.`id`) WHERE
             (`library_caseversion`.`deleted_on` IS NULL AND
             `library_caseversion`.`case_id` = 11 ) ORDER BY
             `core_productversion`.`order` DESC LIMIT 1

              UPDATE `library_caseversion` SET `latest` = False WHERE
             (`library_caseversion`.`deleted_on` IS NULL AND
             `library_caseversion`.`case_id` = 11 )

              UPDATE `library_caseversion` SET `created_on` = 2012-03-07
             19:35:34, `created_by_id` = 2, `modified_on` = 2012-03-07
             19:35:34, `modified_by_id` = 2, `deleted_on` = NULL,
             `deleted_by_id` = NULL, `status` = draft, `productversion_id` =
             12, `case_id` = 11, `name` = Bar, `description` = , `latest` =
             True, `envs_narrowed` = False WHERE `library_caseversion`.`id` =
             11

        Query 18: Check for other caseversions for the same case to sync names

            SELECT `library_caseversion`.`id`, `library_caseversion`
            .`created_on`,
            `library_caseversion`.`created_by_id`, `library_caseversion`
            .`modified_on`,
            `library_caseversion`.`modified_by_id`, `library_caseversion`
            .`deleted_on`,
            `library_caseversion`.`deleted_by_id`, `library_caseversion`
            .`cc_version`,
            `library_caseversion`.`status`, `library_caseversion`
            .`productversion_id`,
            `library_caseversion`.`case_id`, `library_caseversion`.`name`,
            `library_caseversion`.`description`, `library_caseversion`
            .`latest`,
            `library_caseversion`.`envs_narrowed` FROM `library_caseversion`
             INNER JOIN
            `core_productversion` ON (`library_caseversion`
            .`productversion_id` =
            `core_productversion`.`id`) WHERE (`library_caseversion`
            .`deleted_on` IS
            NULL AND `library_caseversion`.`case_id` = 2 ) ORDER BY
            `library_caseversion`.`case_id` ASC,
            `core_productversion`.`order` ASC

        Query 19: Add the step to the second caseversion::

            INSERT INTO `library_casestep` (`created_on`, `created_by_id`,
            `modified_on`, `modified_by_id`, `deleted_on`, `deleted_by_id`,
            `caseversion_id`, `number`, `instruction`, `expected`) VALUES
            (2012-03-07 19:35:34, None, 2012-03-07 19:35:34, None, None, None,
            11, 1, do this, )

        Transaction: RELEASE SAVEPOINT s140735243669888_x2

        Note: Django 1.4 now logs transaction points in the connection.queries

        EXPECT: 19 Queries + 4 Transaction actions = 23 queries.

        To re-capture this query list, use a block like this in place
            of the "with self.assertNumQueries..." block::

                from django.conf import settings
                from django.db import connection
                import json

                settings.DEBUG = True
                connection.queries = []
                result = self.import_data(case_data)

                print(json.dumps(connection.queries, indent=4))
                settings.DEBUG = False

        """

        # need a user to exist, so the import can find it.
        user = self.F.UserFactory.create(email="sumbudee@mozilla.com")

        case_data = {
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

        # Test code as normal
        with self.assertNumQueries(23):
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


    def test_create_caseversion_existing_tag_different_case(self):
        """A caseversion that uses an existing product tag with diff case"""

        # need a tag to exist, so the import can find it.
        tag = self.model.Tag.objects.create(
            name="footag",
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

        result = self.import_data({
            "cases": [{
                "name": "Foo",
                "steps": [{"instruction": "do this"}],
                "suites": ["FooSuite"],
                }]
            }
        )

        cv = self.model.CaseVersion.objects.get()
        self.assertEqual(cv.case.suites.get(), suite)
        self.assertEqual(result.num_cases, 1)
        self.assertEqual(result.num_suites, 0)


    def test_create_caseversion_existing_suite_different_case(self):
        """A case that uses an existing suite with different case."""

        # need a suite to exist, so the import can find it.
        suite = self.model.Suite.objects.create(
            name="foosuite",
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

        self.import_data(
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
        self.assertEqual(s.description, "indescribable")
        self.assertEqual(s.name, "Foo")


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

    @patch.object(SuiteImporter, 'import_suites')
    def test_unknown_exception_rollback(self, new_import_suites):
        """
        An unknown exception is thrown by the import_suites method of
        SuiteImporter, so the entire transaction is rolled back and no
        cases are imported.
        """

        case_suite_data = {
            "suites": [
                    {
                    "name": "FooSuite",
                    "description": "indescribable"
                }
            ],
            "cases": [
                    {
                    "name": "FooCase",
                    "steps": [{"instruction": "do this"}]
                },
                    {
                    "name": "BarCase",
                    "steps": [{"instruction": "do this"}]
                }
            ]
        }

        class SurpriseException(RuntimeError):
            pass

        def raise_exception():
            raise SurpriseException("Surprise!")

        new_import_suites.side_effect = raise_exception

        with self.assertRaises(SurpriseException):
            self.import_data(case_suite_data)

        self.assertEqual(self.model.Case.objects.count(), 0)
        self.assertEqual(self.model.CaseVersion.objects.count(), 0)


    # @@@ This test won't work till we upgrade to Django 1.4
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

        # @@@ The savepoint-rollback won't work until Django 1.4.
        # cv = self.model.CaseVersion.objects.all()
        # self.assertFalse(list(cv))
        # self.assertEqual(result.num_cases, 0)
        self.assertEqual(
            result.warnings[0]["reason"],
            ImportResult.SKIP_STEP_NO_INSTRUCTION,
            )
