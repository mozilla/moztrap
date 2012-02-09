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

import json

from ..core.models import Product, ProductVersion
from ..tags.models import Tag
from models import Case, CaseVersion, CaseStep, Suite, SuiteCase

""" Parser for json suites and cases either from a management command, the UI
    or an external API.
"""
class ParsingError(Exception):
    pass



class JsonParser(object):
    """
    Parser for JSON Suites and Cases import.

    Parses this format::

        {
            "Suites": [
                {
                    "name": "fucci name",
                    "description": "suite description"
                },
            ],
            "Cases": [
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

        parser = JsonParser()
        data = parser.parse(text)

    Returned data will be the count of Suites and Case imported and/or possibly
    an "error" key containing an error message encountered in parsing.

    """
    @transaction.commit_on_success
    def parse(self, product_name, product_version, json_text):

        """Parse given json text and import it into the database. Then return
        the status string of number of imported suites and cases, or an error.
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

        try:
            json_data = json.load(json_text)
            #self.stdout.write(json.dumps(new_cases, sort_keys=True, indent=4))
        except ValueError as (strerror):
            raise CommandError('Could not parse the JSON because %s' %
                 strerror)


        # the total number of test cases that were imported

        self.parse_suites(product, json_data['suites'])

        num_cases = 0

        for new_case in json_data['cases']:
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
                self.parse_steps(case_version, new_case['steps'])

                # add tags to this case, create tags as product specific
                self.parse_tags(product, case_version, new_case['tags'])

                # add this case to the suites
                self.parse_suites(product, new_case['suites'], case)


                # case has been created, increment our count for reporting
                num_cases+=1

        return ('Successfully imported %s cases.\n' %
            (num_cases))


    def parse_steps(self, case_version, step_list):
        for step_num, new_step in enumerate(step_list):
            casestep = CaseStep()
            casestep.caseversion = case_version
            casestep.number = step_num+1
            casestep.instruction = new_step['instruction']
            casestep.expected = new_step['expected']
            casestep.save()


    def parse_tags(self, product, case_version, tag_list):
        """ Find the tag.  If it doesn't exist, then create it.  Either way,
            add it to the case_version"""

        for new_tag in tag_list:
            try:
               tag = Tag.objects.get(name=new_tag, product=product)

            except Tag.DoesNotExist:
               tag = Tag()
               tag.product=product
               tag.name = new_tag
               tag.save()

            case_version.tags.add(tag)

    def parse_suites(self, product, suite_list, case=None):
        """ create the list of suites, if they don't already exist.
        If a case is provided, add that case to the suites."""

        for new_suite in suite_list:
            # this could be a dictionary, or just a list of strings.
            new_desc = None
            if isinstance(new_suite, dict):
                new_name = new_suite['name']
                new_desc = new_suite['description']
            else:
                new_name = new_suite

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
