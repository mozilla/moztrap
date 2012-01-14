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
Tests for Run model.

"""
import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from ... import factories as F
from ...utils import refresh



class RunTest(TestCase):
    def test_unicode(self):
        r = F.RunFactory(name="Firefox 10 final run")

        self.assertEqual(unicode(r), u"Firefox 10 final run")


    def test_invalid_dates(self):
        """Run validates that start date is not after end date."""
        today = datetime.date(2011, 12, 13)
        r = F.RunFactory(
            start=today,
            end=today-datetime.timedelta(days=1))

        with self.assertRaises(ValidationError):
            r.full_clean()


    def test_valid_dates(self):
        """Run validation allows start date before or same as end date."""
        today = datetime.date(2011, 12, 13)
        r = F.RunFactory(
            start=today,
            end=today+datetime.timedelta(days=1))

        r.full_clean()


    def test_parent(self):
        """A Run's ``parent`` property returns its ProductVersion."""
        r = F.RunFactory()

        self.assertIs(r.parent, r.productversion)


    def test_own_team(self):
        """If ``has_team`` is True, Run's team is its own."""
        r = F.RunFactory.create(has_team=True)
        u = F.UserFactory.create()
        r.own_team.add(u)

        self.assertEqual(list(r.team.all()), [u])


    def test_inherit_team(self):
        """If ``has_team`` is False, Run's team is its parent's."""
        r = F.RunFactory.create(has_team=False)
        u = F.UserFactory.create()
        r.productversion.team.add(u)

        self.assertEqual(list(r.team.all()), [u])


    def test_clone(self):
        """Cloning a run returns a new, distinct Run with "Cloned: " name."""
        r = F.RunFactory.create(name="A Run")

        new = r.clone()

        self.assertNotEqual(new, r)
        self.assertIsInstance(new, type(r))
        self.assertEqual(new.name, "Cloned: A Run")


    def test_clone_included_suite(self):
        """Cloning a run clones member RunSuites."""
        rs = F.RunSuiteFactory.create()

        new = rs.run.clone()

        self.assertNotEqual(new.runsuites.get(), rs)


    def test_clone_included_caseversion(self):
        """Cloning a run clones all member RunCaseVersions."""
        rcv = F.RunCaseVersionFactory.create()

        new = rcv.run.clone()

        self.assertNotEqual(new.runcaseversions.get(), rcv)


    def test_clone_environments(self):
        """Cloning a Run clones its environments."""
        r = F.RunFactory(environments={"OS": ["OS X", "Linux"]})

        new = r.clone()

        self.assertEqual(len(new.environments.all()), 2)


    def test_clone_team(self):
        """Cloning a Run clones its team."""
        r = F.RunFactory(team=["One", "Two"])

        new = r.clone()

        self.assertEqual(len(new.team.all()), 2)


    def test_clone_no_results(self):
        """Cloning a run does not clone any results."""
        r = F.ResultFactory.create()

        new = r.runcaseversion.run.clone()

        self.assertEqual(new.runcaseversions.get().results.count(), 0)


    def test_gets_productversion_envs(self):
        """A new test run inherits the environments of its product version."""
        pv = F.ProductVersionFactory.create(
            environments={"OS": ["Windows", "Linux"]})

        r = F.RunFactory.create(productversion=pv)

        self.assertEqual(set(r.environments.all()), set(pv.environments.all()))


    def test_inherits_env_removal(self):
        """Removing an env from a productversion cascades to run."""
        envs = F.EnvironmentFactory.create_full_set({"OS": ["OS X", "Linux"]})
        pv = F.ProductVersionFactory.create(environments=envs)
        run = F.RunFactory.create(productversion=pv)

        pv.remove_envs(envs[0])

        self.assertEqual(set(run.environments.all()), set(envs[1:]))


    def test_draft_run_inherits_env_addition(self):
        """Adding an env to a productversion cascades to a draft run."""
        envs = F.EnvironmentFactory.create_full_set({"OS": ["OS X", "Linux"]})
        pv = F.ProductVersionFactory.create(environments=envs[1:])
        run = F.RunFactory.create(productversion=pv, status="draft")

        pv.add_envs(envs[0])

        self.assertEqual(set(run.environments.all()), set(envs))


    def test_active_run_does_not_inherit_env_addition(self):
        """Adding env to a productversion does not cascade to an active run."""
        envs = F.EnvironmentFactory.create_full_set({"OS": ["OS X", "Linux"]})
        pv = F.ProductVersionFactory.create(environments=envs[1:])
        run = F.RunFactory.create(productversion=pv, status="active")

        pv.add_envs(envs[0])

        self.assertEqual(set(run.environments.all()), set(envs[1:]))


    def test_result_summary(self):
        """``result_summary`` returns dict summarizing result states."""
        r = F.RunFactory()
        rcv1 = F.RunCaseVersionFactory(run=r)
        rcv2 = F.RunCaseVersionFactory(run=r)

        F.ResultFactory(runcaseversion=rcv1, status="assigned")
        F.ResultFactory(runcaseversion=rcv2, status="started")
        F.ResultFactory(runcaseversion=rcv1, status="passed")
        F.ResultFactory(runcaseversion=rcv2, status="failed")
        F.ResultFactory(runcaseversion=rcv1, status="failed")
        F.ResultFactory(runcaseversion=rcv2, status="invalidated")
        F.ResultFactory(runcaseversion=rcv1, status="invalidated")
        F.ResultFactory(runcaseversion=rcv2, status="invalidated")

        self.assertEqual(
            r.result_summary(),
            {
                "passed": 1,
                "failed": 2,
                "invalidated": 3
                }
            )


    def test_completion_percentage(self):
        """``completion`` returns fraction of case/env combos completed."""
        envs = F.EnvironmentFactory.create_full_set(
            {"OS": ["Windows", "Linux"]})
        pv = F.ProductVersionFactory(environments=envs)
        run = F.RunFactory(productversion=pv)
        rcv1 = F.RunCaseVersionFactory(
            run=run, caseversion__productversion=pv)
        rcv2 = F.RunCaseVersionFactory(
            run=run, caseversion__productversion=pv)

        F.ResultFactory(
            runcaseversion=rcv1, environment=envs[0], status="passed")
        F.ResultFactory(
            runcaseversion=rcv1, environment=envs[0], status="failed")
        F.ResultFactory(
            runcaseversion=rcv2, environment=envs[1], status="started")

        self.assertEqual(run.completion(), 0.25)


    def test_completion_percentage_empty(self):
        """If no runcaseversions, ``completion`` returns zero."""
        run = F.RunFactory()

        self.assertEqual(run.completion(), 0)



