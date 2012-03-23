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
Models for test execution (runs, results).

"""
import datetime

from django.core.exceptions import ValidationError
from django.db import connection, models

from model_utils import Choices

from ..ccmodel import CCModel, TeamModel, DraftStatusModel, utcnow
from ..core.auth import User
from ..core.models import ProductVersion
from ..environments.models import Environment, HasEnvironmentsModel
from ..library.models import CaseVersion, Suite, CaseStep, SuiteCase



class Run(CCModel, TeamModel, DraftStatusModel, HasEnvironmentsModel):
    """A test run."""
    productversion = models.ForeignKey(ProductVersion, related_name="runs")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
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


    class Meta:
        permissions = [("manage_runs", "Can add/edit/delete test runs.")]


    @property
    def parent(self):
        return self.productversion


    @classmethod
    def cascade_envs_to(cls, objs, adding):
        if adding:
            return {}
        return {RunCaseVersion: RunCaseVersion.objects.filter(run__in=objs)}


    def clone(self, *args, **kwargs):
        """Clone this Run with default cascade behavior."""
        kwargs.setdefault(
            "cascade", ["runsuites", "environments", "team"])
        overrides = kwargs.setdefault("overrides", {})
        overrides["status"] = self.STATUS.draft
        overrides.setdefault("name", "Cloned: {0}".format(self.name))
        return super(Run, self).clone(*args, **kwargs)


    def activate(self, *args, **kwargs):
        """Make run active, locking in runcaseversions for all suites."""
        if self.status == self.STATUS.draft:
            self._lock_case_versions()
        super(Run, self).activate(*args, **kwargs)


    def _lock_case_versions(self):
        """Select caseversions from suites, create runcaseversions."""
        order = 1
        for runsuite in RunSuite.objects.filter(
                run=self).order_by("order").select_related("suite"):
            for suitecase in SuiteCase.objects.filter(
                    suite=runsuite.suite).order_by(
                    "order").select_related("case"):
                try:
                    caseversion = suitecase.case.versions.filter(
                        productversion=self.productversion,
                        status=CaseVersion.STATUS.active).get()
                except CaseVersion.DoesNotExist:
                    pass
                else:
                    envs = _environment_intersection(self, caseversion)
                    if envs:
                        try:
                            rcv = RunCaseVersion.objects.get(
                                run=self, caseversion=caseversion)
                        except RunCaseVersion.MultipleObjectsReturned:
                            dupes = list(
                                RunCaseVersion.objects.filter(
                                    run=self, caseversion=caseversion)
                                )
                            rcv = dupes.pop()
                            for dupe in dupes:
                                rcv.environments.add(*dupe.environments.all())
                                dupe.results.update(runcaseversion=rcv)
                                dupe.delete(permanent=True)
                        except RunCaseVersion.DoesNotExist:
                            rcv = RunCaseVersion(
                                run=self, caseversion=caseversion, order=order)
                            rcv.save(force_insert=True, inherit_envs=False)
                            rcv.environments.add(*envs)
                            order += 1
                        rcv.suites.add(runsuite.suite)


    def result_summary(self):
        """Return a dict summarizing status of results."""
        return result_summary(Result.objects.filter(runcaseversion__run=self))


    def completion(self):
        """Return fraction of case/env combos that have a completed result."""
        total = RunCaseVersion.environments.through._default_manager.filter(
            runcaseversion__run=self).count()
        completed = Result.objects.filter(
            status__in=Result.COMPLETED_STATES,
            runcaseversion__run=self).values(
            "runcaseversion", "environment").distinct().count()

        try:
            return float(completed) / total
        except ZeroDivisionError:
            return 0



def _environment_intersection(run, caseversion):
    """Intersection of run/caseversion environment IDs."""
    run_env_ids = set(
        run.environments.values_list("id", flat=True))
    case_env_ids = set(
        caseversion.environments.values_list("id", flat=True))
    return run_env_ids.intersection(case_env_ids)



class RunCaseVersion(HasEnvironmentsModel, CCModel):
    """
    An ordered association between a Run and a CaseVersion.

    RunCaseVersion objects are created to lock in the specific case-versions in
    a run when the run is activated.

    """
    run = models.ForeignKey(Run, related_name="runcaseversions")
    caseversion = models.ForeignKey(CaseVersion, related_name="runcaseversions")
    suites = models.ManyToManyField(Suite, related_name="runcaseversions")
    order = models.IntegerField(default=0, db_index=True)


    def __unicode__(self):
        """Return unicode representation."""
        return "Case '%s' included in run '%s'" % (self.caseversion, self.run)


    def bug_urls(self):
        """Returns set of bug URLs associated with this run/caseversion."""
        return set(
            StepResult.objects.filter(
                result__runcaseversion=self).exclude(
                bug_url="").values_list("bug_url", flat=True).distinct()
            )


    class Meta:
        ordering = ["order"]
        permissions = [
            ("execute", "Can run tests and report results."),
            ]


    def save(self, *args, **kwargs):
        """
        Save instance; new instances get intersection of run/case environments.

        """
        adding = False
        if self.id is None:
            adding = True
        inherit_envs = kwargs.pop("inherit_envs", True)

        ret = super(RunCaseVersion, self).save(*args, **kwargs)

        if adding and inherit_envs:
            self.environments.add(
                *_environment_intersection(self.run, self.caseversion))

        return ret


    def result_summary(self):
        """Return a dict summarizing status of results."""
        return result_summary(self.results.all())


    def completion(self):
        """Return fraction of environments that have a completed result."""
        total = self.environments.count()
        completed = self.results.filter(
            status__in=Result.COMPLETED_STATES).values(
            "environment").distinct().count()

        try:
            return float(completed) / total
        except ZeroDivisionError:
            return 0


    def testers(self):
        """Return list of testers with assigned / executed results."""
        return User.objects.filter(
            pk__in=self.results.values_list("tester", flat=True).distinct())



class RunSuite(CCModel):
    """
    An ordered association between a Run and a Suite.

    The only direct impact of RunSuite instances is that they determine which
    RunCaseVersions are created when the run is activated.

    """
    run = models.ForeignKey(Run, related_name="runsuites")
    suite = models.ForeignKey(Suite, related_name="runsuites")
    order = models.IntegerField(default=0, db_index=True)


    def __unicode__(self):
        """Return unicode representation."""
        return "Suite '%s' included in run '%s'" % (self.suite, self.run)


    class Meta:
        ordering = ["order"]



class Result(CCModel):
    """A result of a User running a RunCaseVersion in an Environment."""
    STATUS = Choices("assigned", "started", "passed", "failed", "invalidated")
    REVIEW = Choices("pending", "reviewed")

    COMPLETED_STATES = [STATUS.passed, STATUS.failed, STATUS.invalidated]

    tester = models.ForeignKey(User, related_name="results")
    runcaseversion = models.ForeignKey(
        RunCaseVersion, related_name="results")
    environment = models.ForeignKey(Environment, related_name="results")
    status = models.CharField(
        max_length=50, db_index=True, choices=STATUS, default=STATUS.assigned)
    started = models.DateTimeField(blank=True, null=True)
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


    class Meta:
        permissions = [("review_results", "Can review/edit test results.")]


    def bug_urls(self):
        """Returns set of bug URLs associated with this result."""
        return set(
            self.stepresults.exclude(
                bug_url="").values_list("bug_url", flat=True).distinct()
            )


    def start(self, user=None):
        """Mark this result started."""
        self.status = self.STATUS.started
        self.started = utcnow()
        self.save(force_update=True, user=user)


    def finishsucceed(self, user=None):
        """Mark this result passed."""
        self.status = self.STATUS.passed
        self.completed = utcnow()
        if not self.started:
            self.started = utcnow()
        self.save(force_update=True, user=user)


    def finishinvalidate(self, comment="", user=None):
        """Mark this result invalidated."""
        self.status = self.STATUS.invalidated
        self.comment = comment
        self.completed = utcnow()
        if not self.started:
            self.started = utcnow()
        self.save(force_update=True, user=user)


    def finishfail(self, comment="", stepnumber=None, bug="", user=None):
        """Mark this result failed."""
        self.status = self.STATUS.failed
        self.completed = utcnow()
        if not self.started:
            self.started = utcnow()
        self.comment = comment
        if stepnumber:
            try:
                step = self.runcaseversion.caseversion.steps.get(
                    number=stepnumber)
            except CaseStep.DoesNotExist:
                pass
            else:
                try:
                    stepresult = self.stepresults.get(step=step)
                except StepResult.DoesNotExist:
                    stepresult = StepResult(result=self, step=step)
                stepresult.status = StepResult.STATUS.failed
                stepresult.bug_url = bug
                stepresult.save(user=user)
        self.save(force_update=True, user=user)


    def restart(self, user=None):
        """Restart this test, clearing any previous result."""
        self.stepresults.all().delete()
        self.status = self.STATUS.started
        self.started = utcnow()
        self.completed = None
        self.comment = ""
        self.save(force_update=True, user=user)



class StepResult(CCModel):
    """A result of a particular step in a test case."""
    STATUS = Choices("passed", "failed", "invalidated")

    result = models.ForeignKey(Result, related_name="stepresults")
    step = models.ForeignKey(CaseStep, related_name="stepresults")
    status = models.CharField(
        max_length=50, db_index=True, choices=STATUS, default=STATUS.passed)
    bug_url = models.URLField(blank=True)


    def __unicode__(self):
        """Return unicode representation."""
        return "%s (%s: %s)" % (self.result, self.step, self.status)



def result_summary(results):
    """
    Given a queryset of results, return a dict summarizing their states.

    """
    states = Result.COMPLETED_STATES

    result_ids = results.values_list("id", flat=True)

    if not result_ids:
        return dict((s, 0) for s in states)

    cols = ["COUNT(CASE WHEN status=%s THEN 1 ELSE NULL END)"] * len(states)
    sql = "SELECT {0} FROM {1} WHERE id IN ({2})".format(
        ",".join(cols), Result._meta.db_table, ",".join(map(str, result_ids))
        )

    cursor = connection.cursor()
    cursor.execute(sql, states)

    return dict(zip(states, cursor.fetchone()))
