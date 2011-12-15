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
Admin config for library models.

"""
from django.contrib import admin

from ..core.base_admin import (
    BaseModelAdmin, BaseTabularInline, BaseStackedInline)
from . import models



class CaseVersionInline(BaseStackedInline):
    model = models.CaseVersion
    extra = 0
    fieldsets = [
        (None, {"fields": [("number", "latest", "exists"),
                           "name",
                           "description"]})
        ]


class CaseStepInline(BaseTabularInline):
    model = models.CaseStep
    extra = 0


class CaseVersionAdmin(BaseModelAdmin):
    inlines = [CaseStepInline]
    fieldsets = [
        (None, {"fields": [("number", "latest"),
                           "name",
                           "description"]})
        ]


admin.site.register(models.Suite, BaseModelAdmin)
admin.site.register(models.Case, BaseModelAdmin, inlines=[CaseVersionInline])
admin.site.register(models.CaseVersion, CaseVersionAdmin)
