"""
Admin config for execution models.

"""
from django.contrib import admin

from ..mtadmin import (
    MTModelAdmin, TeamModelAdmin, MTTabularInline, MTStackedInline)
from . import models



class RunCaseVersionInline(MTTabularInline):
    model = models.RunCaseVersion
    extra = 0



class RunSuiteInline(MTTabularInline):
    model = models.RunSuite
    extra = 0



class ResultInline(MTStackedInline):
    model = models.Result
    extra = 0
    fieldsets = [(None, {"fields": [
                    "runcaseversion",
                    ("tester", "environment"),
                    ("status"),
                    "comment",
                    ("review", "reviewed_by"),
                    "exists",
                    ]})]



class StepResultInline(MTTabularInline):
    model = models.StepResult
    extra = 0



class RunAdmin(TeamModelAdmin):
    filter_horizontal = ["environments"]
    fieldsets = [(None, {"fields": [
                    "name",
                    ("productversion", "status"),
                    "description",
                    ("start", "end"),
                    "environments",
                    ]})]
    inlines = [RunSuiteInline, RunCaseVersionInline]



class ResultAdmin(MTModelAdmin):
    fieldsets = [(None, {"fields": [
                    "runcaseversion",
                    ("tester", "environment"),
                    ("status"),
                    "comment",
                    ("review", "reviewed_by"),
                    ]})]
    inlines = [StepResultInline]




admin.site.register(models.Run, RunAdmin)
admin.site.register(
    models.RunCaseVersion, MTModelAdmin, inlines=[ResultInline])
admin.site.register(models.Result, ResultAdmin)
