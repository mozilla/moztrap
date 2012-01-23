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


    def test_inherits_env_removal_from_run(self):
        """RCV inherits env removal from test run."""
        envs = F.EnvironmentFactory.create_full_set({"OS": ["OS X", "Linux"]})
        r = F.RunFactory(environments=envs)
        cv = F.CaseVersionFactory(environments=envs)
        rcv = F.RunCaseVersionFactory(run=r, caseversion=cv)

        r.remove_envs(envs[0])

        self.assertEqual(set(rcv.environments.all()), set(envs[1:]))


    def test_does_not_inherit_env_addition_on_run(self):
        """RCV does not inherit env addition on test run."""
        envs = F.EnvironmentFactory.create_full_set({"OS": ["OS X", "Linux"]})
        r = F.RunFactory(environments=envs[1:])
        cv = F.CaseVersionFactory(environments=envs)
        rcv = F.RunCaseVersionFactory(run=r, caseversion=cv)

        r.add_envs(envs[0])

        self.assertEqual(set(rcv.environments.all()), set(envs[1:]))


    def test_inherits_env_removal_from_productversion(self):
        """RCV inherits env removal from product version."""
        envs = F.EnvironmentFactory.create_full_set({"OS": ["OS X", "Linux"]})
        pv = F.ProductVersionFactory(environments=envs)
        cv = F.CaseVersionFactory(environments=envs)
        rcv = F.RunCaseVersionFactory(run__productversion=pv, caseversion=cv)

        pv.remove_envs(envs[0])

        self.assertEqual(set(rcv.environments.all()), set(envs[1:]))


    def test_inherits_env_removal_from_caseversion(self):
        """RCV inherits env removal from caseversion."""
        envs = F.EnvironmentFactory.create_full_set({"OS": ["OS X", "Linux"]})
        r = F.RunFactory(environments=envs)
        cv = F.CaseVersionFactory(environments=envs)
        rcv = F.RunCaseVersionFactory(run=r, caseversion=cv)

        cv.remove_envs(envs[0])

        self.assertEqual(set(rcv.environments.all()), set(envs[1:]))


    def test_does_not_inherit_env_addition_to_caseversion(self):
        """RCV does not inherit env added to caseversion."""
        envs = F.EnvironmentFactory.create_full_set({"OS": ["OS X", "Linux"]})
        r = F.RunFactory(environments=envs)
        cv = F.CaseVersionFactory(environments=envs[1:])
        rcv = F.RunCaseVersionFactory(run=r, caseversion=cv)

        cv.add_envs(envs[0])

        self.assertEqual(set(rcv.environments.all()), set(envs[1:]))


    def test_result_summary(self):
        """``result_summary`` returns dict summarizing result states."""
        rcv = F.RunCaseVersionFactory()

        F.ResultFactory(runcaseversion=rcv, status="assigned")
        F.ResultFactory(runcaseversion=rcv, status="started")
        F.ResultFactory(runcaseversion=rcv, status="passed")
        F.ResultFactory(runcaseversion=rcv, status="failed")
        F.ResultFactory(runcaseversion=rcv, status="failed")
        F.ResultFactory(runcaseversion=rcv, status="invalidated")
        F.ResultFactory(runcaseversion=rcv, status="invalidated")
        F.ResultFactory(runcaseversion=rcv, status="invalidated")

        self.assertEqual(
            rcv.result_summary(),
            {
                "passed": 1,
                "failed": 2,
                "invalidated": 3,
                }
            )

    def test_result_summary_empty(self):
        """Empty slots in result summary still contain 0."""
        rcv = F.RunCaseVersionFactory()

        self.assertEqual(
            rcv.result_summary(),
            {
                "passed": 0,
                "failed": 0,
                "invalidated": 0,
                }
            )


    def test_completion_percentage(self):
        """``completion`` returns fraction of envs completed."""
        envs = F.EnvironmentFactory.create_full_set(
            {"OS": ["Windows", "Linux"]})
        rcv = F.RunCaseVersionFactory(environments=envs)

        F.ResultFactory(
            runcaseversion=rcv, environment=envs[0], status="passed")
        F.ResultFactory(
            runcaseversion=rcv, environment=envs[0], status="failed")
        F.ResultFactory(
            runcaseversion=rcv, environment=envs[1], status="started")

        self.assertEqual(rcv.completion(), 0.5)


    def test_completion_percentage_empty(self):
        """If no envs, ``completion`` returns zero."""
        rcv = F.RunCaseVersionFactory()

        self.assertEqual(rcv.completion(), 0)
