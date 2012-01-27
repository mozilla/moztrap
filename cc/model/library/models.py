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
Models for test-case library (cases, suites).

"""
from django.db import models

from ..attachments.models import Attachment
from ..ccmodel import CCModel, DraftStatusModel
from ..core.models import Product, ProductVersion
from ..environments.models import HasEnvironmentsModel
from ..tags.models import Tag



class Case(CCModel):
    """A test case for a given product."""
    product = models.ForeignKey(Product, related_name="cases")


    def __unicode__(self):
        return "case #%s" % (self.id,)


    def clone(self, *args, **kwargs):
        """Clone this Case with default cascade behavior: latest versions."""
        kwargs.setdefault("cascade", ["versions"])
        return super(Case, self).clone(*args, **kwargs)


    def set_latest_version(self, update_instance=None):
        """
        Mark latest version of this case in DB, marking all others non-latest.

        If ``update_instance`` is provided, its ``latest`` flag is updated
        appropriately.

        """
        try:
            latest_version = self.versions.order_by("-productversion__order")[0]
        except IndexError:
            pass
        else:
            self.versions.update(latest=False)
            latest_version.latest = True
            latest_version.save(force_update=True, skip_set_latest=True)
            if update_instance == latest_version:
                update_instance.latest = True
            elif update_instance is not None:
                update_instance.latest = False



    class Meta:
        permissions = [
            ("create_cases", "Can create new test cases."),
            ("manage_cases", "Can add/edit/delete test cases."),
            ]



class CaseVersion(CCModel, DraftStatusModel, HasEnvironmentsModel):
    """A version of a test case."""
    productversion = models.ForeignKey(
        ProductVersion, related_name="caseversions")
    case = models.ForeignKey(Case, related_name="versions")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # denormalized for queries
    latest = models.BooleanField(default=False, editable=False)

    tags = models.ManyToManyField(Tag, blank=True)
    # True if this case's envs have been narrowed from the product version.
    envs_narrowed = models.BooleanField(default=False)


    def __unicode__(self):
        return self.name


    class Meta:
        ordering = ["case", "productversion__order"]
        unique_together = [("productversion", "case")]


    def save(self, *args, **kwargs):
        """Save CaseVersion, updating latest version."""
        skip_set_latest = kwargs.pop("skip_set_latest", False)
        super(CaseVersion, self).save(*args, **kwargs)
        if not skip_set_latest:
            self.case.set_latest_version(update_instance=self)


    def clone(self, *args, **kwargs):
        """
        Clone this CaseVersion, cascading steps, attachments, tags.

        Only one CaseVersion can exist for a given case/productversion
        combination; thus if neither a new case nor a new productversion is
        provided in the ``overrides`` dictionary, a new Case will implicitly be
        cloned and the cloned CaseVersion will be assigned to that new case.

        """
        kwargs.setdefault(
            "cascade", ["steps", "attachments", "tags", "environments"])
        overrides = kwargs.setdefault("overrides", {})
        overrides["status"] = self.STATUS.draft
        if "productversion" not in overrides and "case" not in overrides:
            overrides["case"] = self.case.clone(cascade=[])
        return super(CaseVersion, self).clone(*args, **kwargs)


    @property
    def parent(self):
        return self.productversion


    def remove_envs(self, *envs):
        """
        Remove one or more environments from this caseversion's profile.

        Also sets ``envs_narrowed`` flag.

        """
        super(CaseVersion, self).remove_envs(*envs)
        self.envs_narrowed = True
        self.save()


    @classmethod
    def cascade_envs_to(cls, objs, adding):
        RunCaseVersion = cls.runcaseversions.related.model
        if adding:
            return {}
        return {
            RunCaseVersion: RunCaseVersion.objects.filter(caseversion__in=objs)
            }


    def bug_urls(self):
        """Returns set of bug URLs associated with this caseversion."""
        Result = self.runcaseversions.model.results.related.model
        StepResult = Result.stepresults.related.model
        return set(
            StepResult.objects.filter(
                result__runcaseversion__caseversion=self).exclude(
                bug_url="").values_list("bug_url", flat=True).distinct()
            )



class CaseAttachment(Attachment):
    caseversion = models.ForeignKey(CaseVersion, related_name="attachments")



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



class Suite(CCModel, DraftStatusModel):
    """An ordered suite of test cases."""
    product = models.ForeignKey(Product, related_name="suites")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    cases = models.ManyToManyField(
        Case, through="SuiteCase", related_name="suites")


    def __unicode__(self):
        return self.name


    def clone(self, *args, **kwargs):
        """Clone this Suite with default cascade behavior."""
        kwargs.setdefault("cascade", ["suitecases"])
        overrides = kwargs.setdefault("overrides", {})
        overrides["status"] = self.STATUS.draft
        return super(Suite, self).clone(*args, **kwargs)


    class Meta:
        permissions = [("manage_suites", "Can add/edit/delete test suites.")]



class SuiteCase(CCModel):
    """Association between a test case and a suite."""
    suite = models.ForeignKey(Suite, related_name="suitecases")
    case = models.ForeignKey(Case, related_name="suitecases")
    # order of test cases in the suite
    order = models.IntegerField(default=0, db_index=True)


    class Meta:
        ordering = ["order"]
        unique_together = [["suite", "case"]]
        permissions = [
            ("manage_suite_cases", "Can add/remove cases from suites.")]
