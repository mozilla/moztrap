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
Tests for RunCaseVersion model.

"""
from django.test import TestCase

from ...library.builders import create_caseversion
from ..builders import (
    create_runcaseversion, create_run, create_stepresult, create_result)



class RunCaseVersionTest(TestCase):
    @property
    def RunCaseVersion(self):
        from cc.execution.models import RunCaseVersion
        return RunCaseVersion


    def test_unicode(self):
        c = create_runcaseversion(
            run=create_run(name="FF10"),
            caseversion=create_caseversion(name="Open URL"))

        self.assertEqual(unicode(c), u"Case 'Open URL' included in run 'FF10'")


    def test_bug_urls(self):
        """bug_urls aggregates bug urls from all results, sans dupes."""
        rcv = create_runcaseversion()
        result1 = create_result(runcaseversion=rcv)
        result2 = create_result(runcaseversion=rcv)
        create_stepresult(result=result1)
        create_stepresult(
            result=result1, bug_url="http://www.example.com/bug1")
        create_stepresult(
            result=result2, bug_url="http://www.example.com/bug1")
        create_stepresult(
            result=result2, bug_url="http://www.example.com/bug2")

        self.assertEqual(
            rcv.bug_urls(),
            set(["http://www.example.com/bug1", "http://www.example.com/bug2"])
            )
