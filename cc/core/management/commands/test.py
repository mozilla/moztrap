# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
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
    option_list = TestCommand.option_list + (
        make_option(
            '--coverage', action='store_true', dest='coverage', default=False,
            help='Report test coverage in htmlcov/.'),
        make_option(
            '--coverall', action='store_true', dest='coverall', default=False,
            help='Report test coverage of all modules, even if not imported.'),
        )
    help = 'Runs the test modules, cases, or methods specified by dotted path on the command line, or does test discovery if no arguments are given.'
    args = '[dotted-path ...]'

    requires_model_validation = False

    def handle(self, *test_labels, **options):
        patch_for_test_db_setup()

        if options.get("coverage"):
            cov = coverage.coverage(branch=True)
            cov.start()

        from django.conf import settings
        from django.test.utils import get_runner

        verbosity = int(options.get('verbosity', 1))
        interactive = options.get('interactive', True)
        failfast = options.get('failfast', False)
        TestRunner = get_runner(settings)

        test_runner = TestRunner(verbosity=verbosity, interactive=interactive, failfast=failfast)
        failures = test_runner.run_tests(test_labels)

        if options.get("coverage"):
            cov.stop()

            include = []
            omit = [
                "*/migrations/*",
                "cc/deploy/wsgi.py",
                "cc/deploy/vendor_wsgi.py"
                ]
            report_kw = {}
            if options.get("coverall"):
                # include all python modules under cc in report, including even
                # those the tests don't cause to be imported at all yet, so as
                # to get a more accurate overall coverage figure.
                py_files = include
                for dirpath, dirs, filenames in os.walk(
                        os.path.join(settings.BASE_PATH, "cc")):
                    py_files.extend([os.path.join(dirpath, fn)
                                     for fn in filenames if fn.endswith(".py")])
                report_kw["morfs"] = py_files
                report_kw["omit"] = omit + [
                    "cc/core/management/commands/test.py",
                    "cc/settings/base.py",
                    "cc/settings/default.py",
                    "cc/settings/local.py",
                    "cc/settings/local.sample.py"]
            else:
                report_kw["include"] = include + [
                    os.path.join(settings.BASE_PATH, "cc/*")]
                report_kw["omit"] = omit
            cov.html_report(**report_kw)

        if failures:
            sys.exit(bool(failures))
