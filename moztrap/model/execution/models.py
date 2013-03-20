"""
Models for test execution (runs, results).

"""
import datetime

from django.core.exceptions import ValidationError
from django.db import connection, transaction, models
from django.db.models import Q, Count, Max

from model_utils import Choices

from ..mtmodel import MTModel, TeamModel, DraftStatusModel
from ..core.auth import User
from ..core.models import ProductVersion
from ..environments.models import Environment, HasEnvironmentsModel
from ..library.models import CaseVersion, Suite, CaseStep



class Run(MTModel, TeamModel, DraftStatusModel, HasEnvironmentsModel):
    """A test run."""
    productversion = models.ForeignKey(ProductVersion, related_name="runs")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start = models.DateField(default=datetime.date.today)
    end = models.DateField(blank=True, null=True)
    build = models.TextField(null=True, blank=True)
    is_series = models.BooleanField(default=False)
    series = models.ForeignKey("self", null=True, blank=True)

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


    def clone_for_series(self, *args, **kwargs):
        """Clone this Run to create a new series item."""
        build = kwargs.pop("build", None)
        kwargs.setdefault(
            "cascade", ["runsuites", "environments", "team"])
        overrides = kwargs.setdefault("overrides", {})
        overrides.setdefault("name", "{0} - Build: {1}".format(
            self.name, build))
        overrides["status"] = self.STATUS.draft
        overrides.setdefault("is_series", False)
        overrides.setdefault("build", build)
        overrides.setdefault("series", self)
        overrides.setdefault(
            "start",
            datetime.date.today().strftime("%Y-%m-%d"),
            )
        return super(Run, self).clone(*args, **kwargs)


    def activate(self, *args, **kwargs):
        """Make run active, locking in runcaseversions for all suites."""
        if self.status == self.STATUS.draft:
            self.update_case_versions()
        super(Run, self).activate(*args, **kwargs)


    def refresh(self, *args, **kwargs):
        """Update all the runcaseversions while the run is active."""
        if self.status == self.STATUS.active:
            self.update_case_versions()


    def update_case_versions(self):
        """
        Update the runcaseversions with any changes to suites.

        This can happen while the run is still active.
        """
        # we don't need all the runcaseversions for a series.  It is the
        # series member runs that will use them.  So only lock the caseversions
        # if this is NOT a series.
        if not self.is_series:
            self._lock_case_versions()


    @transaction.commit_on_success
    def _lock_case_versions(self):
        """
        Select caseversions from suites, create runcaseversions.

        WARNING: Testing this code in the PyCharm debugger will give an
        incorrect number of queries, because for the debugger to show all the
        information it wants, it must do queries itself.  When testing with
        assertNumQueries, don't use the PyCharm debugger.

        """

        # get the list of environments for this run
        run_env_ids = self.environments.values_list("id", flat=True)

        # make a list of cvs in order by RunSuite, then SuiteCase.
        # This list is built from the run / suite / env combination and has
        # no knowledge of any possibly existing runcaseversions yet.
        if len(run_env_ids):
            cursor = connection.cursor()
            sql = """SELECT DISTINCT cv.id as id
                FROM execution_run as r
                    INNER JOIN execution_runsuite as rs
                        ON rs.run_id = r.id
                    INNER JOIN library_suitecase as sc
                        ON rs.suite_id = sc.suite_id
                    INNER JOIN library_suite as s
                        ON sc.suite_id = s.id
                    INNER JOIN library_caseversion as cv
                        ON cv.case_id = sc.case_id
                        AND cv.productversion_id = r.productversion_id
                    INNER JOIN library_caseversion_environments as cve
                        ON cv.id = cve.caseversion_id
                WHERE cv.status = 'active'
                    AND cv.deleted_on IS NULL
                    AND s.status = 'active'
                    AND rs.run_id = {0}
                    AND cve.environment_id IN ({1})
                ORDER BY rs.order, sc.order
                """.format(self.id, ",".join(map(str, run_env_ids)))
            cursor.execute(sql)

            cv_list = [x[0] for x in cursor.fetchall()]

            # @@@ do we need to check for duplicates?
            # use itertools.unique_everseen
            #if len(set(cv_list)) != len(cv_list):
            #    cv_list = itertools.unique_everseen(cv_list)

        else:
            cv_list = []

        # delete rcvs that we won't be needing anymore
        self._delete_runcaseversions(cv_list)

        # audit for duplicate rcvs for the same cv.id
        dups = self.runcaseversions.values("caseversion_id").annotate(
            num_records=Count("caseversion")).filter(num_records__gt=1)
        if len(dups) > 0:
            for dup in dups:
                # get the runcaseversions, and sort descending by the id
                # of the results.  So the first one is the one with the latest
                # result.  We keep that one and delete the rest.
                rcv_to_save = self.runcaseversions.annotate(
                    latest_result=Max("results__id")).filter(
                        caseversion=dup["caseversion_id"]).order_by(
                            "-latest_result")[0]
                self.runcaseversions.filter(
                    caseversion=dup["caseversion_id"]).exclude(
                        id=rcv_to_save.id).delete()

        # remaining rcvs should be ones we want to keep, and we need to inject
        # those ids into the insert/update list for bulk_insert.  So create
        # a dict mapping cv_id: rcv_id.  If one exists, its order field will
        # be updated in the build_update cmd.
        existing_rcv_map = {}
        for map_item in self.runcaseversions.values("id", "caseversion_id"):
            existing_rcv_map[map_item["caseversion_id"]] = map_item["id"]

        # build the list of rcvs that we DO need.  Be sure to include the ids
        # for rcvs that already exist so that we will just be updating the
        # order and not replacing it.  We will use a special manager that does
        # an update on insert error.

        # runcaseversion objects we will use to bulk create
        rcv_to_update = []
        rcv_proxies_to_create = []

        order = 1
        for cv in cv_list:
            if cv in existing_rcv_map:
                # we will just update the order value
                rcv_to_update.append({"caseversion_id": cv, "order": order})
            else:
                # we need to create a new one
                kwargs = {
                    "run_id": self.id,
                    "caseversion_id": cv,
                    "order": order
                    }
                rcv_proxies_to_create.append(RunCaseVersion(**kwargs))
            order += 1

        # update existing rcvs
        for rcv in rcv_to_update:
            self.runcaseversions.filter(
                caseversion=rcv["caseversion_id"]).update(order=rcv["order"])

        # insert these rcvs in bulk
        self._bulk_insert_new_runcaseversions(rcv_proxies_to_create)

        self._bulk_update_runcaseversion_environments_for_lock()

        self._lock_caseversions_complete()


    def _delete_runcaseversions(self, cv_list):
        """Hook to delete runcaseversions we know we don't need anymore."""
        self.runcaseversions.exclude(caseversion__in=cv_list).delete(
            permanent=True)


    def _bulk_insert_new_runcaseversions(self, rcv_proxies):
        """Hook to bulk-insert runcaseversions we know we DO need."""
        self.runcaseversions.bulk_create(rcv_proxies)


    def _bulk_update_runcaseversion_environments_for_lock(self):
        """
        update runcaseversion_environment records with latest state.

        Approach:
          do another raw sql query to get all existing_rcv_envs for this run
          existing_rcv_envs - needed_rcv_envs = list to delete (no longer needed)
          needed_rcv_envs - existing_rcv_envs = list to create
        build a list of RunCaseVersion_environment objects
        and use bulk_create.

        """

        # re-query all the rcvs (including newly created) for this run
        final_rcvs = RunCaseVersion.objects.filter(run=self).select_related(
            "caseversion").prefetch_related("caseversion__environments")

        final_rcv_ids = [x.id for x in final_rcvs]

        # runcaseversion_environments that were there prior to our changes
        prev_rcv_envs_set = set(RunCaseVersion.environments.through.objects.filter(
            runcaseversion_id__in=final_rcv_ids).values_list(
                "runcaseversion_id", "environment_id"))

        # runcaseversion_environment objects we will use to bulk create
        # loop through all cvs and fetch the env intersection with this run
        needed_rcv_envs_tuples = []
        run_env_ids = set(
            self.environments.values_list("id", flat=True))
        for rcv in final_rcvs:
            case_env_ids = set([x.id for x in rcv.caseversion.environments.all()])
            for env in run_env_ids.intersection(case_env_ids):
                needed_rcv_envs_tuples.append((rcv.id, env))
        needed_rcv_envs_set = set(needed_rcv_envs_tuples)

        # get the set of rcv_envs we need to delete because they don't belong
        # to the needed set.
        delete_rcv_envs = prev_rcv_envs_set - needed_rcv_envs_set
        if len(delete_rcv_envs):
            delquery = Q()
            for combo in delete_rcv_envs:
                delquery = delquery | Q(
                    **{"runcaseversion_id": combo[0],
                       "environment_id": combo[1]})
            RunCaseVersion.environments.through.objects.filter(delquery).delete()

        # get the set of rcv_envs we need to create that don't already exist
        needed_rcv_envs_set = needed_rcv_envs_set - prev_rcv_envs_set

        # build all the objects to pass to bulk_create
        needed_rcv_envs = [RunCaseVersion.environments.through(
            runcaseversion_id=needed[0],
            environment_id=needed[1]) for needed in needed_rcv_envs_set]

        RunCaseVersion.environments.through.objects.bulk_create(needed_rcv_envs)


    def _lock_caseversions_complete(self):
        """Hook for doing any post-processing after doing the rcv lock."""
        pass


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

        self.is_latest = True



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
