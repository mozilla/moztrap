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
"""
Tests for RunSuite model.

"""
from django.test import TestCase

from ...library.builders import create_suite
from ..builders import create_runsuite, create_run



class RunSuiteTest(TestCase):
    @property
    def RunSuite(self):
        from cc.execution.models import RunSuite
        return RunSuite


    def test_unicode(self):
        c = create_runsuite(
            run=create_run(name="FF10"),
            suite=create_suite(name="Speed"))

        self.assertEqual(unicode(c), u"Suite 'Speed' included in run 'FF10'")
