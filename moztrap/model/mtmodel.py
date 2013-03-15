"""
Common model behavior for all MozTrap models.

Soft-deletion (including cascade) and tracking of user and timestamp for model
creation, modification, and soft-deletion.

"""
import datetime

from django.db import models, router
from django.db.models.deletion import Collector
from django.db.models.query import QuerySet
from django.db.models.signals import class_prepared

from model_utils import Choices

from .core.auth import User



class ConcurrencyError(Exception):
    pass



def utcnow():
    return datetime.datetime.utcnow()



class SoftDeleteCollector(Collector):
    """
    A variant of Django's default delete-cascade collector that implements soft
    delete.

    """
    def collect(self, objs, *args, **kwargs):
        """
        Collect ``objs`` and dependent objects.

        We override in order to store "root" objects for undelete.

        """
        if kwargs.get("source", None) is None:
            self.root_objs = objs
        super(SoftDeleteCollector, self).collect(objs, *args, **kwargs)


    def delete(self, user=None):
        """
        Soft-delete all collected instances.

        """
        now = utcnow()
        for model, instances in self.data.iteritems():
            pk_list = [obj.pk for obj in instances]
            model._base_manager.filter(
                pk__in=pk_list, deleted_on__isnull=True).update(
                deleted_by=user, deleted_on=now)


    def undelete(self, user=None):
        """
        Undelete all collected instances that were deleted.

        """
        # timestamps on which root obj(s) were deleted; only cascade items also
        # deleted in one of these same cascade batches should be undeleted.
        deletion_times = set([o.deleted_on for o in self.root_objs])
        for model, instances in self.data.iteritems():
            pk_list = [obj.pk for obj in instances]
            model._base_manager.filter(
                pk__in=pk_list, deleted_on__in=deletion_times).update(
                deleted_by=None, deleted_on=None)



class MTQuerySet(QuerySet):
    """
    Implements modification tracking and soft deletes on bulk update/delete.

    """
    def create(self, *args, **kwargs):
        """
        Creates, saves, and returns a new object with the given kwargs.
        """
        user = kwargs.pop("user", None)
        kwargs["created_by"] = user
        kwargs["modified_by"] = user
        return super(MTQuerySet, self).create(*args, **kwargs)


    def update(self, *args, **kwargs):
        """
        Update all objects in this queryset with modifications in ``kwargs``.

        """
        if not kwargs.pop("notrack", False):
            kwargs["modified_by"] = kwargs.pop("user", None)
            kwargs["modified_on"] = utcnow()
        # increment the concurrency control version for all updated objects
        kwargs["cc_version"] = models.F("cc_version") + 1
        return super(MTQuerySet, self).update(*args, **kwargs)


    def delete(self, user=None, permanent=False):
        """
        Soft-delete all objects in this queryset, unless permanent=True.

        """
        if permanent:
            return super(MTQuerySet, self).delete()
        collector = SoftDeleteCollector(using=self.db)
        collector.collect(self)
        collector.delete(user)


    def undelete(self, user=None):
        """
        Undelete all objects in this queryset.

        """
        collector = SoftDeleteCollector(using=self.db)
        collector.collect(self)
        collector.undelete(user)



class MTManager(models.Manager):
    """
    Manager using ``MTQuerySet`` and optionally hiding deleted objects.

    By making show_deleted an instantiation argument, and defaulting it to
    False, we can achieve something a bit subtle: the instantiated default
    manager on a MTModel shows all objects, including deleted one (meaning the
    admin will show deleted objects, so they can be undeleted). But
    related-object managers (which subclass the default manager class) will
    still hide deleted objects.

    """
    def __init__(self, *args, **kwargs):
        """Instantiate a MTManager, pulling out the ``show_deleted`` arg."""
        self._show_deleted = kwargs.pop("show_deleted", False)
        super(MTManager, self).__init__(*args, **kwargs)


    def get_query_set(self):
        """Return a ``MTQuerySet`` for all queries."""
        qs = MTQuerySet(self.model, using=self.db)
        if not self._show_deleted:
            qs = qs.filter(deleted_on__isnull=True)
        return qs


    def bulk_insert_or_update(self, obj_list):
        """ Bulk insert with a list of model objects"""

        if len(obj_list):
            create_fields = [
                field.get_attname_column()[1] for field in obj_list[0]._meta.fields
                ]
            update_fields = set(create_fields) - set([
                "id", "created_by_id", "created_on", "deleted_by_id", "deleted_on"
            ])

            def getfield(obj, field):
                value = getattr(obj, field)
                if isinstance(value, (str, datetime.datetime)):
                    return "'{0}'".format(value)
                elif value is None:
                    return "NULL"
                else:
                    return value

            values = []
            for obj in obj_list:
                values.append("({0})".format(", ".join(
                    ["{0}".format(getfield(obj, field)) for field in create_fields]
                )))

            db_table = self.model._meta.db_table

            bulk_insert_or_update(
                db_table,
                create_fields,
                update_fields,
                values,
                )



