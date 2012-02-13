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
Models for tags.

"""
from django.db import models

from ..ccmodel import CCModel
from ..core.models import Product



class Tag(CCModel):
    """A tag."""
    name = models.CharField(max_length=100)

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
