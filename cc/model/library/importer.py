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
"""Importer for suites and cases from a dictionary."""

from django.db import transaction

from ..core.models import Product, ProductVersion
from ..core.auth import User
from ..tags.models import Tag
from .models import Case, CaseVersion, CaseStep, Suite, SuiteCase


class Importer(object):
    """
    Importer for Suites and Cases.  The object should be structured like this.
    The "suites" or "cases" sections are optional::

        {
            "suites": [
                {
                    "name": "suite1 name",
                    "description": "suite description"
                },
            ],
            "cases": [
                {
                    "name": "case title",
                    "description": "case description",
                    "tags": ["tag1", "tag2", "tag3"],
                    "suites": ["suite1 name", "suite2 name", "suite3 name"],
                    "created_by": "cdawson@mozilla.com"
                    "steps": [
                        {
                            "instruction": "insruction text",
                            "expected": "expected text"
                        },
                    ]
                }
            ]
        }

    Instantiate a ``Importer`` and call its ``import_data`` method::

        importer = Importer()
        data = importer.import_data(product_version, case_data)

    Returned data will be a dictionary with the following:

    * cases: the number of cases imported
    * suites: the number of suites imported
    * skipped: list of items that could not be imported and some
      explanation why
    * warnings: list of warnings about the imported items, if any.
    """

    @transaction.commit_on_success
    def import_data(self, product_version, case_data):
        """
        Import the given dictionary object into the database. Then return
        an object that has the number of imported and skipped items.
        """

        # the result object used to keep track of import status
        result = ImportResult()

        # map of tags to caseversions so we can reduce lookups on the tags
        self.tag_map = {}

        # this a a mapping of cases to suites that we will build and,
        # then use in the final stage to finally link up

        self.suite_map = {}
        if "suites" in case_data:
            for suite in case_data["suites"]:
                if "name" in suite:
                    self.suite_map[suite["name"]] = {
                        "description": suite.get("description", "")
                        }
                else:
                    result.warn(
                        ImportResult.SKIP_SUITE_NO_NAME,
                        suite,
                        )


        # no reason why the data couldn't include ONLY suites.  So function
        # gracefully if no cases.
        if "cases" in case_data:
            result.append(self.import_cases(
                product_version,
                case_data["cases"],
                ))

        # now create the suites and add cases to them where mapped
        result.append(self.import_mapped_suites(product_version.product))

        # now create the tags and add case versions to them where mapped
        self.import_mapped_tags(product_version.product)

        return result

    def import_cases(self, product_version, case_list):
        """
        Import the cases section of case_data.  This may include
        suites that each case belongs to.
        """

        result = ImportResult()

        for new_case in case_list:

            if not "name" in new_case:
                result.warn(
                    ImportResult.SKIP_CASE_NO_NAME,
                    new_case,
                    )
                continue

            # Don't re-import if we have the same case name and Product Version
            if CaseVersion.objects.filter(name=new_case["name"],
                                          productversion=product_version
                                          ).exists():

                result.warn(
                    ImportResult.SKIP_CASE_NAME_CONFLICT,
                    new_case,
                    )

                continue


            # the case looks good so far, but there may be a problem with
            # one of the steps.  So, create a savepoint in case something
            # is inherently wrong with this case, we can roll back to skip
            # it, and still import the rest of the cases.
            sid = transaction.savepoint()

            # create the top-level case object which holds the versions
            case = Case.objects.create(product=product_version.product)

            # create the case version which holds the details
            case_version = CaseVersion.objects.create(
                productversion = product_version,
                case = case,
                name = new_case["name"],
                description = new_case.get("description", ""))


            if "created_by" in new_case:
                try:
                    user = User.objects.get(email=new_case["created_by"])
                    case_version.created_by = user
                    case_version.save()

                except User.DoesNotExist:
                    result.warn(
                        ImportResult.WARN_USER_NOT_FOUND,
                        new_case,
                        )



            # add the steps to this case version
            if "steps" in new_case:
                try:
                    self.import_steps(case_version, new_case["steps"])
                except ValueError as e:
                    result.warn(
                        e,
                        new_case,
                        )
                    transaction.savepoint_rollback(sid)
                    continue
            else:
                result.warn(
                    ImportResult.WARN_NO_STEPS,
                    case_version,
                    )

            # map the tags to the case version
            if "tags" in new_case:
                self.map_tags(case_version, new_case["tags"])

            # map this case to the suite
            if "suites" in new_case:
                self.map_suites(case, new_case["suites"])

            # case has been created, increment our count for reporting
            result.newcase()

            # this case went ok.  We'll save it as complete in the overall
            # transaction.
            transaction.savepoint_commit(sid)

        return result


    def import_steps(self, case_version, step_data):
        """
        Add the steps to this case version.
        Instruction is a required field for a step, but expected is optional.
        """

        for step_num, new_step in enumerate(step_data):
            if "instruction" in new_step:
                casestep = CaseStep.objects.create(
                        caseversion = case_version,
                        number = step_num+1,
                        instruction = new_step["instruction"],
                        expected = new_step.get("expected", None))
            else:
                raise ValueError(ImportResult.SKIP_STEP_NO_INSTRUCTION)

    def map_tags(self, case_version, tag_data):
        for tag_name in tag_data:
            case_versions = self.tag_map.setdefault(tag_name, [])
            case_versions.append(case_version)

    def import_mapped_tags(self, product):
        """
        If there's a non-product specific tag, apply that.  If there's not,
        then create this tag as product specific.
        """

        for tag_name, case_versions in self.tag_map.items():
            tag, created = Tag.objects.get_or_create(name=tag_name,
                                                     product=None)

            # if we created this here, make it product specific
            if created:
                tag.product=product

            for case_version in case_versions:
                case_version.tags.add(tag)


    def map_suites(self, case, suite_data):
        """
        This map will looks like this::

            {
                "suitename": {
                    "description": "foo",
                    "cases": [case1, case2]
                }
            }

        suite_data is a list of suite names

        """

        for suite_name in suite_data:
            suite = self.suite_map.setdefault(suite_name, {})
            cases = suite.setdefault("cases", [])
            cases.append(case)

    def import_mapped_suites(self, product):

        result = ImportResult()

        for suite_name, suite_data in self.suite_map.items():

            suite, created = Suite.objects.get_or_create(name=suite_name,
                                                         product=product)
            if not suite.description:
                suite.description = suite_data.get("description", "")
            suite.save()

            if created:
                result.newsuite()

            # now add any cases the suite may have specified
            if "cases" in suite_data:
                for case in suite_data["cases"]:
                    SuiteCase.objects.create(case=case, suite=suite)
        return result

