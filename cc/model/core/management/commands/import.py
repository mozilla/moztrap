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
"""
Import Suite and Case data for a given Product Version.

The "suites" or "cases" sections are optional.
The data must be in JSON format and structured like this::

    {
        "suites": [
            {
                "name": "suite1 name",
                "description": "suite description"
            }
        ]
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
                    }
                ]
            }
        ]
    }

"""

from django.core.management.base import BaseCommand, CommandError

import json

from cc.model.core.models import Product, ProductVersion
from cc.model.library.importer import Importer, ImportResult



class Command(BaseCommand):
    args = "<product_name> <product_version> <filename>"
    help = ("Imports the cases from a JSON file into "
            "the specified Product Version")


    def handle(self, *args, **options):
        if not len(args) == 3:
            raise CommandError("Usage: {0}".format(self.args))

        try:
            product = Product.objects.get(name=args[0])

        except Product.DoesNotExist:
            raise CommandError('Product "{0}" does not exist'.format(
                args[0]))

        try:
            product_version = ProductVersion.objects.get(
                product=product, version=args[1])

        except ProductVersion.DoesNotExist:
            raise CommandError(
                'Product Version "{0}" does not exist'.format(
                product_version))

        try:
            with open(args[2]) as cases_text:

                # try to import this as JSON
                try:
                    case_data = json.load(cases_text)

                except ValueError as e:
                    raise CommandError(
                        "Could not parse JSON because {0}".format(str(e)))

                # @@@: support importing as CSV.  Rather than returning an
                # error above, just try CSV import instead.


                result_list = Importer().import_data(
                    product_version, case_data).get_as_list()
                result_list.append("")

                self.stdout.write("\n".join(result_list))


        except IOError as (errno, strerror):
            raise CommandError("I/O error({0}): {1}".format(errno, strerror))
