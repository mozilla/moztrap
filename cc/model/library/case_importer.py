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


class CaseImporter(object):
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
                            "action": "action text",
                            "expected": "expected text"
                        },
                    ]
                }
            ]
        }

    Instantiate a ``CaseImporter`` and call its ``import`` method::

        importer = CaseImporter()
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

        # the total number of test cases that were imported
        self.num_cases = 0
        self.num_suites = 0
        self.skipped = []
        self.warnings = []

        # map of tags to caseversions so we can reduce lookups on the tags
        self.tag_map = {}

        # this a a mapping of cases to suites that we will build and,
        # then use in the final stage to finally link up

        if 'suites' in case_data:
            self.suite_map = {
                    x['name']: {'description': x['description']} for x in \
                    case_data['suites']}
        else:
            self.suite_map = {}

        # no reason why the data couldn't include ONLY suites.  So function
        # gracefully if no cases.
        if 'cases' in case_data:
            self.import_cases(product_version, case_data['cases'])

        # now create the suites and add cases to them where mapped
        self.import_mapped_suites(product_version.product)

        # now create the tags and add case versions to them where mapped
        self.import_mapped_tags(product_version.product)

        return {"cases": self.num_cases,
                "suites": self.num_suites,
                "skipped": self.skipped,
                "warnings": self.warnings}

    def import_cases(self, product_version, case_list):
        """
        Import the cases section of case_data.  This may include
        suites that each case belongs to.
        """

        for new_case in case_list:

            if not 'name' in new_case:
                self.skipped.append(
                    '"name" field required for a case: {0}'.format(new_case)
                )
                continue

            # Don't re-import if we have the same case name and Product Version
            if CaseVersion.objects.filter(name=new_case['name'],
                                          productversion=product_version
                                          ).exists():

                self.skipped.append(
                    ('product "{0}" already has a case named "{1}".'.format(
                        product_version.product.name, new_case['name'])))

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
                name = new_case['name'],
                description = new_case.get('description',
                None))


            if 'created_by' in new_case:
                try:
                    user = User.objects.get(email=new_case['created_by'])
                    case_version.created_by = user
                    case_version.save()

                except User.DoesNotExist:
                    self.warnings.append(
                        ('user with email "{0}" does not exist. '
                        'Setting created_by to None for {1}\n').format(
                        new_case['created_by'], new_case['name']))



            # add the steps to this case version
            if 'steps' in new_case:
                try:
                    self.import_steps(case_version, new_case['steps'])
                except ValueError as e:
                    self.skipped.append("bad steps in case: {0}: {1}".format(
                        case_version, e))
                    transaction.savepoint_rollback(sid)
                    continue
            else:
                warnings.append("no steps in case: {0}".format(case_version))

            # map the tags to the case version
            if 'tags' in new_case:
                self.map_tags(case_version, new_case['tags'])

            # map this case to the suite
            if 'suites' in new_case:
                self.map_suites(case, new_case['suites'])

            # case has been created, increment our count for reporting
            self.num_cases+=1

            # this case went ok.  We'll save it as complete in the overall
            # transaction.
            transaction.savepoint_commit(sid)



    def import_steps(self, case_version, step_data):
        """
        Add the steps to this case version.
        Instruction is a required field for a step, but expected is optional.
        """

        for step_num, new_step in enumerate(step_data):
            if 'instruction' in new_step:
                casestep = CaseStep.objects.create(
                        caseversion = case_version,
                        number = step_num+1,
                        instruction = new_step['instruction'],
                        expected = new_step.get('expected', None))
            else:
                raise ValueError(
                    "instruction required for every step: {0}".format(
                        new_step))

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
            cases = suite.setdefault('cases', [])
            cases.append(case)

    def import_mapped_suites(self, product):
        for suite_name, suite_data in self.suite_map.items():

            suite, created = Suite.objects.get_or_create(name=suite_name,
                                                         product=product)
            if not suite.description:
                suite.description = suite_data.get('description', '')
            suite.save()

            if created:
                self.num_suites +=1

            # now add any cases the suite may have specified
            if 'cases' in suite_data:
                for case in suite_data['cases']:
                    SuiteCase.objects.create(case=case, suite=suite)