class ImportResult:

    SKIP_SUITE_NO_NAME = "Skipped: Name field required for Suite"
    SKIP_CASE_NO_NAME = "Skipped: Name field required for Case"
    SKIP_STEP_NO_INSTRUCTION = "Skipped: Instruction field required for Step"
    SKIP_CASE_NAME_CONFLICT = ("Skipped: Case with this name already exists "
        "for this product")
    WARN_NO_STEPS = "Warning: Case has no steps"
    WARN_USER_NOT_FOUND = "Warning: user with this email does not exist."

    def __init__(self):

        # the total number of test cases that were imported
        self.num_cases = 0
        self.num_suites = 0
        self.warnings = []

    def warn(self, reason, item):
        self.warnings.append({"reason": reason, "item": item})

    def newcase(self, incr=1):
        self.num_cases += incr

    def newsuite(self, incr=1):
        self.num_suites += incr

    def append(self, result):
        """Append the results object into this results object."""

        new_data = result.get_results()

        self.newcase(new_data["cases"])
        self.newsuite(new_data["suites"])
        self.warnings.extend(new_data["warnings"])

    def get_results(self):
        return {
            "cases": self.num_cases,
            "suites": self.num_suites,
            "warnings": self.warnings,
            }

    def get_as_list(self):
        result_list = ["{0}: {1}".format(x["reason"], x["item"])
            for x in self.warnings]
        result_list.append("Imported {0} cases".format(self.num_cases))
        result_list.append("Imported {0} suites".format(self.num_suites))
        return result_list
