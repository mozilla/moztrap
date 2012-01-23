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
Tests for StepResult model.

"""
from django.test import TestCase

from ... import factories as F

from cc.execution.models import Result, StepResult



class StepResultTest(TestCase):
    def test_unicode(self):
        env = F.EnvironmentFactory.create_full_set(
            {"OS": ["OS X"], "Language": ["English"]})[0]

        step = F.CaseStepFactory.create(
            caseversion__name="Open URL")

        sr = F.StepResultFactory.create(
            status=StepResult.STATUS.passed,
            step=step,
            result__status=Result.STATUS.started,
            result__runcaseversion__run__name="FF10",
            result__runcaseversion__caseversion=step.caseversion,
            result__tester__username="tester",
            result__environment=env,
            )

        self.assertEqual(
            unicode(sr),
            u"Case 'Open URL' included in run 'FF10', "
            "run by tester in English, OS X: started (step #%s: passed)"
            % step.number)