class MTModel(models.Model):
    """
    Common base abstract model for all MozTrap models.

    Tracks user and timestamp for creation, modification, and (soft) deletion.

    """
    created_on = models.DateTimeField(default=utcnow)
    created_by = models.ForeignKey(
        User, blank=True, null=True, related_name="+", on_delete=models.SET_NULL)

    modified_on = models.DateTimeField(default=utcnow)
    modified_by = models.ForeignKey(
        User, blank=True, null=True, related_name="+", on_delete=models.SET_NULL)
    deleted_on = models.DateTimeField(db_index=True, blank=True, null=True)
    deleted_by = models.ForeignKey(
        User, blank=True, null=True, related_name="+", on_delete=models.SET_NULL)

    # for optimistic concurrency control
    cc_version = models.IntegerField(default=0)



    # default manager returns all objects, so admin can see all
    everything = MTManager(show_deleted=True)
    # ...but "objects", for use in most code, returns only not-deleted
    objects = MTManager(show_deleted=False)


    def save(self, *args, **kwargs):
        """
        Save this instance.

        Records modified timestamp and user, and raises ConcurrencyError if an
        out-of-date version is being saved.

        """
        if not kwargs.pop("notrack", False):
            user = kwargs.pop("user", None)
            now = utcnow()
            if self.pk is None and user is not None:
                self.created_by = user
            # .create() won't pass in user, but presets modified_by
            if not (self.pk is None and self.modified_by is not None):
                self.modified_by = user
            self.modified_on = now

        # MTModels always have an auto-PK and we don't set PKs explicitly, so
        # we can assume that a set PK means this should be an update.
        if kwargs.get("force_update") or self.id is not None:
            non_pks = [f for f in self._meta.local_fields if not f.primary_key]
            # This isn't a race condition because the save will only take
            # effect if previous_version is actually up to date.
            previous_version = self.cc_version
            self.cc_version += 1
            values = [(f, None, f.pre_save(self, False)) for f in non_pks]
            rows = self.__class__.objects.filter(
                id=self.id, cc_version=previous_version)._update(values)
            if not rows:
                raise ConcurrencyError(
                    "No {0} row with id {1} and version {2} updated.".format(
                        self.__class__, self.id, previous_version)
                    )
        else:
            return super(MTModel, self).save(*args, **kwargs)


    def clone(self, cascade=None, overrides=None, user=None):
        """
        Clone this instance and return the new, cloned instance.

        ``overrides`` should be a dictionary of override values for fields on
        the cloned instance.

        M2M or reverse FK relations listed in ``cascade`` iterable will be
        cascade-cloned. By default, if not listed in ``cascade``, m2m/reverse
        FKs will effectively be cleared (as the remote object will still be
        pointing to the original instance, not the cloned one.)

        If ``cascade`` is a dictionary, keys are m2m/reverse-FK accessor names,
        and values are a callable that takes the queryset of all related
        objects and returns those that should be cloned.

        """
        if cascade is None:
            cascade = {}
        else:
            try:
                cascade.iteritems
            except AttributeError:
                cascade = dict((i, lambda qs: qs) for i in cascade)

        if overrides is None:
            overrides = {}

        overrides["created_on"] = utcnow()
        overrides["created_by"] = user
        overrides["modified_by"] = user

        clone = self.__class__()

        for field in self._meta.fields:
            if field.primary_key:
                continue
            val = overrides.get(field.name, getattr(self, field.name))
            setattr(clone, field.name, val)

        clone.save(force_insert=True)

        for name, filter_func in cascade.items():
            mgr = getattr(self, name)
            if mgr.__class__.__name__ == "ManyRelatedManager":  # M2M
                clone_mgr = getattr(clone, name)
                existing = set(clone_mgr.all())
                new = set(filter_func(mgr.all()))
                clone_mgr.add(*new.difference(existing))
                clone_mgr.remove(*existing.difference(new))
            elif mgr.__class__.__name__ == "RelatedManager":  # reverse FK
                reverse_name = getattr(self.__class__, name).related.field.name
                for obj in filter_func(mgr.all()):
                    obj.clone(overrides={reverse_name: clone})
            else:
                raise ValueError(
                    "Cannot cascade-clone '{0}'; "
                    "not a many-to-many or reverse foreignkey.".format(name))

        return clone


    def delete(self, user=None, permanent=False):
        """
        (Soft) delete this instance, unless permanent=True.

        """
        if permanent:
            return super(MTModel, self).delete()
        self._collector.delete(user)


    def undelete(self, user=None):
        """
        Undelete this instance.

        """
        self._collector.undelete(user)


    @property
    def _collector(self):
        """Returns populated delete-cascade collector."""
        db = router.db_for_write(self.__class__, instance=self)
        collector = SoftDeleteCollector(using=db)
        collector.collect([self])
        return collector


    class Meta:
        abstract = True



