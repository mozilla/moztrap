"""
Models for test execution (runs, results).

"""
import datetime

from django.core.exceptions import ValidationError
from django.db import connection, models

from model_utils import Choices

from ..mtmodel import MTModel, TeamModel, DraftStatusModel
from ..core.auth import User
from ..core.models import ProductVersion
from ..environments.models import Environment, HasEnvironmentsModel
from ..library.models import CaseVersion, Suite, CaseStep, SuiteCase



class Run(MTModel, TeamModel, DraftStatusModel, HasEnvironmentsModel):
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
        rcv_ids = set()
        preexisting_rcv_ids = set(
            self.runcaseversions.values_list("id", flat=True))
        for runsuite in RunSuite.objects.filter(
                run=self, suite__status=Suite.STATUS.active).order_by(
                "order").select_related("suite"):
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
                    rcv_id = self._add_caseversion(
                        caseversion, runsuite.suite, order)
                    if rcv_id is not None:
                        order += 1
                        rcv_ids.add(rcv_id)
        self.runcaseversions.filter(
            id__in=preexisting_rcv_ids.difference(rcv_ids)).delete()


    def _add_caseversion(self, caseversion, suite, order):
        """
        Add given caseversion to this run, from given suite, at given order.

        Returns runcaseversion ID if the caseversion was actually added (or
        found to already exist), else None.

        """
        envs = _environment_intersection(self, caseversion)
        if not envs:
            return None
        found = False
        try:
            rcv = RunCaseVersion.objects.get(
                run=self, caseversion=caseversion)
            found = True
        except RunCaseVersion.MultipleObjectsReturned:
            dupes = list(
                RunCaseVersion.objects.filter(
                    run=self, caseversion=caseversion)
                )
            rcv = dupes.pop()
            for dupe in dupes:
                dupe.results.update(runcaseversion=rcv)
                dupe.delete(permanent=True)
            found = True
        except RunCaseVersion.DoesNotExist:
            rcv = RunCaseVersion(
                run=self, caseversion=caseversion, order=order)
            rcv.save(force_insert=True, inherit_envs=False)
            rcv.environments.add(*envs)
        if found:
            rcv.order = order
            rcv.save()
            current_envs = set(rcv.environments.values_list("id", flat=True))
            rcv.environments.remove(*current_envs.difference(envs))
            rcv.environments.add(*envs.difference(current_envs))
        rcv.suites.add(suite)
        return rcv.id


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



class RunCaseVersion(HasEnvironmentsModel, MTModel):
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


    def start(self, environment=None, user=None):
        """Mark this result started."""
        Result.objects.create(
            runcaseversion=self,
            tester=user,
            environment=environment,
            status=Result.STATUS.started,
            user=user
            )


    def get_result_method(self, status):
        """Find the appropriate result generator for the given status."""
        status_methods = {
            "passed": self.result_pass,
            "failed": self.result_fail,
            "invalidated": self.result_invalid,
            }

        return status_methods[status]



    def result_pass(self, environment=None, user=None):
        """Create a passed result for this case."""
        Result.objects.create(
            runcaseversion=self,
            tester=user,
            environment=environment,
            status=Result.STATUS.passed,
            user=user
        )


    def result_invalid(self, environment=None, comment="", user=None):
        """Create an invalidated result for this case."""
        Result.objects.create(
            runcaseversion=self,
            tester=user,
            environment=environment,
            status=Result.STATUS.invalidated,
            comment=comment,
            user=user,
        )


    def result_fail(self, environment=None, comment="", stepnumber=None, bug="", user=None):
        """Create a failed result for this case."""
        result = Result.objects.create(
            runcaseversion=self,
            tester=user,
            environment=environment,
            status=Result.STATUS.failed,
            comment=comment,
            user=user,
            )
        if stepnumber is not None:
            try:
                step = self.caseversion.steps.get(
                    number=stepnumber)
            except CaseStep.DoesNotExist:
                pass
            else:
                stepresult = StepResult(result=result, step=step)
                stepresult.status = StepResult.STATUS.failed
                stepresult.bug_url = bug
                stepresult.save(user=user)
        self.save(force_update=True, user=user)



class RunSuite(MTModel):
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



class Result(MTModel):
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
    comment = models.TextField(blank=True)
    is_latest = models.BooleanField(default=True)

    review = models.CharField(
        max_length=50, db_index=True, choices=REVIEW, default=REVIEW.pending)
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


    def save(self, *args, **kwargs):
        if self.pk is None:
            self.set_latest()
        super(Result, self).save(*args, **kwargs)


    def set_latest(self):
        """
        Set this result to latest, and unset all others with this env/user/rcv

        """

        Result.objects.filter(
            tester=self.tester,
            runcaseversion=self.runcaseversion,
            environment=self.environment,
            is_latest=True,
            ).exclude(pk=self.pk).update(is_latest=False)

        self.is_latest=True



class StepResult(MTModel):
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

    result_ids = results.filter(is_latest=True).values_list("id", flat=True)

    if not result_ids:
        return dict((s, 0) for s in states)

    cols = ["COUNT(CASE WHEN status=%s THEN 1 ELSE NULL END)"] * len(states)
    sql = "SELECT {0} FROM {1} WHERE id IN ({2})".format(
        ",".join(cols), Result._meta.db_table, ",".join(map(str, result_ids))
        )

    cursor = connection.cursor()
    cursor.execute(sql, states)

    return dict(zip(states, cursor.fetchone()))
