"""
Models for environments.

"""
import itertools
from collections import defaultdict

from django.db import models

from ..ccmodel import CCModel



class Profile(CCModel):
    """
    A set of Environments for a type of product.

    For instance, a "browser testing" Profile might be a set of
    environments relevant to testing browsers.

    """
    name = models.CharField(max_length=200)


    def __unicode__(self):
        """Return unicode representation."""
        return self.name


    @classmethod
    def generate(cls, name, *elements, **kwargs):
        """
        Create profile of environments as Cartesian product of given elements.

        Elements are split by category, and then an environment is generated
        for each combination of one element from each category.

        """
        by_category = defaultdict(list)
        for element in elements:
            by_category[element.category].append(element)

        new = cls.objects.create(name=name, **kwargs)

        for element_list in itertools.product(*by_category.values()):
            e = Environment.objects.create(profile=new)
            e.elements.add(*element_list)

        return new


    def clone(self, *args, **kwargs):
        """Clone profile, with environments."""
        kwargs.setdefault("cascade", ["environments"])
        overrides = kwargs.setdefault("overrides", {})
        overrides.setdefault("name", "Cloned: {0}".format(self.name))
        return super(Profile, self).clone(*args, **kwargs)


    def categories(self):
        """Return an iterable of categories that are part of this profile."""
        return Category.objects.filter(
            elements__environments__profile=self).distinct().order_by("name")



class Category(CCModel):
    """
    A category of parallel environment elements.

    For instance, the category "Operating System" could include "Linux", "OS
    X", "Windows"...

    """
    name = models.CharField(max_length=200)


    def __unicode__(self):
        """Return unicode representation."""
        return self.name


    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"


    # @@@ there should be some way to annotate this onto a queryset efficiently
    @property
    def deletable(self):
        """Return True if this category can be deleted, otherwise False."""
        return not Environment.objects.filter(elements__category=self).exists()


    # @@@ this protection should apply to queryset.delete as well
    def delete(self, *args, **kwargs):
        """Delete this category, or raise ProtectedError if its in use."""
        if not self.deletable:
            raise models.ProtectedError(
                "Category '{0}' is in use and cannot be deleted.".format(
                    self.name),
                list(Environment.objects.filter(elements__category=self).all())
                )
        return super(Category, self).delete(*args, **kwargs)



class Element(CCModel):
    """
    An individual environment factor (e.g. "OS X" or "English").

    """
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, related_name="elements")


    def __unicode__(self):
        """Return unicode representation."""
        return self.name


    class Meta:
        ordering = ["name"]


    # @@@ there should be some way to annotate this onto a queryset efficiently
    @property
    def deletable(self):
        """Return True if this element can be deleted, otherwise False."""
        return not self.environments.exists()


    # @@@ this protection should apply to queryset.delete as well
    def delete(self, *args, **kwargs):
        """Delete this element, or raise ProtectedError if its in use."""
        if not self.deletable:
            raise models.ProtectedError(
                "Element '{0}' is in use and cannot be deleted.".format(
                    self.name),
                list(self.environments.all())
                )
        return super(Element, self).delete(*args, **kwargs)



class Environment(CCModel):
    """
    A collection of elements representing a testing environment.

    For instance, an Environment for testing a web application might include
    the elements "Firefox 10", "English", "Windows 7".

    An Environment containing multiple elements from the same category
    (e.g. both "Linux" and "OS X") means that either of those elements matches
    this environment: in other words, the test can be run on either Linux or OS
    X, it doesn't matter for the purposes of this test.

    """
    profile = models.ForeignKey(
        Profile, blank=True, null=True, related_name="environments")

    elements = models.ManyToManyField(Element, related_name="environments")


    def __unicode__(self):
        """Return unicode representation."""
        return u", ".join(unicode(e) for e in self.ordered_elements())


    class Meta:
        permissions = [
            (
                "manage_environments",
                "Can add/edit/delete environments, profiles, etc."
                )
            ]


    def ordered_elements(self):
        """All elements in category name order."""
        return iter(self.elements.order_by("category__name"))


    def clone(self, *args, **kwargs):
        """Clone environment, including element relationships."""
        kwargs.setdefault("cascade", ["elements"])
        return super(Environment, self).clone(*args, **kwargs)


    # @@@ there should be some way to annotate this onto a queryset efficiently
    @property
    def deletable(self):
        """Return True if this environment can be deleted, otherwise False."""
        from cc.model import ProductVersion
        return not ProductVersion.objects.filter(environments=self).exists()


    # @@@ this protection should apply to queryset.delete as well
    def delete(self, *args, **kwargs):
        """Delete this environment, or raise ProtectedError if its in use."""
        if not self.deletable:
            from cc.model import ProductVersion
            raise models.ProtectedError(
                "Environment '{0}' is in use and cannot be deleted.".format(
                    str(self)),
                list(ProductVersion.objects.filter(environments=self).all())
                )
        return super(Environment, self).delete(*args, **kwargs)


    def remove_from_profile(self, user=None):
        """Remove environment from its profile and delete it if not in use."""
        if self.deletable:
            self.delete(user=user)
        else:
            self.profile = None
            self.save(force_update=True, user=user)



class HasEnvironmentsModel(models.Model):
    """
    Base for models that inherit/cascade environments to/from parents/children.

    Subclasses should implement ``parent`` property and ``cascade_envs_to``
    classmethod.

    """
    environments = models.ManyToManyField(Environment, related_name="%(class)s")


    class Meta:
        abstract = True


    def save(self, *args, **kwargs):
        """Save instance; new instances get parent environments."""
        adding = False
        if self.id is None:
            adding = True

        ret = super(HasEnvironmentsModel, self).save(*args, **kwargs)

        if adding and isinstance(self.parent, HasEnvironmentsModel):
            self.environments.add(*self.parent.environments.all())

        return ret


    @property
    def parent(self):
        """
        The model instance to inherit environments from.

        """
        return None


    @classmethod
    def cascade_envs_to(cls, objs, adding):
        """
        Return model instances to cascade env profile changes to.

        Return value should be a dictionary mapping model classes to iterables
        of model instances to cascade to.

        ``objs`` arg is list of objs`` of this class to cascade from;
        ``adding`` arg is True if cascading for an addition of envs to the
        profile, False if cascading a removal.

        """
        return {}


    @classmethod
    def _remove_envs(cls, objs, envs):
        """Remove one or environments from one or more objects of this class."""
        for model, instances in cls.cascade_envs_to(objs, adding=False).items():
            model._remove_envs(instances, envs)
        m2m_reverse_name = cls.environments.field.related_query_name()
        cls.environments.through._base_manager.filter(
            **{
                "{0}__in".format(m2m_reverse_name): objs,
                "environment__in": envs
                }
              ).delete()


    def remove_envs(self, *envs):
        """Remove one or more environments from this object's profile."""
        self._remove_envs([self], envs)


    def add_envs(self, *envs):
        """Add one or more environments to this object's profile."""
        # @@@ optimize this to reduce queries once we have bulk insert in 1.4
        self.environments.add(*envs)
        for model, instances in self.cascade_envs_to(
                [self], adding=True).items():
            for instance in instances:
                instance.add_envs(*envs)