class RunActivationTest(TestCase):
    """Tests for activating runs and locking-in runcaseversions."""
    def setUp(self):
        """Set up envs, product and product versions used by all tests."""
        self.envs = F.EnvironmentFactory.create_full_set(
            {"OS": ["Linux", "Windows"], "Browser": ["Firefox", "Chrome"]})
        self.p = F.ProductFactory.create()
        self.pv8 = F.ProductVersionFactory.create(
            product=self.p, version="8.0", environments=self.envs)
        self.pv9 = F.ProductVersionFactory.create(
            product=self.p, version="9.0", environments=self.envs)



    def assertCaseVersions(self, run, caseversions):
        """Assert that ``run`` has (only) ``caseversions`` in it (any order)."""
        self.assertEqual(
            set([rcv.caseversion.id for rcv in run.runcaseversions.all()]),
            set([cv.id for cv in caseversions])
            )


    def assertOrderedCaseVersions(self, run, caseversions):
        """Assert that ``run`` has (only) ``caseversions`` in it (in order)."""
        self.assertEqual(
            [rcv.caseversion.id for rcv in run.runcaseversions.all()],
            [cv.id for cv in caseversions]
            )


    def test_productversion(self):
        """Selects test case version for run's product version."""
        tc = F.CaseFactory.create(product=self.p)
        tcv1 = F.CaseVersionFactory.create(
            case=tc, productversion=self.pv8, status="active")
        F.CaseVersionFactory.create(
            case=tc, productversion=self.pv9, status="active")

        ts = F.SuiteFactory.create(product=self.p)
        F.SuiteCaseFactory.create(suite=ts, case=tc)

        r = F.RunFactory.create(productversion=self.pv8)
        F.RunSuiteFactory.create(suite=ts, run=r)

        r.activate()

        self.assertCaseVersions(r, [tcv1])


    def test_draft_not_included(self):
        """Only active test cases are considered."""
        tc = F.CaseFactory.create(product=self.p)
        F.CaseVersionFactory.create(
            case=tc, productversion=self.pv8, status="draft")

        ts = F.SuiteFactory.create(product=self.p)
        F.SuiteCaseFactory.create(suite=ts, case=tc)

        r = F.RunFactory.create(productversion=self.pv8)
        F.RunSuiteFactory.create(suite=ts, run=r)

        r.activate()

        self.assertCaseVersions(r, [])


    def test_wrong_product_version_not_included(self):
        """Only caseversions for correct productversion are considered."""
        tc = F.CaseFactory.create(product=self.p)
        F.CaseVersionFactory.create(
            case=tc, productversion=self.pv9, status="active")

        ts = F.SuiteFactory.create(product=self.p)
        F.SuiteCaseFactory.create(suite=ts, case=tc)

        r = F.RunFactory.create(productversion=self.pv8)
        F.RunSuiteFactory.create(suite=ts, run=r)

        r.activate()

        self.assertCaseVersions(r, [])


    def test_no_environments_in_common(self):
        """Caseversion with no env overlap with run will not be included."""
        self.pv8.environments.add(*self.envs)

        tc = F.CaseFactory.create(product=self.p)
        tcv1 = F.CaseVersionFactory.create(
            case=tc, productversion=self.pv8, status="active")
        tcv1.remove_envs(*self.envs[:2])

        ts = F.SuiteFactory.create(product=self.p)
        F.SuiteCaseFactory.create(suite=ts, case=tc)

        r = F.RunFactory.create(productversion=self.pv8)
        r.remove_envs(*self.envs[2:])
        F.RunSuiteFactory.create(suite=ts, run=r)

        r.activate()

        self.assertCaseVersions(r, [])


    def test_ordering(self):
        """Suite/case ordering reflected in runcaseversion order."""
        tc1 = F.CaseFactory.create(product=self.p)
        tcv1 = F.CaseVersionFactory.create(
            case=tc1, productversion=self.pv8, status="active")
        tc2 = F.CaseFactory.create(product=self.p)
        tcv2 = F.CaseVersionFactory.create(
            case=tc2, productversion=self.pv8, status="active")
        tc3 = F.CaseFactory.create(product=self.p)
        tcv3 = F.CaseVersionFactory.create(
            case=tc3, productversion=self.pv8, status="active")

        ts1 = F.SuiteFactory.create(product=self.p)
        F.SuiteCaseFactory.create(suite=ts1, case=tc3, order=1)
        ts2 = F.SuiteFactory.create(product=self.p)
        F.SuiteCaseFactory.create(suite=ts2, case=tc2, order=1)
        F.SuiteCaseFactory.create(suite=ts2, case=tc1, order=2)

        r = F.RunFactory.create(productversion=self.pv8)
        F.RunSuiteFactory.create(suite=ts2, run=r, order=1)
        F.RunSuiteFactory.create(suite=ts1, run=r, order=2)

        r.activate()

        self.assertOrderedCaseVersions(r, [tcv2, tcv1, tcv3])


    def test_sets_status_active(self):
        """Sets status of run to active."""
        r = F.RunFactory.create(status="draft")

        r.activate()

        self.assertEqual(refresh(r).status, "active")


    def test_already_active(self):
        """Has no effect on already-active run."""
        tc = F.CaseFactory.create(product=self.p)
        F.CaseVersionFactory.create(
            case=tc, productversion=self.pv8, status="active")

        ts = F.SuiteFactory.create(product=self.p)
        F.SuiteCaseFactory.create(suite=ts, case=tc)

        r = F.RunFactory.create(productversion=self.pv8, status="active")
        F.RunSuiteFactory.create(suite=ts, run=r)

        r.activate()

        self.assertCaseVersions(r, [])


    def test_disabled(self):
        """Sets disabled run to active but does not create runcaseversions."""
        tc = F.CaseFactory.create(product=self.p)
        F.CaseVersionFactory.create(
            case=tc, productversion=self.pv8, status="active")

        ts = F.SuiteFactory.create(product=self.p)
        F.SuiteCaseFactory.create(suite=ts, case=tc)

        r = F.RunFactory.create(productversion=self.pv8, status="disabled")
        F.RunSuiteFactory.create(suite=ts, run=r)

        r.activate()

        self.assertCaseVersions(r, [])
        self.assertEqual(refresh(r).status, "active")
