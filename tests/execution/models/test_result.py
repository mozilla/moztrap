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

from ... import factories as F

from cc.execution.models import Result



class ResultTest(TestCase):
    def test_unicode(self):
        env = F.EnvironmentFactory.create_full_set(
            {"OS": ["OS X"], "Language": ["English"]})[0]

        r = F.ResultFactory(
            status=Result.STATUS.started,
            runcaseversion__run__name="FF10",
            runcaseversion__caseversion__name="Open URL",
            tester__username="tester",
            environment=env,
            )

        self.assertEqual(
            unicode(r),
            u"Case 'Open URL' included in run 'FF10', "
            "run by tester in English, OS X: started")


    def test_bug_urls(self):
        """Result.bug_urls aggregates bug urls from step results, sans dupes."""
        r = F.ResultFactory()
        F.StepResultFactory.create(result=r)
        F.StepResultFactory.create(
            result=r, bug_url="http://www.example.com/bug1")
        F.StepResultFactory.create(
            result=r, bug_url="http://www.example.com/bug1")
        F.StepResultFactory.create(
            result=r, bug_url="http://www.example.com/bug2")

        self.assertEqual(
            r.bug_urls(),
            set(["http://www.example.com/bug1", "http://www.example.com/bug2"])
            )
