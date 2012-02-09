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

from ....library.jsonparse import JsonParser

class Command(BaseCommand):
    args = '<product_name> <product_version> <filename>'
    help = 'Imports the cases from the JSON file into the specified Product Version'


    def handle(self, *args, **options):

        try:
            json_text = open(args[2])
        except IOError as (errno, strerror):
            raise CommandError("I/O error({0}): {1}".format(errno, strerror))

        self.stdout.write(JsonParser().parse(args[0], args[1], json_text))
