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
Admin config for execution models.

"""
from django.contrib import admin

from ..core.ccadmin import (
    CCModelAdmin, TeamModelAdmin, CCTabularInline, CCStackedInline)
from . import models



class RunCaseVersionInline(CCTabularInline):
    model = models.RunCaseVersion
    extra = 0



class RunSuiteInline(CCTabularInline):
    model = models.RunSuite
    extra = 0



class ResultInline(CCStackedInline):
    model = models.Result
    extra = 0
    fieldsets = [(None, {"fields": [
                    "runcaseversion",
                    ("tester", "environment"),
                    ("status", "started", "completed"),
                    "comment",
                    ("review", "reviewed_on", "reviewed_by"),
                    "exists",
                    ]})]



class StepResultInline(CCTabularInline):
    model = models.StepResult
    extra = 0



class RunAdmin(TeamModelAdmin):
    fieldsets = [(None, {"fields": [
                    "name",
                    ("productversion", "status"),
                    "description",
                    ("start", "end"),
                    "environments",
                    ]})]
    inlines = [RunSuiteInline, RunCaseVersionInline]



class ResultAdmin(CCModelAdmin):
    fieldsets = [(None, {"fields": [
                    "runcaseversion",
                    ("tester", "environment"),
                    ("status", "started", "completed"),
                    "comment",
                    ("review", "reviewed_on", "reviewed_by"),
                    ]})]
    inlines = [StepResultInline]




admin.site.register(models.Run, RunAdmin)
admin.site.register(
    models.RunCaseVersion, CCModelAdmin, inlines=[ResultInline])
admin.site.register(models.Result, ResultAdmin)
