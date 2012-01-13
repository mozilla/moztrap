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
Tests for Run model.

"""
import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from ... import factories as F



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
