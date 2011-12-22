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

from .ccmodel import CCModel



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
