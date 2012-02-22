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
            with open(args[2]) as cases_text:

                # try to import this as JSON
                try:
                    case_data = json.load(cases_text)

                except ValueError as e:
                    raise CommandError(
                        "Could not parse JSON because {0}".format(str(e)))

                # @@@: support importing as CSV.  Rather than returning an
                # error above, just try CSV import instead.


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

                self.write_result(Importer().import_data(
                    product_version, case_data))


        except IOError as (errno, strerror):
            raise CommandError("I/O error({0}): {1}".format(errno, strerror))


    def write_result(self, result):
        """Print the result to the command line."""
        result_list = result.get_as_list()
        result_list.append("")
        self.stdout.write("\n".join(result_list))
