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
Tests for Result model.

"""
from django.test import TestCase

from ...core.builders import create_user
from ...environments.builders import create_environment, create_element
from ...library.builders import create_caseversion
from ..builders import (
    create_result, create_stepresult, create_runcaseversion, create_run)



class ResultTest(TestCase):
    @property
    def Result(self):
        from cc.execution.models import Result
        return Result


    def test_unicode(self):
        c = create_result(
            status=self.Result.STATUS.started,
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
            u"Case 'Open URL' included in run 'FF10', "
            "run by tester in English, OS X: started")


    def test_bug_urls(self):
        """Result.bug_urls aggregates bug urls from step results, sans dupes."""
        r = create_result()
        create_stepresult(result=r)
        create_stepresult(result=r, bug_url="http://www.example.com/bug1")
        create_stepresult(result=r, bug_url="http://www.example.com/bug1")
        create_stepresult(result=r, bug_url="http://www.example.com/bug2")

        self.assertEqual(
            r.bug_urls(),
            set(["http://www.example.com/bug1", "http://www.example.com/bug2"])
            )
