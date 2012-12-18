"""
Models for tags.

"""
from django.db import models

from ..mtmodel import MTModel
from ..core.models import Product



class Tag(MTModel):
    """A tag."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # tags may be product-specific or global (in which case this FK is null)
    product = models.ForeignKey(Product, blank=True, null=True)


    def __unicode__(self):
        """Unicode representation is name."""
        return self.name


    def clone(self, *args, **kwargs):
        """Clone tag; sets name prefix by default."""
        overrides = kwargs.setdefault("overrides", {})
        overrides.setdefault("name", "Cloned: {0}".format(self.name))
        return super(Tag, self).clone(*args, **kwargs)


    class Meta:
        permissions = [("manage_tags", "Can add/edit/delete tags.")]
