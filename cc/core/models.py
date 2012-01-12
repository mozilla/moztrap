# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
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
Core Case Conductor models (Product).

"""
from django.db import models

from django.contrib.auth.models import User

from ..environments.models import HasEnvironmentsModel
from .ccmodel import CCModel, TeamModel



class Product(CCModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    team = models.ManyToManyField(User, blank=True)


    def __unicode__(self):
        return self.name


    class Meta:
        permissions = [
            ("manage_products", "Can add/edit/delete products."),
            ("manage_users", "Can add/edit/delete user accounts."),
            ]



class ProductVersion(TeamModel, HasEnvironmentsModel):
    product = models.ForeignKey(Product, related_name="versions")
    version = models.CharField(max_length=100)
    codename = models.CharField(max_length=100)
    order = models.IntegerField(default=0, editable=False)


    def __unicode__(self):
        return "%s %s" % (self.product, self.version)


    class Meta:
        ordering = ["order"]
        unique_together = [("product", "version")]


    @property
    def parent(self):
        return self.product


    def cascade_envs_to(self, adding):
        if adding:
            return {
                self.runs.model: self.runs.filter(
                    status=self.runs.model.STATUS.draft),
                self.caseversions.model: self.caseversions.filter(
                    envs_narrowed=False)
                }
        return {
            self.runs.model: self.runs.all(),
            self.caseversions.model: self.caseversions.all()
            }


    def clone(self, *args, **kwargs):
        """
        Clone ProductVersion, with ".next" version and "Cloned:" codename.

        """
        overrides = kwargs.setdefault("overrides", {})
        overrides["version"] = "%s.next" % self.version
        overrides["codename"] = "Cloned: %s" % self.codename
        return super(ProductVersion, self).clone(*args, **kwargs)
