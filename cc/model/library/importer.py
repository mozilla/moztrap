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
    Importer for Suites and Cases.

    The "suites" or "cases" sections are optional.
    The object should be structured like this::

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

    Instantiate an ``Importer`` and call its ``import_data`` method::

        importer = Importer()
        data = importer.import_data(productversion, case_data)

    Returned data will be an ImportResult object with the following data:

    * cases: the number of cases imported
    * suites: the number of suites imported
    * skipped: list of items that could not be imported and some
      explanation why
    * warnings: list of warnings about the imported items, if any.

    """

    @transaction.commit_on_success
    def import_data(self, productversion, case_data):
        """
        Import the top-level dictionary of cases and suites.

        Return an object that has the number of imported and skipped items.

        """

        # the result object used to keep track of import status
        result = ImportResult()

        # map of suites to cases.  Map the initial dict, if one exists.
        suite_importer = None
        if "suites" in case_data:
            suite_importer = SuiteImporter(productversion.product)
            result.append(suite_importer.map_dict_list(case_data["suites"]))


        # no reason why the data couldn't include ONLY suites.  So function
        # gracefully if no cases.
        if "cases" in case_data:
            case_importer = CaseImporter(productversion, suite_importer)
            result.append(case_importer.import_cases(case_data["cases"]))

        # now create the suites and add cases to them where mapped
        if suite_importer:
            result.append(suite_importer.import_map())

        return result

class CaseImporter:
    """Imports cases and links to or creates associated tags, suites."""

    def __init__(self, productversion, suite_importer=None):

        self.productversion = productversion
        self.suite_importer = (suite_importer if suite_importer
            else SuiteImporter(productversion.product))

        # map of tags to caseversions so we can reduce lookups on the tags
        self.tag_importer = TagImporter(self.productversion.product)

        # cache of user emails
        self.user_cache = UserCache()

    def import_cases(self, case_dict_list):
        """
        Import the test cases in the data.

        This may include suites and tags that each case belongs to.  If a case
        has no name, it will be skipped.  If a case has no steps, it will
        be imported, but a warning will be given.  All fields are optional
        with the exception of a name.

        Case data should be in this format::

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


        """

        result = ImportResult()

        for new_case in case_dict_list:

            if not "name" in new_case:
                result.warn(
                    ImportResult.SKIP_CASE_NO_NAME,
                    new_case,
                    )
                continue

            # Don't re-import if we have the same case name and Product Version
            if CaseVersion.objects.filter(
                name=new_case["name"],
                productversion=self.productversion,
                ).exists():

                result.warn(
                    ImportResult.SKIP_CASE_NAME_CONFLICT,
                    new_case,
                    )

                continue

            user = self.user_cache.get_user(new_case, result)

            # the case looks good so far, but there may be a problem with
            # one of the steps.  So, create a savepoint in case something
            # is inherently wrong with this case, we can roll back to skip
            # it, and still import the rest of the cases.
            sid = transaction.savepoint()

            # create the top-level case object which holds the versions
            case = Case.objects.create(product=self.productversion.product)

            # create the case version which holds the details
            caseversion = CaseVersion.objects.create(
                productversion=self.productversion,
                case=case,
                name=new_case["name"],
                description=new_case.get("description", ""),
                user=user,
                )


            # add the steps to this case version
            if "steps" in new_case:
                try:
                    self.import_steps(caseversion, new_case["steps"])
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
                    caseversion,
                    )

            # map the tags to the case version
            if "tags" in new_case:
                self.tag_importer.map_name_list(caseversion, new_case["tags"])

            # map this case to the suite
            if "suites" in new_case:
                self.suite_importer.map_name_list(case, new_case["suites"])

            # case has been created, increment our count for reporting
            result.newcase()

            # this case went ok.  We'll save it as complete in the overall
            # transaction.
            transaction.savepoint_commit(sid)

            # now create the tags and add case versions to them where mapped
            self.tag_importer.import_map()

            # now create the suites and add cases to them where mapped
            self.suite_importer.import_map()

        return result


    def import_steps(self, caseversion, step_data):
        """
        Add the steps to this case version.

        Instruction is a required field for a step, but expected is optional.

        """

        for step_num, new_step in enumerate(step_data):
            if "instruction" in new_step:
                casestep = CaseStep.objects.create(
                    caseversion=caseversion,
                    number=step_num+1,
                    instruction=new_step["instruction"],
                    expected=new_step.get("expected", ""),
                    )
            else:
                raise ValueError(ImportResult.SKIP_STEP_NO_INSTRUCTION)

class UserCache:

    def __init__(self):
        self.cache = {}

    def get_user(self, single_case_data, result):
        """
        Return the user object that matches the email in the case, if any.

        If the single_case_data has no "created_by" field, return None.
        If the email is already in the cache, then return that user.
        If this method had already searched for the user and not found it,
        then it will have registered a warning already, and will only warn
        for that user once.  In that case, it will save the user of None
        in the cache and subsequent calls for that user will return None

        """

        if "created_by" in single_case_data:
            email = single_case_data["created_by"]
        else:
            return None

        if email in self.cache:
            return self.cache[email]

        else:
            try:
                user = User.objects.get(email=email)
                self.cache[email] = user

            except User.DoesNotExist:
                result.warn(
                    ImportResult.WARN_USER_NOT_FOUND,
                    new_case,
                    )
                self.cache[email] = None

        return self.cache[email]

class MapBase:
    """Base for both types of maps"""

    def __init__(self, product):
        self.product = product
        self.map = {}

class TagImporter(MapBase):
    """Imports suites based on lists and dicts of suites used to build it."""

    def map_name_list(self, caseversion, tag_data):
        """Map a simple list of tag names"""

        for tag_name in tag_data:
            caseversions = self.map.setdefault(tag_name, [])
            caseversions.append(caseversion)

    def import_map(self):
        """
        Import all mapped tags.

        The UI should prevent creating global and product tags of the same
        name.  However, we check for that, just in case.

        Use or create tags in this order of priority:

            * product tag
            * global tag
            * create new product tag

        """

        for tag_name, caseversions in self.map.items():
            tag_list = Tag.objects.filter(
                name=tag_name,
                product__in=[None, self.product],
                ).order_by("-product")

            # If there is a product tag, it will be sorted to first.
            # If not, then the only item will be the global one, so
            # use that.
            if tag_list.count() > 0:
                tag = tag_list[0]

            else:
                tag = Tag.objects.create(
                    name=tag_name,
                    product=self.product,
                    )

            tag.caseversions.add(*caseversions)

        # we have imported these items.  clear them out now.
        self.map.clear()

class SuiteImporter(MapBase):
    """
    Imports suites based on lists and dicts of suites used to build it.

    The internal dict looks like this::

        {
            "suitename": {
                "description": "foo",
                "cases": [case1, case2]
            }
        }

    """

    def map_name_list(self, case, suite_data):
        """Map a simple list of Suite names."""

        for suite_name in suite_data:
            suite = self.map.setdefault(suite_name, {})
            cases = suite.setdefault("cases", [])
            cases.append(case)

    def map_dict_list(self, suite_data):
        """
        Map a list of suite dictionary objects.

        Map a dict that looks like this::

            "suites": [
                {
                    "description": "suite description",
                    "name": "suite1 name"
                },
                {
                    "description": "suite description",
                    "name": "top-level suite name"
                }
            ]

        Suites without names will be skipped.

        """

        result = ImportResult()

        for suite in suite_data:
            if "name" in suite:
                self.map[suite["name"]] = {
                    "description": suite.get("description", "")
                    }
            else:
                result.warn(
                    ImportResult.SKIP_SUITE_NO_NAME,
                    suite,
                    )
        return result

    def import_map(self):
        """Import all mapped suites."""

        result = ImportResult()

        for suite_name, suite_data in self.map.items():

            suite, created = Suite.objects.get_or_create(
                name=suite_name,
                product=self.product,
                defaults={"description": suite_data.get("description", "")},
                )

            if created:
                result.newsuite()

            # now add any cases the suite may have specified
            if "cases" in suite_data:
                for case in suite_data["cases"]:
                    SuiteCase.objects.create(case=case, suite=suite)

        # we have imported (or warned on) these items, so reset ourself.
        self.map.clear()

        return result


class ImportResult:
    """
    Results of the import process.

    This may be for a small part of the process, or the process as a whole.
    ImportResults can be merged with the append() method.

    """

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

        new_data = result.get_as_dict()

        self.newcase(new_data["cases"])
        self.newsuite(new_data["suites"])
        self.warnings.extend(new_data["warnings"])

    def get_as_dict(self):
        return {
            "cases": self.num_cases,
            "suites": self.num_suites,
            "warnings": self.warnings,
            }

    def get_as_list(self):
        result_list = [
            "{0}: {1}".format(x["reason"], x["item"])
            for x in self.warnings
            ]

        result_list.append("Imported {0} cases".format(self.num_cases))
        result_list.append("Imported {0} suites".format(self.num_suites))
        return result_list
