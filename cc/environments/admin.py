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
Admin config for environment models.

"""
from django.contrib import admin

from ..core.ccadmin import CCModelAdmin, CCTabularInline
from . import models



class ElementInline(CCTabularInline):
    model = models.Element
    extra = 0



# not CCTabularInline because auto-generated through model is not CCModel
class EnvironmentElementInline(admin.TabularInline):
    model = models.Environment.elements.through
    extra = 0



admin.site.register(models.Profile, CCModelAdmin)
admin.site.register(models.Category, CCModelAdmin, inlines=[ElementInline])
admin.site.register(models.Element, CCModelAdmin)
admin.site.register(
    models.Environment, CCModelAdmin,
    inlines=[EnvironmentElementInline], exclude=["elements"])
