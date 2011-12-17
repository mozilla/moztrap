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
Models for environments.

"""
from django.db import models

from ..core.ccmodel import CCModel



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
        verbose_name_plural = "categories"



class Element(CCModel):
    """
    An individual environment factor (e.g. "OS X" or "English").

    """
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, related_name="elements")


    def __unicode__(self):
        """Return unicode representation."""
        return self.name



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
    profile = models.ForeignKey(Profile, related_name="environments")

    elements = models.ManyToManyField(Element)


    def __unicode__(self):
        """Return unicode representation."""
        return u", ".join(str(e) for e in self.elements.all())
