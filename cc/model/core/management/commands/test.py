# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-2012 Mozilla
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
import os, sys
from optparse import make_option

from django.core.management.commands.test import Command as TestCommand

import coverage
from south.management.commands import patch_for_test_db_setup



class Command(TestCommand):
    help = 'Runs the test modules, cases, or methods specified by dotted path on the command line, or does test discovery if no arguments are given.'
    args = '[dotted-path ...]'

    requires_model_validation = False

    def handle(self, *test_labels, **options):
        patch_for_test_db_setup()

        from django.conf import settings
        from django.test.utils import get_runner

        verbosity = int(options.get('verbosity', 1))
        interactive = options.get('interactive', True)
        failfast = options.get('failfast', False)
        TestRunner = get_runner(settings)

        test_runner = TestRunner(verbosity=verbosity, interactive=interactive, failfast=failfast)
        failures = test_runner.run_tests(test_labels)

        sys.exit(bool(failures))
