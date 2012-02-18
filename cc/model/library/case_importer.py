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
"""Importer suites and cases from a dictionary."""

from django.db import transaction

from ..core.models import Product, ProductVersion
from ..core.auth import User
from ..tags.models import Tag
from .models import Case, CaseVersion, CaseStep, Suite, SuiteCase


class CaseImporter(object):
    """
    Importer for Suites and Cases.  The object should be structured like this.
    The "suites" section is optional::

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
        data = importer.import_data(product_name, product_version, case_data)

    Returned data will be the count of cases imported and/or possibly
    an "error" key containing an error message encountered in parsing.

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
        self.skipped=[]
        self.warnings=[]

        if 'suites' in case_data:
            self.import_suites(product_version.product, case_data['suites'])

        # no reason why the data couldn't include ONLY suites.  So function
        # gracefully if no cases.
        if 'cases' in case_data:
            self.import_cases(product_version, case_data['cases'])

        return {"cases": self.num_cases,
                "suites": self.num_suites,
                "skipped": skipped,
                "warnings": warnings}

    def import_cases(self, product_version, case_list):
        """
        Import the cases section of case_data.  This may include suites that each
        case belongs to.

        """

        for new_case in case_list:
            if not 'name' in new_case:
                self.skipped.append('"name" field required for a case: {1}'.format(new_case))
                continue

            # Don't re-import if we have the same case name and Product Version
            if CaseVersion.objects.filter(name=new_case['name'],
                                          productversion=product_version
                                          ).exists():

                self.skipped.append('product version "{1}" already has a case named "{2}".'.format(
                    product_version.name, new_case['name']))
                continue


            # create the top-level case object which holds the versions
            case = Case.objects.create(product=product)

            # create the case version which holds the details
            case_version = CaseVersion.objects.create(productversion = product_version,
                                                      case = case,
                                                      name = new_case['name'],
                                                      description = new_case.get('description', None))


            if 'created_by' in new_case:
                try:
                    user = User.objects.get(email=new_case['created_by'])
                    case_version.created_by = user
                    case_version.save()

                except User.DoesNotExist:
                    result_str += 'user with email "{1}" does not exist. Setting created_by to None for {2}\n'.format(
                        new_case['created_by'], new_case['name'])



            # add the steps to this case version
            if 'steps' in new_case:
                self.import_steps(case_version, new_case['steps'])
            else:
                warnings.append("case has no steps: {1}".format(case_version))

            # add tags to this case version,
            # create tags as product specific
            if 'tags' in new_case:
                self.import_tags(product, case_version, new_case['tags'])

            # add this case to the suites
            # if the suites don't exist, create them
            if 'suites' in new_case:
                self.import_suites(product,
                                   [{"name": x} for x in new_case['suites']],
                                   case)


            # case has been created, increment our count for reporting
            self.num_cases+=1




    def import_steps(self, case_version, step_data):
        """
        Add the steps to this case version.
        Instruction is a required field for a step, but expected is optional.

        """

        for step_num, new_step in enumerate(step_data):
            if 'instruction' in new_step:
                casestep = CaseStep.objects.create(caseversion = case_version,
                                                   number = step_num+1,
                                                   instruction = new_step['instruction'],
                                                   expected = new_step.get('expected', None)
            else:
                raise ValueError("instruction required for every step: {1}".format(
                    new_step
                ))

    def import_tags(self, product, case_version, tag_list):
        """
        Find the tag.  If it doesn't exist, then create it as product specific.
        Either way, add it to the case_version

        """

        for new_tag in tag_list:
            tag, created = Tag.objects.get_or_create(name=new_tag)

            # if we created this here, make it product specific
            if created:
                tag.product=product
                tag.save()

            case_version.tags.add(tag)

    def import_suites(self, product, suite_data, case=None):
        """
        Create each suite in the list, if it doesn't already exist.
        If a case is provided, add that case to the suite.

        """

        for new_suite in suite_data:
            # this could be a dictionary, if it's in the "suites" object
            # or just a list of strings if it's listed for an individual case

            if not 'name' in new_suite:
                skipped.append('can\'t import suite "{1}" without a name').format(
                               new_suite)
                    continue

            suite, created = Suite.objects.get_or_create(name=new_name, product=product)
            if not suite.description:
                suite.description = new_suite.get('description', None)
            suite.save()

            if created:
                self.num_suites +=1

            # if a case is provided, add it to this suite
            if case:
                SuiteCase.objects.create(case=case, suite=suite)