class NotDeletedCount(models.Count):
    """A Count on a related field that only counts not-deleted objects."""
    def add_to_query(self, query, alias, col, source, is_summary):
        """
        Add the aggregate to the nominated query.

        Expects col to be a tuple (which means this can only be used to count
        related fields), and transforms it into a NotDeletedCountColumn.

        """
        try:
            table, field = col
        except ValueError:
            table, field = None, col
        col = NotDeletedCountColumn(table, field)
        return super(NotDeletedCount, self).add_to_query(
            query, alias, col, source, is_summary)



class NotDeletedCountColumn(object):
    """An object with an as_sql method that counts only not-deleted objects."""
    def __init__(self, table, field):
        """Initialize the column with a table and field name."""
        self.table = table
        self.field = field


    def as_sql(self, qn, connection):
        """Return CASE statement to select only not-deleted objects."""
        field = qn(self.field)
        deleted_on = qn("deleted_on")
        if self.table is not None:
            table = qn(self.table)
            field = "{0}.{1}".format(table, field)
            deleted_on = "{0}.{1}".format(table, deleted_on)
        return "CASE WHEN {0} IS NULL THEN {1} ELSE NULL END".format(
            deleted_on, field)



class TeamModel(models.Model):
    """
    Model which may have its own team or inherit team from parent.

    If ``has_team`` is True, ``own_team`` is this instance's team. If False,
    the parent's team is used instead.

    If a ``TeamModel`` does not implement a ``parent`` property that returns
    its "parent" for purposes of team inheritance, it will be considered to be
    the top of the inheritance chain and won't inherit a team.

    """
    has_team = models.BooleanField(default=False)
    own_team = models.ManyToManyField(User, blank=True)


    @property
    def team(self):
        if self.has_team or self.parent is None:
            return self.own_team
        return self.parent.team


    def add_to_team(self, *users):
        """Add given users to this object's team (not to parent team)."""
        self.own_team.add(*users)
        self.__class__.objects.filter(pk=self.pk).update(has_team=True)
        self.has_team = True
        self.cc_version += 1


    @property
    def parent(self):
        return None


    class Meta:
        abstract = True



class DraftStatusModel(models.Model):
    """
    Model which has a status that can be draft, active, or disabled.

    Also provides ``activate`` and ``deactivate`` model methods.

    """
    STATUS = Choices("draft", "active", "disabled")
    DEFAULT_STATUS = STATUS.draft


    status = models.CharField(
        max_length=30, db_index=True, choices=STATUS, default=DEFAULT_STATUS)


    def activate(self, user=None):
        """Activate this object."""
        self.status = self.STATUS.active
        self.save(force_update=True, user=user)


    def draft(self, user=None):
        """Reset this object to draft status."""
        self.status = self.STATUS.draft
        self.save(force_update=True, user=user)


    def deactivate(self, user=None):
        """Deactivate this object."""
        self.status = self.STATUS.disabled
        self.save(force_update=True, user=user)


    class Meta:
        abstract = True



def set_default_status(sender, **kwargs):
    """Set the default status on a DraftStatusModel subclass."""
    if issubclass(sender, DraftStatusModel):
        sender._meta.get_field("status").default = sender.DEFAULT_STATUS


def bulk_insert_or_update(db_table, create_fields, update_fields, values):
    """
    Bulk insert with a list of fields and values list

    On duplicate key, update those values based on the update_fields list.

    The concept of this handy manager was borrowed
    from a gist by mmohiudd: https://gist.github.com/3903508

    Except I made this work with model objects instead of lists of
    specific fields to update and insert.  We figure it out based on the
    fields of the model object.

    This provides bulk insert and UPDATE ON DUPLICATE KEY.

    """

    from django.db import connection, transaction
    cursor = connection.cursor()

    base_sql = "INSERT INTO {0} (`{1}`) VALUES {2}".format(
        db_table,
        "`, `".join(create_fields),
        ", ".join(values)
    )

    on_duplicates = []
    for field in update_fields:
        on_duplicates.append("`{0}`=VALUES(`{0}`)".format(field, field))

    sql = "{0} ON DUPLICATE KEY UPDATE {1}".format(
        base_sql,
        ", ".join(on_duplicates),
        )

    cursor.execute(sql)
    transaction.commit_unless_managed()


class_prepared.connect(set_default_status)
