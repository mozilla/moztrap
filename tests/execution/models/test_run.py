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

from ...core.builders import create_user
from ...environments.builders import create_environments
from ...library.builders import create_suite, create_caseversion
from ..builders import (
    create_cycle, create_run, create_runsuite, create_runcaseversion,
    create_result)



class RunTest(TestCase):
    @property
    def Run(self):
        from cc.execution.models import Run
        return Run


    def test_unicode(self):
        c = self.Run(name="Firefox 10 final run")

        self.assertEqual(unicode(c), u"Firefox 10 final run")


    def test_invalid_dates(self):
        """Run validates that start date is not after end date."""
        today = datetime.date(2011, 12, 13)
        c = create_run(
            start=today,
            end=today-datetime.timedelta(days=1))

        with self.assertRaises(ValidationError):
            c.full_clean()


    def test_valid_dates(self):
        """Run validation allows start date before or same as end date."""
        today = datetime.date(2011, 12, 13)
        c = create_run(
            start=today,
            end=today+datetime.timedelta(days=1))

        c.full_clean()


    def test_parent(self):
        """A Run's ``parent`` property returns its Cycle."""
        r = create_run()

        self.assertEqual(r.parent, r.cycle)


    def test_own_team(self):
        """If ``has_team`` is True, Run's team is its own."""
        r = create_run(has_team=True)
        u = create_user()
        r.own_team.add(u)

        self.assertEqual(list(r.team.all()), [u])


    def test_inherit_team(self):
        """If ``has_team`` is False, Run's team is its parent's."""
        r = create_run(has_team=False)
        u = create_user()
        r.cycle.team.add(u)

        self.assertEqual(list(r.team.all()), [u])


    def test_clone(self):
        """
        Cloning a run returns a new, distinct Run with "Cloned: " name.

        """
        c = create_run(name="A Run")

        new = c.clone()

        self.assertNotEqual(new, c)
        self.assertIsInstance(new, self.Run)
        self.assertEqual(new.name, "Cloned: A Run")


    def test_clone_included_suite(self):
        """
        Cloning a run clones member RunSuites.

        """
        suite = create_suite()
        run = create_run()
        rs = create_runsuite(run=run, suite=suite)

        new = run.clone()

        self.assertNotEqual(new.runsuites.get(), rs)


    def test_clone_included_caseversion(self):
        """
        Cloning a run clones all member RunCaseVersions.

        """
        caseversion = create_caseversion()
        run = create_run()
        rs = create_runcaseversion(run=run, caseversion=caseversion)

        new = run.clone()

        self.assertNotEqual(new.runcaseversions.get(), rs)


    def test_clone_no_results(self):
        """
        Cloning a run does not clone any results.

        """
        r = create_result()

        new = r.runcaseversion.run.clone()

        self.assertEqual(new.runcaseversions.get().results.count(), 0)


    def test_run_gets_parent_envs(self):
        """
        A new test run inherits the environments of its cycle.

        """
        c = create_cycle()
        c.environments.add(*create_environments(["OS"], ["Windows"], ["Linux"]))

        r = create_run(cycle=c)

        self.assertEqual(set(r.environments.all()), set(c.environments.all()))
