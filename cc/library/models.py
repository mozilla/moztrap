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
Models for test-case library (cases, suites).

"""
from django.db import models

from model_utils import Choices

from ..attachments.models import Attachment
from ..core.ccmodel import CCModel
from ..core.models import Product



class Case(CCModel):
    """A test case for a given product."""
    product = models.ForeignKey(Product, related_name="cases")


    def __unicode__(self):
        return "case #%s" % (self.id,)



class CaseVersion(CCModel):
    """A version of a test case."""
    STATUS = Choices("draft", "active", "disabled")

    status = models.CharField(
        max_length=30, db_index=True, choices=STATUS, default=STATUS.draft)
    case = models.ForeignKey(Case, related_name="versions")
    number = models.PositiveIntegerField(db_index=True)
    latest = models.BooleanField(default=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)


    def __unicode__(self):
        return self.name


    class Meta:
        ordering = ["number"]



class CaseAttachment(Attachment):
    caseversion = models.ForeignKey(CaseVersion)



class CaseStep(CCModel):
    """A step of a test case."""
    caseversion = models.ForeignKey(CaseVersion, related_name="steps")
    number = models.IntegerField()
    instruction = models.TextField()
    expected = models.TextField(blank=True)


    def __unicode__(self):
        return u"step #%s" % (self.number,)


    class Meta:
        ordering = ["caseversion", "number"]
        unique_together = [("caseversion", "number")]



class Suite(CCModel):
    """An ordered suite of test cases."""
    STATUS = Choices("draft", "active", "disabled")

    status = models.CharField(
        max_length=30, db_index=True, choices=STATUS, default=STATUS.draft)
    product = models.ForeignKey(Product, related_name="suites")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    cases = models.ManyToManyField(
        Case, through="SuiteCase", related_name="suites")


    def __unicode__(self):
        return self.name



class SuiteCase(CCModel):
    """Association between a test case and a suite."""
    suite = models.ForeignKey(Suite)
    case = models.ForeignKey(Case)
    order = models.IntegerField(default=0, db_index=True)


    class Meta:
        ordering = ["order"]
