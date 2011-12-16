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
Tests for Assignment model.

"""
from django.test import TestCase

from ...core.builders import create_user
from ...environments.builders import create_environment, create_element
from ...library.builders import create_caseversion
from ..builders import create_assignment, create_runcaseversion, create_run



class AssignmentTest(TestCase):
    @property
    def Assignment(self):
        from cc.execution.models import Assignment
        return Assignment


    def test_unicode(self):
        c = create_assignment(
            runcaseversion=create_runcaseversion(
                run=create_run(name="FF10"),
                caseversion=create_caseversion(name="Open URL")
                ),
            tester=create_user(username="tester"),
            environment=create_environment(elements=[
                    create_element(name="English"),
                    create_element(name="OS X")
                    ])
            )

        self.assertEqual(
            unicode(c),
            u"Case 'Open URL' included in run 'FF10' "
            "assigned to tester in English, OS X")
