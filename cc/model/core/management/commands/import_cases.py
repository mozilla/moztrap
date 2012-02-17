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

from ....library.case_importer import CaseImporter

class Command(BaseCommand):
    args = '<product_name> <product_version> <filename>'
    help = 'Imports the cases from a JSON file into the specified Product Version'


    def handle(self, *args, **options):
        if len(args) < 3:
            raise CommandError("Usage: %s" % self.args)

        try:
            with open(args[2]) as cases_text:

                # try to import this as JSON
                try:
                    case_data = json.load(cases_text)

                except ValueError as (strerror):
                    self.stderr.write('Could not parse the JSON because %s' %
                         strerror)

                # TODO: support importing as CSV.  Rather than returning an error above,
                # just try CSV import instead.

                self.stdout.write(CaseImporter().import_cases(args[0], args[1], case_data))


        except IOError as (errno, strerror):
            raise CommandError("I/O error({0}): {1}".format(errno, strerror))

