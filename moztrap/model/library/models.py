"""
Models for test-case library (cases, suites).

"""
from django.core.exceptions import ValidationError
from django.db import models

from ..attachments.models import Attachment
from ..mtmodel import MTModel, DraftStatusModel
from ..core.models import Product, ProductVersion
from ..environments.models import HasEnvironmentsModel
from ..tags.models import Tag



class Case(MTModel):
    """A test case for a given product."""
    product = models.ForeignKey(Product, related_name="cases")
    idprefix = models.CharField(max_length=25, blank=True)


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
            self.versions.exclude(pk=latest_version.pk).update(
                latest=False, notrack=True)
            self.versions.filter(pk=latest_version.pk).update(
                latest=True, notrack=True)
            if update_instance is not None:
                update_instance.cc_version += 1
                if update_instance == latest_version:
                    update_instance.latest = True
                else:
                    update_instance.latest = False


    def all_versions(self):
        """
        Return list of (productversion, caseversion) tuples for this case.

        Includes all product versions; caseversion may be None if this case has
        no version for that product version.

        """
        caseversions_by_pv = dict(
            (cv.productversion, cv) for cv in self.versions.all())
        return(
            [
                (pv, caseversions_by_pv.get(pv, None))
                for pv in self.product.versions.all()
                ]
            )


    def latest_version(self):
        """Return latest version of this case."""
        return self.versions.get(latest=True)



    class Meta:
        permissions = [
            ("create_cases", "Can create new test cases."),
            ("manage_cases", "Can add/edit/delete test cases."),
            ]



class CaseVersion(MTModel, DraftStatusModel, HasEnvironmentsModel):
    """A version of a test case."""
    DEFAULT_STATUS = DraftStatusModel.STATUS.active

    productversion = models.ForeignKey(
        ProductVersion, related_name="caseversions")
    case = models.ForeignKey(Case, related_name="versions")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # denormalized for queries
    latest = models.BooleanField(default=False, editable=False)

    tags = models.ManyToManyField(Tag, blank=True, related_name="caseversions")
    # True if this case's envs have been narrowed from the product version.
    envs_narrowed = models.BooleanField(default=False)


    def __unicode__(self):
        return self.name


    class Meta:
        ordering = ["case", "productversion__order"]


    def save(self, *args, **kwargs):
        """Save CaseVersion, updating latest version."""
        skip_set_latest = kwargs.pop("skip_set_latest", False)
        super(CaseVersion, self).save(*args, **kwargs)
        if not skip_set_latest:
            self.case.set_latest_version(update_instance=self)


    def delete(self, *args, **kwargs):
        """Delete CaseVersion, updating latest version."""
        super(CaseVersion, self).delete(*args, **kwargs)
        self.case.set_latest_version()


    def undelete(self, *args, **kwargs):
        """Undelete CaseVersion, updating latest version."""
        super(CaseVersion, self).undelete(*args, **kwargs)
        self.case.set_latest_version()


    def clean(self):
        """
        Validate uniqueness of product/version combo.

        Can't use actual unique constraint due to soft-deletion; if we don't
        include deleted-on in the constraint, deleted objects can cause
        integrity errors; if we include deleted-on in the constraint it
        nullifies the constraint entirely, since NULL != NULL in SQL.

        """
        try:
            dupes = CaseVersion.objects.filter(
                productversion=self.productversion, case=self.case)
        except (Case.DoesNotExist, ProductVersion.DoesNotExist):
            return
        if self.pk is not None:
            dupes = dupes.exclude(pk=self.pk)
        if dupes.exists():
            raise ValidationError(
                "A version of this test case for '{0}' already exists.".format(
                    self.productversion)
                )


    def clone(self, *args, **kwargs):
        """
        Clone this CaseVersion, cascading steps, attachments, tags.  Cloned
        CaseVersions take on the status of their source CaseVersion.

        Only one CaseVersion can exist for a given case/productversion
        combination; thus if neither a new case nor a new productversion is
        provided in the ``overrides`` dictionary, a new Case will implicitly be
        cloned and the cloned CaseVersion will be assigned to that new case.

        """
        kwargs.setdefault(
            "cascade", ["steps", "attachments", "tags", "environments"])
        overrides = kwargs.setdefault("overrides", {})
        overrides.setdefault("name", "Cloned: {0}".format(self.name))
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



class CaseStep(MTModel):
    """A step of a test case."""
    caseversion = models.ForeignKey(CaseVersion, related_name="steps")
    number = models.IntegerField()
    instruction = models.TextField()
    expected = models.TextField(blank=True)


    def __unicode__(self):
        return u"step #%s" % (self.number,)


    def clean(self):
        """
        Validate uniqueness of caseversion/number combo.

        Can't use actual unique constraint due to soft-deletion; if we don't
        include deleted-on in the constraint, deleted objects can cause
        integrity errors; if we include deleted-on in the constraint it
        nullifies the constraint entirely, since NULL != NULL in SQL.

        """
        try:
            dupes = CaseStep.objects.filter(
                caseversion=self.caseversion, number=self.number)
        except CaseVersion.DoesNotExist:
            return
        if self.pk is not None:
            dupes = dupes.exclude(pk=self.pk)
        if dupes.exists():
            raise ValidationError(
                "Test case '{0}' already has a step number '{1}'.".format(
                    self.caseversion, self.number)
                )


    class Meta:
        ordering = ["caseversion", "number"]



class Suite(MTModel, DraftStatusModel):
    """An ordered suite of test cases."""
    DEFAULT_STATUS = DraftStatusModel.STATUS.active

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
        overrides.setdefault("name", "Cloned: {0}".format(self.name))
        return super(Suite, self).clone(*args, **kwargs)


    class Meta:
        permissions = [("manage_suites", "Can add/edit/delete test suites.")]



class SuiteCase(MTModel):
    """Association between a test case and a suite."""
    suite = models.ForeignKey(Suite, related_name="suitecases")
    case = models.ForeignKey(Case, related_name="suitecases")
    # order of test cases in the suite
    order = models.IntegerField(default=0, db_index=True)


    class Meta:
        ordering = ["order"]
        permissions = [
            ("manage_suite_cases", "Can add/remove cases from suites.")]


    def clean(self):
        """
        Validate uniqueness of suite/case combo.

        Can't use actual unique constraint due to soft-deletion; if we don't
        include deleted-on in the constraint, deleted objects can cause
        integrity errors; if we include deleted-on in the constraint it
        nullifies the constraint entirely, since NULL != NULL in SQL.

        """
        try:
            dupes = SuiteCase.objects.filter(
                suite=self.suite, case=self.case)
        except (Suite.DoesNotExist, Case.DoesNotExist):
            return
        if self.pk is not None:
            dupes = dupes.exclude(pk=self.pk)
        if dupes.exists():
            raise ValidationError(
                "'{0}' is already in suite '{1}'".format(
                    self.case, self.suite)
                )
