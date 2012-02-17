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
from django.db import transaction

from ..core.models import Product, ProductVersion
from ..tags.models import Tag
from models import Case, CaseVersion, CaseStep, Suite, SuiteCase

""" Importer for json suites and cases either from a management command, the UI
    or an external API.
"""

class CaseImporter(object):
    """
    Importer for Suites and Cases.  The object should be structured like this.
    The "suites" section is optional:

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
                    "steps": [
                        {
                            "action": "action text",
                            "expected": "expected text"
                        },
                    ]
                }
            ]
        }

    Instantiate a ``JsonParser`` and call its ``parse`` method::

        importer = CaseImporter()
        data = importer.import_cases(product_name, product_version, case_data)

    Returned data will be the count of cases imported and/or possibly
    an "error" key containing an error message encountered in parsing.

    """
    @transaction.commit_on_success
    def import_cases(self, product_name, product_version, case_data):

        """ Parse given json text and import it into the database. Then return
            the status string of number of imported cases, or an error.
        """

        try:
            product = Product.objects.get(name=product_name)

        except Product.DoesNotExist:
            raise CommandError('Product "%s" does not exist' % product_name)

        try:
            product_version = ProductVersion.objects.get(version=product_version)

        except ProductVersion.DoesNotExist:
            raise CommandError('Product Version "%s" does not exist' %
                product_version)


        self.import_suites(product, case_data['suites'])

        # the total number of test cases that were imported
        num_cases = 0

        # the result of what was done.
        result_str = ''

        for new_case in case_data['cases']:
            # Don't re-import if we have the same case name and Product Version
            if not CaseVersion.objects.filter(name=new_case['name'],
                                              productversion=product_version
                                              ).exists():

                # create the top-level case object which holds the versions
                case = Case()
                case.product=product
                case.save()

                # create the case version which holds the details
                case_version = CaseVersion()
                case_version.productversion = product_version
                case_version.case = case
                case_version.name = new_case['name']
                case_version.description = new_case['description']

                case_version.save()

                # add the steps to this case version
                self.import_steps(case_version, new_case['steps'])

                # add tags to this case version,
                # create tags as product specific
                self.import_tags(product, case_version, new_case['tags'])

                # add this case to the suites
                # if the suites don't exist, create them
                self.import_suites(product, new_case['suites'], case)


                # case has been created, increment our count for reporting
                num_cases+=1

            else:
                result_str += ('skipping: product version "%s" already has a case named "%s".\n' %
                    (product_version.name, new_case['name']))

        result_str += ('Successfully imported %s cases.\n' %
            (num_cases))

        return(result_str)


    def import_steps(self, case_version, step_list):
        """ add the steps to this case version"""

        for step_num, new_step in enumerate(step_list):
            casestep = CaseStep()
            casestep.caseversion = case_version
            casestep.number = step_num+1
            casestep.instruction = new_step['instruction']
            casestep.expected = new_step['expected']
            casestep.save()


    def import_tags(self, product, case_version, tag_list):
        """ Find the tag.  If it doesn't exist, then create it as product specific.
            Either way, add it to the case_version"""

        for new_tag in tag_list:
            try:
               tag = Tag.objects.get(name=new_tag, product=product)

            except Tag.DoesNotExist:
               tag = Tag()
               tag.product=product
               tag.name = new_tag
               tag.save()

            case_version.tags.add(tag)

    def import_suites(self, product, suite_list, case=None):
        """ Create each suite in the list, if it doesn't already exist.
            If a case is provided, add that case to the suite."""

        for new_suite in suite_list:
            # this could be a dictionary, if it's in the "suites" object
            # or just a list of strings if it's listed for an individual case

            if isinstance(new_suite, dict):
                new_name = new_suite['name']
                new_desc = new_suite['description']
            else:
                new_name = new_suite
                new_desc = None

            try:
                suite = Suite.objects.get(name=new_name, product=product)

            except Suite.DoesNotExist:

                suite = Suite()
                suite.product=product
                suite.name = new_name
                if new_desc:
                    suite.description = new_desc
                suite.save()

            # if a case is provided, add it to this suite
            if case:
                SuiteCase.objects.create(case=case, suite=suite)
