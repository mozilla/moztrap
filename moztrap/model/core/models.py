"""
Core MozTrap models (Product).

"""
import uuid

from django.core.exceptions import ValidationError
from django.db import models

from pkg_resources import parse_version
from preferences.models import Preferences

from ..environments.models import HasEnvironmentsModel
from ..mtmodel import MTModel, MTManager, TeamModel
from .auth import Role, User



class Product(MTModel, TeamModel):
    name = models.CharField(db_index=True, max_length=100)
    description = models.TextField(blank=True)


    def __unicode__(self):
        return self.name


    class Meta:
        permissions = [
            ("manage_products", "Can add/edit/delete products."),
            ("manage_users", "Can add/edit/delete user accounts."),
            ]
        ordering = ["name"]


    def clone(self, *args, **kwargs):
        """
        Clone Product, with team.

        """
        kwargs.setdefault("cascade", ["team"])
        overrides = kwargs.setdefault("overrides", {})
        overrides.setdefault("name", "Cloned: {0}".format(self.name))
        return super(Product, self).clone(*args, **kwargs)


    def reorder_versions(self, update_instance=None):
        """
        Reorder versions of this product, saving new order in db.

        If an ``update_instance`` is given, update it with new order and
        ``latest`` flag.

        """
        ordered = sorted(self.versions.all(), key=by_version)
        for i, version in enumerate(ordered, 1):
            version.order = i
            version.latest = (i == len(ordered))
            version.save(force_update=True, skip_reorder=True, notrack=True)
            if version == update_instance:
                update_instance.order = version.order
                update_instance.latest = version.latest
                update_instance.cc_version += 1
        # now we have to update latest caseversions too, @@@ too slow?
        for case in self.cases.all():
            case.set_latest_version()



class ProductVersion(MTModel, TeamModel, HasEnvironmentsModel):
    product = models.ForeignKey(Product, related_name="versions")
    version = models.CharField(max_length=100)
    codename = models.CharField(max_length=100, blank=True)
    order = models.IntegerField(default=0, editable=False)
    # denormalized for querying
    latest = models.BooleanField(default=False, editable=False)


    @property
    def name(self):
        """A ProductVersion's name is its product name and version."""
        return u"%s %s" % (self.product, self.version)


    def __unicode__(self):
        """A ProductVersion's unicode representation is its name."""
        return self.name


    class Meta:
        ordering = ["product", "order"]


    def save(self, *args, **kwargs):
        """Save productversion, updating latest version."""
        skip_reorder = kwargs.pop("skip_reorder", False)
        super(ProductVersion, self).save(*args, **kwargs)
        if not skip_reorder:
            self.product.reorder_versions(update_instance=self)


    def delete(self, *args, **kwargs):
        """Delete productversion, updating latest version."""
        super(ProductVersion, self).delete(*args, **kwargs)
        self.product.reorder_versions()


    def undelete(self, *args, **kwargs):
        """Undelete productversion, updating latest version."""
        super(ProductVersion, self).undelete(*args, **kwargs)
        self.product.reorder_versions()


    def clean(self):
        """
        Validate uniqueness of product/version combo.

        Can't use actual unique constraint due to soft-deletion; if we don't
        include deleted-on in the constraint, deleted objects can cause
        integrity errors; if we include deleted-on in the constraint it
        nullifies the constraint entirely, since NULL != NULL in SQL.

        """
        try:
            dupes = ProductVersion.objects.filter(
                product=self.product, version=self.version)
        except Product.DoesNotExist:
            # product is not set or is invalid; dupes are not an issue.
            return
        if self.pk is not None:
            dupes = dupes.exclude(pk=self.pk)
        if dupes.exists():
            raise ValidationError(
                "Product version '{0}' for '{1}' already exists.".format(
                    self.version, self.product)
                )


    @property
    def parent(self):
        return self.product


    def fix_environments(self):
        """Fix environments on un-narrowed caseversions"""

        cvs = self.caseversions.filter(envs_narrowed=False)
        try:
            Cv_Env = cvs.model.environments.through

            env_ids = set(self.environments.values_list(
                "id", flat=True))
            to_create = []
            for cv in cvs:
                current_env_ids = set(cv.environments.values_list(
                    "id", flat=True))
                envs_needed = env_ids.difference(current_env_ids)
                for env_id in envs_needed:
                    to_create.append(
                        Cv_Env(caseversion_id=cv.id, environment_id=env_id)
                        )

            Cv_Env.objects.bulk_create(to_create)
        except Exception as ex:
            # we had no caseversions, so no action needed anyway
            raise ex


    @classmethod
    def cascade_envs_to(cls, objs, adding):
        Run = cls.runs.related.model
        CaseVersion = cls.caseversions.related.model

        runs = Run.objects.filter(productversion__in=objs)
        caseversions = CaseVersion.objects.filter(productversion__in=objs)

        if adding:
            runs = runs.filter(status=Run.STATUS.draft)
            caseversions = caseversions.filter(envs_narrowed=False)

        return {Run: runs, CaseVersion: caseversions}


    def clone(self, *args, **kwargs):
        """
        Clone ProductVersion, with ".next" version and "Cloned:" codename.

        """
        overrides = kwargs.setdefault("overrides", {})
        overrides["version"] = "%s.next" % self.version
        overrides["codename"] = "Cloned: %s" % self.codename
        kwargs.setdefault("cascade", ["environments", "team"])
        return super(ProductVersion, self).clone(*args, **kwargs)



def by_version(productversion):
    """
    Given a ProductVersion, return a version tuple that will order correctly.

    Uses pkg_resources' ``parse_version`` function.

    This function is intended to be passed to the ``key`` argument of the
    ``sorted`` builtin.

    """
    return parse_version(productversion.version)



class CorePreferences(Preferences):
    __module__ = "preferences.models"

    default_new_user_role = models.ForeignKey(Role, blank=True, null=True)

    class Meta:
        verbose_name_plural = "core preferences"



class ApiKeyManager(MTManager):
    use_for_related_fields = True

    def active(self):
        return self.get_query_set().filter(active=True)



class ApiKey(MTModel):
    owner = models.ForeignKey(User, related_name="api_keys")
    key = models.CharField(max_length=36, unique=True)
    active = models.BooleanField(default=True, db_index=True)

    objects = ApiKeyManager()


    def __unicode__(self):
        return self.key


    @classmethod
    def generate(cls, owner, user=None):
        """
        Generate, save and return a new API key.

        ``owner`` is the owner of the new key, ``user`` is the creating user.

        """
        if user is None:
            user = owner

        return cls.objects.create(
            owner=owner, user=user, key=unicode(uuid.uuid4()))
