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
Models for test execution (cycles, runs, results).

"""
import datetime

from django.core.exceptions import ValidationError
from django.db import models

from django.contrib.auth.models import User

from model_utils import Choices

from ..core.ccmodel import CCModel, utcnow
from ..core.models import Product
from ..environments.models import Environment
from ..library.models import CaseVersion, Suite, CaseStep



class Cycle(CCModel):
    """A test cycle."""
    STATUS = Choices("draft", "active", "disabled")

    product = models.ForeignKey(Product, related_name="cycles")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=30, db_index=True, choices=STATUS, default=STATUS.draft)
    start = models.DateField(default=datetime.date.today)
    end = models.DateField(blank=True, null=True)


    def __unicode__(self):
        """Return unicode representation."""
        return self.name


    def clean(self):
        """Validate instance field values."""
        if self.end is not None and self.start > self.end:
            raise ValidationError("Start date must be prior to end date.")



class Run(CCModel):
    """A test run."""
    STATUS = Choices("draft", "active", "disabled")

    cycle = models.ForeignKey(Cycle, related_name="runs")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=30, db_index=True, choices=STATUS, default=STATUS.draft)
    start = models.DateField(default=datetime.date.today)
    end = models.DateField(blank=True, null=True)

    caseversions = models.ManyToManyField(
        CaseVersion, through="RunCaseVersion", related_name="runs")
    suites = models.ManyToManyField(
        Suite, through="RunSuite", related_name="runs")


    def __unicode__(self):
        """Return unicode representation."""
        return self.name


    def clean(self):
        """Validate instance field values."""
        if self.end is not None and self.start > self.end:
            raise ValidationError("Start date must be prior to end date.")



class RunCaseVersion(CCModel):
    """An ordered association between a Run and a CaseVersion."""
    run = models.ForeignKey(Run)
    caseversion = models.ForeignKey(CaseVersion)
    order = models.IntegerField(default=0, db_index=True)


    def __unicode__(self):
        """Return unicode representation."""
        return "Case '%s' included in run '%s'" % (self.caseversion, self.run)



class RunSuite(CCModel):
    """An ordered association between a Run and a Suite."""
    run = models.ForeignKey(Run)
    suite = models.ForeignKey(Suite)
    order = models.IntegerField(default=0, db_index=True)


    def __unicode__(self):
        """Return unicode representation."""
        return "Suite '%s' included in run '%s'" % (self.suite, self.run)



class Result(CCModel):
    """A result of a User running a RunCaseVersion in an Environment."""
    STATUS = Choices("assigned", "started", "passed", "failed", "invalidated")
    REVIEW = Choices("pending", "reviewed")

    tester = models.ForeignKey(User, related_name="results")
    runcaseversion = models.ForeignKey(
        RunCaseVersion, related_name="results")
    environment = models.ForeignKey(Environment, related_name="results")
    status = models.CharField(
        max_length=50, db_index=True, choices=STATUS, default=STATUS.assigned)
    started = models.DateTimeField(default=utcnow)
    completed = models.DateTimeField(blank=True, null=True)
    comment = models.TextField(blank=True)

    review = models.CharField(
        max_length=50, db_index=True, choices=REVIEW, default=REVIEW.pending)
    reviewed_on = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        User, related_name="reviews", blank=True, null=True)


    def __unicode__(self):
        """Return unicode representation."""
        return "%s, run by %s in %s: %s" % (
            self.runcaseversion, self.tester, self.environment, self.status)




class StepResult(CCModel):
    """A result of a particular step in a test case."""
    STATUS = Choices("passed", "failed", "invalidated")

    result = models.ForeignKey(Result, related_name="stepresults")
    step = models.ForeignKey(CaseStep, related_name="stepresults")
    status = models.CharField(
        max_length=50, db_index=True, choices=STATUS, default=STATUS.passed)


    def __unicode__(self):
        """Return unicode representation."""
        return "%s (%s: %s)" % (self.result, self.step, self.status)
