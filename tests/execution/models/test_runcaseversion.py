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

from ... import factories as F



class RunCaseVersionTest(TestCase):
    def test_unicode(self):
        c = F.RunCaseVersionFactory(
            run__name="FF10", caseversion__name="Open URL")

        self.assertEqual(unicode(c), u"Case 'Open URL' included in run 'FF10'")


    def test_bug_urls(self):
        """bug_urls aggregates bug urls from all results, sans dupes."""
        rcv = F.RunCaseVersionFactory.create()
        result1 = F.ResultFactory.create(runcaseversion=rcv)
        result2 = F.ResultFactory.create(runcaseversion=rcv)
        F.StepResultFactory.create(result=result1)
        F.StepResultFactory.create(
            result=result1, bug_url="http://www.example.com/bug1")
        F.StepResultFactory.create(
            result=result2, bug_url="http://www.example.com/bug1")
        F.StepResultFactory.create(
            result=result2, bug_url="http://www.example.com/bug2")

        self.assertEqual(
            rcv.bug_urls(),
            set(["http://www.example.com/bug1", "http://www.example.com/bug2"])
            )


    def test_environment_inheritance(self):
        """RCV gets intersection of run and caseversion environments."""
        envs = F.EnvironmentFactory.create_set(
            ["OS", "Browser"],
            ["Linux", "Firefox"],
            ["Linux", "Chrome"],
            ["OS X", "Chrome"],
            )

        rcv = F.RunCaseVersionFactory.create(
            run__environments=envs[:2],
            caseversion__environments=envs[1:])

        self.assertEqual(rcv.environments.get(), envs[1])

        # only happens when first created, not on later saves

        rcv.environments.clear()
        rcv.save()

        self.assertEqual(rcv.environments.count(), 0)
